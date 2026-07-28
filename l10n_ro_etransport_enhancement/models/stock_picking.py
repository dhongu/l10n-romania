# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import logging
from datetime import datetime, time

import pytz
import requests

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Operațiunile pentru care traseul rutier poate avea la AMBELE capete un punct de
# trecere a frontierei sau un birou vamal, nu doar o locație.
#
# Nativ (`l10n_ro_edi_stock`), biroul vamal e permis doar la plecare pentru import
# (40) și doar la sosire pentru export (50), iar celălalt capăt rămâne obligatoriu
# o locație. Asta face imposibil de declarat tocmai tronsonul sub supraveghere
# vamală:
#   * import  — din punctul de trecere a frontierei până la biroul vamal de
#               interior unde se face vămuirea (PTF -> birou vamal);
#   * export  — din biroul vamal unde s-a depus declarația de export până la
#               punctul de trecere a frontierei (birou vamal -> PTF).
#
# Schema ANAF (`LocTraseuRutierType` din schema_ETR_v2) acceptă `codPtf` sau
# `codBirouVamal` la oricare dintre `locStartTraseuRutier` / `locFinalTraseuRutier`,
# deci restricția e a implementării Odoo, nu a declarației.
FULL_ROUTE_OPERATION_TYPES = ("40", "50")


class Picking(models.Model):
    _inherit = "stock.picking"

    l10n_ro_edi_stock_required = fields.Boolean(string="eTransport Required")
    l10n_ro_shipping_weights = fields.Boolean(string="Custom Shipping Weights")
    l10n_ro_shipping_weight_lines = fields.One2many(
        "l10n.ro.stock.picking.weight.line", "picking_id", string="Shipping Weight Lines"
    )
    l10n_ro_transport_partner_id = fields.Many2one("res.partner", string="Transport Partner")
    # Documentele însoțitoare declarate la ANAF (CMR, factură, aviz…). Nativ,
    # `l10n_ro_edi_stock` trimite UN SINGUR document, hardcodat ca aviz (tip 30)
    # cu numărul transferului — deci CMR-ul sau numărul real de aviz nu ajungeau
    # în declarație. Schema ANAF acceptă o LISTĂ de `documenteTransport`.
    l10n_ro_etransport_document_ids = fields.One2many(
        "l10n.ro.etransport.document",
        "picking_id",
        string="Documente însoțitoare",
        copy=False,
    )

    def l10n_ro_etransport_add_default_documents(self):
        """Completează documentele însoțitoare cu ce se poate deduce automat:
        avizul (numărul transferului) și facturile emise pe livrarea respectivă.
        Nu duplică rândurile deja existente (potrivire pe tip + număr)."""
        Document = self.env["l10n.ro.etransport.document"]
        for picking in self:
            existing = {(d.document_type, d.name) for d in picking.l10n_ro_etransport_document_ids}
            vals_list = []
            # avizul de însoțire = transferul însuși (tip 30)
            if ("30", picking.name) not in existing:
                vals_list.append(
                    {
                        "picking_id": picking.id,
                        "document_type": "30",
                        "name": picking.name,
                        "date": (picking.scheduled_date or fields.Datetime.now()).date(),
                    }
                )
            # facturile legate de livrare, prin liniile de vânzare (tip 20)
            invoices = picking.move_ids.sale_line_id.invoice_lines.move_id.filtered(
                lambda m: m.state == "posted" and m.move_type in ("out_invoice", "out_refund")
            )
            for invoice in invoices:
                if ("20", invoice.name) not in existing:
                    vals_list.append(
                        {
                            "picking_id": picking.id,
                            "document_type": "20",
                            "name": invoice.name,
                            "date": invoice.invoice_date or invoice.date,
                        }
                    )
            if vals_list:
                Document.create(vals_list)

    @api.onchange("carrier_id")
    def _onchange_carrier_id(self):
        for picking in self:
            if picking.carrier_id and picking.carrier_id.l10n_ro_edi_stock_partner_id:
                picking.l10n_ro_transport_partner_id = picking.carrier_id.l10n_ro_edi_stock_partner_id

    def _compute_l10n_ro_edi_stock_enable(self):
        res = super()._compute_l10n_ro_edi_stock_enable()
        for picking in self:
            picking.l10n_ro_edi_stock_enable = picking.l10n_ro_edi_stock_required
        return res

    @api.depends("l10n_ro_edi_stock_enable", "state", "l10n_ro_edi_stock_state")
    def _compute_l10n_ro_edi_stock_enable_send(self):
        res = super()._compute_l10n_ro_edi_stock_enable_send()
        for picking in self:
            picking.l10n_ro_edi_stock_enable_send = (
                picking.l10n_ro_edi_stock_enable
                and picking.l10n_ro_edi_stock_state in (False, "stock_sending_failed")
                and not picking._l10n_ro_edi_stock_get_last_document("stock_validated")
            )
        return res

    @api.model
    def _l10n_ro_edi_stock_get_available_location_types(self, operation_type, location):
        """Deschide punctul de trecere a frontierei și biroul vamal la ambele capete
        ale traseului, pentru import și export.

        Vezi `FULL_ROUTE_OPERATION_TYPES`: fără asta nu se poate obține UIT pe
        tronsonul PTF -> birou vamal (import) sau birou vamal -> PTF (export).
        Metoda e folosită și de `l10n_ro_edi_stock_batch`, care o apelează pe
        `stock.picking`, deci loturile de transfer moștenesc automat comportamentul.
        """
        if operation_type in FULL_ROUTE_OPERATION_TYPES:
            return "location,bcp,customs"
        return super()._l10n_ro_edi_stock_get_available_location_types(operation_type, location)

    @api.model
    def _l10n_ro_edi_stock_get_template_data(self, data: dict):
        for move in self.move_ids:
            move._cal_move_weight()
        res = super()._l10n_ro_edi_stock_get_template_data(data)
        for key in ("locStartTraseuRutier", "locFinalTraseuRutier"):
            locatie = res["data"]["notificare"][key].get("locatie", {})
            if locatie and not locatie["alteInfo"]:
                locatie["alteInfo"] = "-"
        transport_partner = data["transport_partner_id"]
        if transport_partner.country_code == "GR":
            res["data"]["notificare"]["dateTransport"]["codTaraOrgTransport"] = "EL"
        if res["data"]["notificare"]["partenerComercial"]["codTara"] == "GR":
            res["data"]["notificare"]["partenerComercial"]["codTara"] = "EL"

        # fix data
        user_tz = self.env.user.tz or self.env.context.get("tz")
        if self:
            scheduled_date_tz = pytz.utc.localize(self.scheduled_date or fields.Date.today()).astimezone(
                pytz.timezone(user_tz)
            )
            res["data"]["notificare"]["dateTransport"]["dataTransport"] = scheduled_date_tz.date()
        else:
            dt = datetime.combine(res["data"]["notificare"]["dateTransport"]["dataTransport"], time.min)
            scheduled_date_tz = pytz.utc.localize(dt).astimezone(pytz.timezone(user_tz))
            res["data"]["notificare"]["dateTransport"]["dataTransport"] = scheduled_date_tz.date()
        today = fields.Date.today()
        if res["data"]["notificare"]["dateTransport"]["dataTransport"] < today:
            res["data"]["notificare"]["dateTransport"]["dataTransport"] = today

        for item in res["data"]["notificare"]["bunuriTransportate"]:
            # fix bug
            item["valoareLeiFaraTva"] = round(item["valoareLeiFaraTva"] * item["cantitate"], 2)
            # fix rounding - ex. 0.470000000000003
            item["greutateNeta"] = round(item["greutateNeta"], 2)
            item["greutateBruta"] = round(item["greutateBruta"], 2)

        # get prices if configured in settings
        def _get_unit_price_for_uit(move):
            direction = move.picking_code
            if direction == "incoming" and move.purchase_line_id:
                price = (
                    move.purchase_line_id.price_subtotal / move.purchase_line_id.product_qty
                    if move.purchase_line_id.product_qty
                    else 0.00
                )
                if move.purchase_line_id.currency_id != move.picking_id.company_id.currency_id:
                    price = move.purchase_line_id.currency_id._convert(
                        price,
                        move.picking_id.company_id.currency_id,
                        move.picking_id.company_id,
                        move.picking_id.scheduled_date,
                    )
                return price
            elif direction == "outgoing" and move.sale_line_id:
                price = move.sale_line_id.price_reduce_taxexcl
                if move.sale_line_id.currency_id != move.picking_id.company_id.currency_id:
                    price = move.sale_line_id.currency_id._convert(
                        price,
                        move.picking_id.company_id.currency_id,
                        move.picking_id.company_id,
                        move.picking_id.scheduled_date,
                    )
                return price
            return 0.00

        if self and self.company_id.l10n_ro_etransport_get_order_value:
            if len(data["stock_move_ids"]) != len(res["data"]["notificare"]["bunuriTransportate"]):
                raise UserError(self.env._("UIT lines and moves lines are not the same. Cannot get prices."))
            else:
                item_no = 0
                for item in res["data"]["notificare"]["bunuriTransportate"]:
                    try:
                        move_id = data["stock_move_ids"][item_no]
                    except IndexError:
                        move_id = False
                    if move_id:
                        unit_price = _get_unit_price_for_uit(move_id)
                        if unit_price:
                            item["valoareLeiFaraTva"] = round(unit_price * item["cantitate"], 2)
                        if self.l10n_ro_shipping_weights:
                            weight_line = self.l10n_ro_shipping_weight_lines.filtered(
                                lambda x, move_id=move_id: x.move_id == move_id
                            )
                            if weight_line:
                                item["greutateNeta"] = round(weight_line.net_weight, 2)
                                item["greutateBruta"] = round(weight_line.gross_weight, 2)
                    item_no += 1
        if (
            not self
            and "company_id" in data
            and data["company_id"]
            and data["company_id"].l10n_ro_etransport_get_order_value
        ):  # called from batch
            if len(data["stock_move_ids"]) != len(res["data"]["notificare"]["bunuriTransportate"]):
                raise UserError(self.env._("UIT lines and moves lines are not the same. Cannot get prices."))
            else:
                item_no = 0
                for item in res["data"]["notificare"]["bunuriTransportate"]:
                    try:
                        move_id = data["stock_move_ids"][item_no]
                    except IndexError:
                        move_id = False
                    if move_id:
                        unit_price = _get_unit_price_for_uit(move_id)
                        if unit_price:
                            item["valoareLeiFaraTva"] = round(unit_price * item["cantitate"], 2)
                    item_no += 1

        # Documentele însoțitoare declarate pe transfer (CMR, factură, aviz…).
        # Nativ, `documenteTransport` e un DICT cu un singur document hardcodat
        # (tip 30 = aviz, numărul transferului); schema ANAF acceptă o listă.
        # Trecem cheia pe LISTĂ: dacă operatorul a declarat documente, le trimitem
        # pe toate; dacă nu, păstrăm documentul nativ (compatibilitate).
        native_doc = res["data"]["notificare"].get("documenteTransport")
        docs = self.l10n_ro_etransport_document_ids if self else self.browse()
        if docs:
            res["data"]["notificare"]["documenteTransport"] = [
                {
                    "tipDocument": doc.document_type,
                    "dataDocument": doc.date,
                    "numarDocument": doc.name,
                    "observatii": doc.remarks or "",
                }
                for doc in docs
            ]
        elif isinstance(native_doc, dict):
            res["data"]["notificare"]["documenteTransport"] = [native_doc]
        return res

    def _l10n_ro_edi_stock_send_etransport_document(self, send_type: str):
        """Tratează căderile de rețea către ANAF fără să arunce traceback în interfață.

        Standardul nu prinde excepțiile requests, deci un timeout urcă până la RPC
        și anulează tranzacția: nu rămâne nicio urmă pe livrare, deși ANAF poate să
        fi înregistrat deja notificarea.
        """
        self.ensure_one()
        try:
            return super()._l10n_ro_edi_stock_send_etransport_document(send_type=send_type)
        except requests.exceptions.RequestException as error:
            _logger.warning("eTransport: ANAF request failed for %s: %s", self.name, error)
            document_values = {"message": self._l10n_ro_etransport_network_error_message(error)}

            if send_type == "amend":
                last_sent_document = self._l10n_ro_edi_stock_get_last_document("stock_validated")
                document_values |= {
                    "l10n_ro_edi_stock_load_id": last_sent_document.l10n_ro_edi_stock_load_id,
                    "l10n_ro_edi_stock_uit": last_sent_document.l10n_ro_edi_stock_uit,
                }

            self._l10n_ro_edi_stock_create_document_stock_sending_failed(document_values)

    def _l10n_ro_etransport_network_error_message(self, error):
        self.ensure_one()
        return self.env._(
            "ANAF did not answer the eTransport request: %(error)s\n\n"
            "IMPORTANT: the notification may have reached ANAF anyway, only the answer was lost. "
            "Before sending again, check in SPV whether a UIT was already issued for this transfer, "
            "otherwise you may end up with two UITs for the same goods.",
            error=error,
        )

    # pylint: disable=missing-return
    def _l10n_ro_edi_stock_fetch_document_status(self):
        """Interoghează starea picking cu picking, ca o cădere de rețea să nu oprească restul lotului.

        Standardul nu întoarce nimic din această metodă, deci nu avem ce propaga.
        """
        for picking in self:
            try:
                super(Picking, picking)._l10n_ro_edi_stock_fetch_document_status()
            except requests.exceptions.RequestException as error:
                # Starea rămâne 'stock_sent', deci următoarea interogare reia livrarea.
                _logger.warning("eTransport: status fetch failed for %s: %s", picking.name, error)
                picking._message_log(
                    body=self.env._(
                        "ANAF did not answer the eTransport status request: %(error)s\n"
                        "The status will be checked again later.",
                        error=error,
                    )
                )

    def action_l10n_ro_edi_stock_fetch_status(self):
        res = super().action_l10n_ro_edi_stock_fetch_status()
        for picking in self:
            if picking.l10n_ro_edi_stock_state == "stock_validated":
                picking.carrier_tracking_ref = picking.l10n_ro_edi_stock_document_uit

        return res

    def l10n_ro_compute_weight_lines(self):
        for picking in self:
            vals = []
            for move in picking.move_ids:
                if move.quantity > 0:
                    vals.append(
                        {
                            "picking_id": picking.id,
                            "move_id": move.id,
                            "net_weight": move.product_id.l10n_ro_net_weight * move.quantity,
                            "gross_weight": move.product_id.weight * move.quantity,
                            "weight_uom_id": self.env["product.template"]
                            ._get_weight_uom_id_from_ir_config_parameter()
                            .id,
                        }
                    )
            picking.l10n_ro_shipping_weight_lines.create(vals)

    # @api.model
    # def _l10n_ro_edi_stock_validate_data(self, data: dict):
    #     errors = super()._l10n_ro_edi_stock_validate_data(data)
    #
    #     for error in errors:
    #         if error == _("The delivery carrier partner has to be located in Romania."):
    #             errors.remove(error)
    #
    #     return errors

    def _l10n_ro_edi_stock_validate_carrier(self):
        pickings_without_transport_partner = self.filtered(
            lambda p: p._l10n_ro_edi_stock_validate_carrier_filter(p) and not p.l10n_ro_transport_partner_id
        )

        # Pentru pickings fără l10n_ro_transport_partner_id, apelăm super() care verifică carrier_id
        if pickings_without_transport_partner:
            return super(Picking, pickings_without_transport_partner)._l10n_ro_edi_stock_validate_carrier()

    @api.model
    def _l10n_ro_edi_stock_validate_data(self, data: dict):
        data["transport_partner_id"] = self.l10n_ro_transport_partner_id or data.get("transport_partner_id")
        if not self or not data.get("transport_partner_id"):  # called from batch there's no self
            # try to get the batch itself:
            if data["stock_move_ids"]:
                first_move = data["stock_move_ids"][0]
                batch_id = first_move.picking_id.batch_id
                if batch_id:
                    data["transport_partner_id"] = batch_id.l10n_ro_transport_partner_id
        errors = super()._l10n_ro_edi_stock_validate_data(data)

        no_weight = self.env["product.product"]
        for move in data["stock_move_ids"]:
            if not move.product_id.weight:
                no_weight |= move.product_id
        if no_weight:
            product_name = no_weight.mapped("display_name")
            errors.append(
                self.env._(
                    "The following products do not have weight defined:\n%(product_name)s\n.",
                    product_name=", ".join(product_name),
                )
            )
        return errors
