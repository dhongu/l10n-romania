# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models


class StockPickingWeightLine(models.Model):
    _name = "l10n.ro.stock.picking.weight.line"

    picking_id = fields.Many2one("stock.picking")
    move_id = fields.Many2one("stock.move")
    net_weight = fields.Float()
    gross_weight = fields.Float()
    weight_uom_id = fields.Many2one("uom.uom", string="Weight Unit of Measure")

    @api.onchange("move_id")
    def onchange_move_id(self):
        self.net_weight = self.move_id.product_id.l10n_ro_net_weight * self.move_id.quantity
        self.gross_weight = self.move_id.product_id.weight * self.move_id.quantity
        self.weight_uom_id = self.env["product.template"]._get_weight_uom_id_from_ir_config_parameter()
