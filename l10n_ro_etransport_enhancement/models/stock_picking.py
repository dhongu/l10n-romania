# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from datetime import datetime, time

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class Picking(models.Model):
    _inherit = "stock.picking"

    l10n_ro_edi_stock_required = fields.Boolean(string="eTransport Required")
    l10n_ro_shipping_weights = fields.Boolean(string="Custom Shipping Weights")
    l10n_ro_shipping_weight_lines = fields.One2many(
        "l10n.ro.stock.picking.weight.line", "picking_id", string="Shipping Weight Lines"
    )

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
            # fix bug and get price from move if cost price is 0
            if float_is_zero(item["valoareLeiFaraTva"], precision_rounding=0.01):
                # try to find the move
                product_name = item["denumireMarfa"]
                move = self.env["stock.move"].search(
                    [("product_id.name", "=", product_name), ("picking_id", "in", self.ids)], limit=1
                )
                if move:
                    price_unit = 0.0
                    if move.stock_valuation_layer_ids:
                        quantity = 0.0
                        value = 0.0
                        for svl in move.stock_valuation_layer_ids:
                            quantity += svl.quantity
                            value += svl.value
                        if quantity:
                            price_unit = value / quantity
                        else:
                            price_unit = 0.0
                    if not price_unit:
                        price_unit = move.product_id.standard_price
                    if not price_unit:
                        price_unit = move.product_id.list_price
                    if not price_unit:
                        raise UserError(_("Nu am gasit un pret pentru %s") % move.product_id.display_name)
                    item["valoareLeiFaraTva"] = price_unit
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
                raise UserError(_("UIT lines and moves lines are not the same. Cannot get prices."))
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
                            if self and self.company_id.l10n_ro_etransport_get_validated_qty:
                                item["cantitate"] = move_id.quantity
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
                raise UserError(_("UIT lines and moves lines are not the same. Cannot get prices."))
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
                            if self and self.company_id.l10n_ro_etransport_get_validated_qty:
                                item["cantitate"] = move_id.quantity
                            item["valoareLeiFaraTva"] = round(unit_price * item["cantitate"], 2)
                    item_no += 1
        # remove lines with 0 quantity, it's possible when the validated qty is used
        if self and self.company_id.l10n_ro_etransport_get_validated_qty:
            for item in res["data"]["notificare"]["bunuriTransportate"]:
                if float_is_zero(item["cantitate"], precision_rounding=0.01):
                    res["data"]["notificare"]["bunuriTransportate"].pop(
                        res["data"]["notificare"]["bunuriTransportate"].index(item)
                    )
        return res

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

    @api.model
    def _l10n_ro_edi_stock_validate_data(self, data: dict):
        errors = super()._l10n_ro_edi_stock_validate_data(data)

        no_weight = self.env["product.product"]
        for move in data["stock_move_ids"]:
            if not move.product_id.weight:
                no_weight |= move.product_id
        if no_weight:
            product_name = no_weight.mapped("display_name")
            errors.append(_(f"The following products do not have weight defined:\n{product_name}\n."))
        return errors
