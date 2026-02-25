# ©  2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import _, api, fields, models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    l10n_ro_edi_stock_required = fields.Boolean(string="eTransport Required")
    l10n_ro_edi_carrier_id = fields.Many2one(
        "delivery.carrier",
        string="Delivery",
        compute="_compute_l10n_ro_edi_carrier_id",
        inverse="_inverse_l10n_ro_edi_carrier_id",
    )
    carrier_tracking_ref = fields.Char(string="Tracking Reference", copy=False)
    l10n_ro_shipping_weights = fields.Boolean(string="Custom Shipping Weights")
    l10n_ro_shipping_weight_lines = fields.One2many(
        "l10n.ro.stock.picking.weight.line", "batch_id", string="Shipping Weight Lines"
    )
    total_net_weight = fields.Float()
    total_gross_weight = fields.Float()

    def _compute_l10n_ro_edi_carrier_id(self):
        for batch in self:
            if self.picking_ids:
                first_carrier = self.picking_ids[0].carrier_id
                batch.l10n_ro_edi_carrier_id = first_carrier

    def _inverse_l10n_ro_edi_carrier_id(self):
        for batch in self:
            for picking in batch.picking_ids:
                picking.carrier_id = batch.l10n_ro_edi_carrier_id

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
        return res

    def action_l10n_ro_edi_stock_fetch_status(self):
        res = super().action_l10n_ro_edi_stock_fetch_status()
        for picking in self:
            if picking.l10n_ro_edi_stock_state == "stock_validated":
                picking.carrier_tracking_ref = picking.l10n_ro_edi_stock_document_uit

        return res

    @api.model
    def _l10n_ro_edi_stock_validate_data(self, data: dict):
        errors = super()._l10n_ro_edi_stock_validate_data(data)

        for error in errors:
            if error == _("The delivery carrier partner has to be located in Romania."):
                errors.remove(error)

        return errors

    def l10n_ro_compute_weight_lines(self):
        self.picking_ids.l10n_ro_compute_weight_lines()

    def l10n_ro_distribute_weights(self):
        from odoo.exceptions import UserError
        from odoo.tools import float_is_zero

        for batch in self:
            if not batch.l10n_ro_shipping_weight_lines:
                continue
            if float_is_zero(batch.total_net_weight, precision_digits=4) or float_is_zero(
                batch.total_gross_weight, precision_digits=4
            ):
                raise UserError(_("Total net and gross weights must be greater than 0."))

            current_net_total = sum(batch.l10n_ro_shipping_weight_lines.mapped("net_weight"))
            current_gross_total = sum(batch.l10n_ro_shipping_weight_lines.mapped("gross_weight"))
            net_diff = batch.total_net_weight - current_net_total
            gross_diff = batch.total_gross_weight - current_gross_total

            if not float_is_zero(net_diff, precision_digits=4) or not float_is_zero(gross_diff, precision_digits=4):
                for line in batch.l10n_ro_shipping_weight_lines:
                    if not float_is_zero(current_net_total, precision_digits=4):
                        line.net_weight += net_diff * (line.net_weight / current_net_total)
                    else:
                        line.net_weight = batch.total_net_weight / len(batch.l10n_ro_shipping_weight_lines)

                    if not float_is_zero(current_gross_total, precision_digits=4):
                        line.gross_weight += gross_diff * (line.gross_weight / current_gross_total)
                    else:
                        line.gross_weight = batch.total_gross_weight / len(batch.l10n_ro_shipping_weight_lines)


class StockPickingWeightLine(models.Model):
    _inherit = "l10n.ro.stock.picking.weight.line"

    batch_id = fields.Many2one("stock.picking.batch", index=True)

    @api.onchange("picking_id")
    def _onchange_picking_id(self):
        self.batch_id = self.picking_id.batch_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("batch_id") and vals.get("picking_id"):
                picking = self.env["stock.picking"].browse(
                    vals["picking_id"] if isinstance(vals["picking_id"], int) else vals["picking_id"][0]
                )
                vals["batch_id"] = picking.batch_id.id
        return super().create(vals_list)
