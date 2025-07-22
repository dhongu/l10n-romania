# ©  2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Picking(models.Model):
    _inherit = "stock.picking"

    l10n_ro_edi_stock_required = fields.Boolean(string="eTransport Required")
    l10n_ro_edi_stock_check_purchase = fields.Boolean(string="Check Purchase Price for eTransport")

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
        if self.l10n_ro_edi_stock_check_purchase and len(data["stock_move_ids"]) != len(
            res["data"]["notificare"]["bunuriTransportate"]
        ):
            raise UserError(_("eTransport items and move lines do not match. Uncheck Check Purchase Price option"))
        item_no = 0
        for item in res["data"]["notificare"]["bunuriTransportate"]:
            # fix bug
            item["valoareLeiFaraTva"] = round(item["valoareLeiFaraTva"] * item["cantitate"], 2)
            if self.l10n_ro_edi_stock_check_purchase:
                # try to get price from purchase order, assuming the moves are in the same order as the items
                try:
                    move_id = data["stock_move_ids"][item_no]
                except IndexError:
                    move_id = False
                if move_id and move_id.purchase_line_id:
                    unit_price = move_id.purchase_line_id.price_unit
                    currency_id = move_id.purchase_line_id.currency_id
                    to_currency = move_id.picking_id.company_id.currency_id
                    if currency_id != to_currency:
                        unit_price = currency_id._convert(
                            unit_price, to_currency, move_id.picking_id.company_id, move_id.date
                        )
                    item["valoareLeiFaraTva"] = round(unit_price * item["cantitate"], 2)

            # fix rounding - ex. 0.470000000000003
            item["greutateNeta"] = round(item["greutateNeta"], 2)
            item["greutateBruta"] = round(item["greutateBruta"], 2)
            item_no += 1

        return res

    def action_l10n_ro_edi_stock_fetch_status(self):
        res = super().action_l10n_ro_edi_stock_fetch_status()
        for picking in self:
            if picking.l10n_ro_edi_stock_state == "stock_validated":
                picking.carrier_tracking_ref = picking.l10n_ro_edi_stock_document_uit

        return res

    # @api.model
    # def _l10n_ro_edi_stock_validate_data(self, data: dict):
    #     errors = super()._l10n_ro_edi_stock_validate_data(data)
    #
    #     for error in errors:
    #         if error == _("The delivery carrier partner has to be located in Romania."):
    #             errors.remove(error)
    #
    #     return errors
