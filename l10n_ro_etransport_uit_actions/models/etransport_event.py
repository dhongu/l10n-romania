# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import base64
import logging

import markupsafe
import requests

from odoo import api, fields, models
from odoo.exceptions import UserError

from .etransport_api_actions import ETransportActionsAPI

_logger = logging.getLogger(__name__)

# Codurile de eveniment ANAF care se trimit DUPĂ obținerea unui UIT.
# NOT (notificare) și COR (corecție) rămân în modulul standard.
EVENT_TYPES = [
    ("DEL", "Deletion"),
    ("CON", "Confirmation"),
    ("MVH", "Vehicle Modification"),
]

CONFIRMATION_TYPES = [
    ("10", "Confirmed"),
    ("20", "Partially confirmed"),
    ("30", "Refused"),
]

EVENT_TEMPLATES = {
    "DEL": "l10n_ro_etransport_uit_actions.template_etransport_stergere",
    "CON": "l10n_ro_etransport_uit_actions.template_etransport_confirmare",
    "MVH": "l10n_ro_etransport_uit_actions.template_etransport_modif_vehicul",
}


class EtransportEvent(models.Model):
    """Un eveniment trimis la ANAF pentru un UIT existent, cu ciclul lui de stare.

    Model SEPARAT de `l10n_ro_edi.document`, deliberat: standardul derivă
    `stock.picking.l10n_ro_edi_stock_state` din „documentul curent” și șterge
    documentele în `stock_sent` / `stock_sending_failed` la fiecare interogare
    de stare. Un eveniment scris în tabela aceea ar schimba starea notificării
    (și gardul din `l10n_ro_etransport_block`) și ar putea fi șters de fluxul
    de status al notificării.
    """

    _name = "l10n.ro.etransport.event"
    _description = "eTransport UIT Event"
    _order = "create_date desc, id desc"
    _check_company_auto = True

    picking_id = fields.Many2one(
        "stock.picking", string="Transfer", required=True, ondelete="cascade", index=True, check_company=True
    )
    # compute (nu related) ca modulul de loturi să poată lua compania de pe lot
    company_id = fields.Many2one("res.company", compute="_compute_company_id", store=True)
    event_type = fields.Selection(EVENT_TYPES, string="Event", required=True, readonly=True)
    uit = fields.Char(string="UIT", required=True, readonly=True, size=16)
    state = fields.Selection(
        [
            ("sent", "Sent"),
            ("validated", "Validated"),
            ("failed", "Error"),
        ],
        default="sent",
        required=True,
        readonly=True,
        copy=False,
    )
    load_id = fields.Char(string="ANAF Load Index", readonly=True, copy=False)
    message = fields.Text(string="Message", readonly=True, copy=False)
    attachment = fields.Binary(string="XML", readonly=True, copy=False, attachment=True)
    remarks = fields.Char(string="Remarks", size=200, readonly=True)
    post_outage = fields.Boolean(
        string="Post-outage declaration",
        readonly=True,
        help="Declaration filed after an ANAF system outage (OUG 41/2022 art. 8 par. 1^3).",
    )
    # CON
    confirmation_type = fields.Selection(CONFIRMATION_TYPES, string="Confirmation", readonly=True)
    # MVH
    vehicle_number = fields.Char(string="Vehicle Number", size=20, readonly=True)
    trailer_1_number = fields.Char(string="Trailer 1 Number", size=20, readonly=True)
    trailer_2_number = fields.Char(string="Trailer 2 Number", size=20, readonly=True)
    modification_date = fields.Datetime(string="Modification Date", readonly=True)

    @api.depends("picking_id.company_id")
    def _compute_company_id(self):
        for event in self:
            event.company_id = event._get_parent().company_id

    def _get_parent(self):
        """Înregistrarea căreia îi aparține UIT-ul: transferul aici, lotul în
        `l10n_ro_etransport_uit_actions_batch`. Tot ce ține de nume, companie,
        chatter și plăcuțe trece prin ea, ca lotul să nu dubleze logica."""
        self.ensure_one()
        return self.picking_id

    @api.depends("event_type", "uit")
    def _compute_display_name(self):
        types = dict(self._fields["event_type"]._description_selection(self.env))
        for event in self:
            event.display_name = f"{types.get(event.event_type, '')} {event.uit or ''}".strip()

    # ------------------------------------------------------------------
    # Randare și trimitere
    # ------------------------------------------------------------------

    def _get_template_data(self):
        """Datele pentru șablonul QWeb al evenimentului.

        Atributele opționale trebuie să ajungă `False`/`None` când lipsesc, nu
        string gol: `observatii` e `Str200` cu minLength=1 în XSD, iar QWeb randează
        un string gol ca atribut prezent-dar-vid, pe care ANAF îl respinge.
        """
        self.ensure_one()
        parent = self._get_parent()
        company = parent.company_id
        data = {
            "codDeclarant": (company.vat or "").upper().replace("RO", ""),
            # `refDeclarant` e limitat la 50 de caractere în XSD
            "refDeclarant": (parent.name or "")[:50] or None,
            "declPostAvarie": "D" if self.post_outage else None,
            "uit": self.uit,
            "observatii": (self.remarks or "").strip()[:200] or None,
        }
        if self.event_type == "CON":
            data["tipConfirmare"] = self.confirmation_type
        elif self.event_type == "MVH":
            data.update(
                {
                    "nrVehicul": (self.vehicle_number or "").upper(),
                    "nrRemorca1": (self.trailer_1_number or "").upper() or None,
                    "nrRemorca2": (self.trailer_2_number or "").upper() or None,
                    "dataModificare": self.modification_date.strftime("%Y-%m-%dT%H:%M:%S"),
                }
            )
        return data

    def _render_xml(self):
        self.ensure_one()
        return markupsafe.Markup("<?xml version='1.0' encoding='UTF-8'?>\n") + self.env["ir.qweb"]._render(
            EVENT_TEMPLATES[self.event_type], values={"data": self._get_template_data()}
        )

    def _send(self):
        """Încarcă evenimentul la ANAF și îl lasă în `sent`.

        Răspunsul de la upload conține doar `index_incarcare`; validarea vine
        din `_fetch_status`. Erorile sincrone (schemă, token) marchează `failed`.
        """
        for event in self:
            raw_xml = event._render_xml()
            event.attachment = base64.b64encode(raw_xml.encode("utf-8"))
            try:
                result = ETransportActionsAPI().upload_action(company_id=event.company_id, data=raw_xml)
            except requests.exceptions.RequestException as error:
                _logger.warning("eTransport: ANAF %s upload failed for %s: %s", event.event_type, event.uit, error)
                result = {
                    "error": self.env._(
                        "ANAF did not answer the request: %(error)s\n"
                        "The event may have reached ANAF anyway. Check in SPV before sending it again.",
                        error=error,
                    )
                }
            if "error" in result:
                event.write({"state": "failed", "message": result["error"]})
                event._log_on_picking(self.env._("eTransport %(event)s was rejected: %(message)s"))
                continue
            event.write({"state": "sent", "load_id": result["content"]["index_incarcare"], "message": False})
            event._log_on_picking(
                self.env._("eTransport %(event)s was sent to the authority (load index %(load_id)s)."),
                attach=True,
            )

    # ------------------------------------------------------------------
    # Interogarea stării
    # ------------------------------------------------------------------

    def action_fetch_status(self):
        self._fetch_status()

    @api.model
    def _cron_fetch_status(self):
        self.search([("state", "=", "sent"), ("load_id", "!=", False)])._fetch_status()

    def _fetch_status(self):
        """Ia starea fiecărui eveniment `sent` cu `stareMesaj/{load_id}`.

        Interogăm eveniment cu eveniment, ca o cădere de rețea să nu oprească
        restul lotului: evenimentul rămâne `sent` și e reluat de cron.
        """
        session = requests.Session()
        for event in self.filtered(lambda e: e.state == "sent" and e.load_id):
            try:
                result = ETransportActionsAPI().get_status(
                    company_id=event.company_id, document_load_id=event.load_id, session=session
                )
            except requests.exceptions.RequestException as error:
                _logger.warning("eTransport: status fetch failed for %s %s: %s", event.event_type, event.uit, error)
                continue
            if "error" in result:
                event.write({"state": "failed", "message": result["error"]})
                event._log_on_picking(self.env._("eTransport %(event)s was rejected: %(message)s"))
                continue
            match state := result["content"]["stare"]:
                case "ok":
                    event.write({"state": "validated", "message": False})
                    event._on_validated()
                    event._log_on_picking(self.env._("eTransport %(event)s was validated by the authority."))
                case "in prelucrare":
                    pass
                case "XML cu erori nepreluat de sistem":
                    event.write({"state": "failed", "message": self.env._("XML contains errors.")})
                    event._log_on_picking(self.env._("eTransport %(event)s was rejected: %(message)s"))
                case _:
                    event._log_on_picking(
                        self.env._("Unhandled eTransport state for %(event)s: %(message)s"), message=state
                    )

    def _on_validated(self):
        """Efectele pe transfer ale unui eveniment acceptat de ANAF.

        Se aplică DOAR după validare — după upload ANAF încă poate refuza, iar
        transferul nu trebuie să arate un vehicul sau o stare pe care SPV nu le are.
        """
        for event in self:
            if event.event_type == "MVH":
                event._get_parent().write(
                    {
                        "l10n_ro_edi_stock_vehicle_number": event.vehicle_number,
                        "l10n_ro_edi_stock_trailer_1_number": event.trailer_1_number or False,
                        "l10n_ro_edi_stock_trailer_2_number": event.trailer_2_number or False,
                    }
                )

    def _log_on_picking(self, body_template, attach=False, **extra):
        self.ensure_one()
        types = dict(self._fields["event_type"]._description_selection(self.env))
        values = {
            "event": f"{types[self.event_type]} (UIT {self.uit})",
            "load_id": self.load_id or "",
            "message": extra.get("message", self.message or ""),
        }
        parent = self._get_parent()
        attachment_ids = []
        if attach and self.attachment:
            attachment_ids = (
                self.env["ir.attachment"]
                .create(
                    {
                        "name": f"etransport_{self.event_type}_{self.uit}.xml",
                        "type": "binary",
                        "datas": self.attachment,
                        "res_model": parent._name,
                        "res_id": parent.id,
                    }
                )
                .ids
            )
        parent._message_log(body=body_template % values, attachment_ids=attachment_ids)

    @api.ondelete(at_uninstall=False)
    def _unlink_only_failed(self):
        if any(event.state != "failed" for event in self):
            raise UserError(self.env._("Only events rejected by ANAF can be deleted; the others are an audit trail."))
