# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _get_report_base_filename(self):
        self.ensure_one()
        return "{} {}".format(self.picking_type_id.name, self.name)

    origin = fields.Char(states={"done": [("readonly", False)]})
    delegate_id = fields.Many2one("res.partner", string="Delegate")
    mean_transp = fields.Char(string="Mean transport")

    @api.onchange("delegate_id")
    def on_change_delegate_id(self):
        if self.delegate_id:
            self.mean_transp = self.delegate_id.mean_transp

    # metoda locala sau se poate in 10 are alt nume
    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        res = super()._get_invoice_vals(key, inv_type, journal_id, move)
        if inv_type == "out_invoice":
            res["delegate_id"] = move.picking_id.delegate_id.id
            res["mean_transp"] = move.picking_id.mean_transp
        return res

    def do_print_picking(self):
        self.write({"printed": True})
        if self.picking_type_code == "incoming":
            if self.location_dest_id.l10n_ro_merchandise_type == "store":
                res = self.env.ref("l10n_ro_stock_picking_report.action_report_reception_sale_price").report_action(
                    self
                )
            else:
                res = self.env.ref("l10n_ro_stock_picking_report.action_report_reception").report_action(self)

        elif self.picking_type_code == "outgoing":
            res = self.env.ref("l10n_ro_stock_picking_report.action_report_delivery").report_action(self)
        else:
            res = self.env.ref("l10n_ro_stock_picking_report.action_report_internal_transfer").report_action(self)
        return res
