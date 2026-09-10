# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models
from odoo.exceptions import UserError

from ..models.etransport_event import CONFIRMATION_TYPES, EVENT_TYPES


class EtransportActionWizard(models.TransientModel):
    """Pregătește și trimite un eveniment (DEL / CON / MVH) pentru UIT-ul curent."""

    _name = "l10n.ro.etransport.action.wizard"
    _description = "eTransport UIT Action"

    picking_id = fields.Many2one("stock.picking", string="Transfer", required=True, readonly=True)
    event_type = fields.Selection(EVENT_TYPES, string="Action", required=True, default="DEL")
    uit = fields.Char(string="UIT", compute="_compute_uit", readonly=True)
    remarks = fields.Char(string="Remarks", size=200)
    post_outage = fields.Boolean(
        string="Post-outage declaration",
        help="Tick when the event is filed after an ANAF system outage (OUG 41/2022 art. 8 par. 1^3).",
    )
    # CON
    confirmation_type = fields.Selection(CONFIRMATION_TYPES, string="Confirmation")
    # MVH
    vehicle_number = fields.Char(string="Vehicle Number", size=20)
    trailer_1_number = fields.Char(string="Trailer 1 Number", size=20)
    trailer_2_number = fields.Char(string="Trailer 2 Number", size=20)
    modification_date = fields.Datetime(string="Modification Date", default=fields.Datetime.now)

    def _get_parent(self):
        """Transferul aici; lotul în modulul de loturi. Aceleași câmpuri
        `l10n_ro_edi_stock_*` există pe amândouă."""
        self.ensure_one()
        return self.picking_id

    def _get_event_values(self):
        self.ensure_one()
        return {"picking_id": self.picking_id.id}

    @api.depends("picking_id")
    def _compute_uit(self):
        for wizard in self:
            wizard.uit = wizard._get_parent().l10n_ro_edi_stock_document_uit

    @api.onchange("picking_id", "event_type")
    def _onchange_vehicle_defaults(self):
        parent = self._get_parent()
        if self.event_type == "MVH" and parent and not self.vehicle_number:
            self.vehicle_number = parent.l10n_ro_edi_stock_vehicle_number
            self.trailer_1_number = parent.l10n_ro_edi_stock_trailer_1_number
            self.trailer_2_number = parent.l10n_ro_edi_stock_trailer_2_number

    def _validate(self):
        self.ensure_one()
        parent = self._get_parent()
        errors = []
        if not self.uit:
            errors.append(self.env._("The transfer has no validated UIT."))
        if not parent.l10n_ro_etransport_enable_actions:
            errors.append(
                self.env._("The UIT is not in a state that accepts actions (deleted, or another event is pending).")
            )
        if self.event_type == "CON" and not self.confirmation_type:
            errors.append(self.env._("Choose the confirmation type."))
        if self.event_type == "MVH":
            if not self.vehicle_number:
                errors.append(self.env._("The new vehicle number is required."))
            if not self.modification_date:
                errors.append(self.env._("The modification date is required."))
            # aceeași regulă ca la notificare: plăcuțele completate trebuie să fie distincte
            plates = [p.upper() for p in (self.vehicle_number, self.trailer_1_number, self.trailer_2_number) if p]
            if len(plates) != len(set(plates)):
                errors.append(self.env._("Vehicle number and trailer number fields must be unique."))
            current = (parent.l10n_ro_edi_stock_vehicle_number or "").upper()
            if plates and plates[0] == current and not (self.trailer_1_number or self.trailer_2_number):
                errors.append(self.env._("The vehicle number is the same as the one already declared."))
        if errors:
            raise UserError("\n".join(errors))

    def action_send(self):
        self.ensure_one()
        self._validate()
        event = self.env["l10n.ro.etransport.event"].create(
            {
                **self._get_event_values(),
                "event_type": self.event_type,
                "uit": self.uit,
                "remarks": self.remarks,
                "post_outage": self.post_outage,
                "confirmation_type": self.confirmation_type if self.event_type == "CON" else False,
                "vehicle_number": self.vehicle_number if self.event_type == "MVH" else False,
                "trailer_1_number": self.trailer_1_number if self.event_type == "MVH" else False,
                "trailer_2_number": self.trailer_2_number if self.event_type == "MVH" else False,
                "modification_date": self.modification_date if self.event_type == "MVH" else False,
            }
        )
        event._send()
        if event.state == "failed":
            # NU ridicăm UserError: ar anula tranzacția și ar pierde evenimentul
            # respins și mesajul din chatter — exact urma de care e nevoie ca să
            # știi ce a refuzat ANAF. Afișăm eroarea ca notificare și lăsăm
            # evenimentul `failed` în tabelul de pe transfer.
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": self.env._("eTransport event rejected"),
                    "message": event.message,
                    "type": "danger",
                    "sticky": True,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
        return {"type": "ir.actions.act_window_close"}
