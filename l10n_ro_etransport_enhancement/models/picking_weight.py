# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models


class StockPickingWeightLine(models.Model):
    _name = "l10n.ro.stock.picking.weight.line"
    _description = "Stock Picking Weight Line"

    picking_id = fields.Many2one("stock.picking")
    move_id = fields.Many2one("stock.move")
    net_weight = fields.Float()
    gross_weight = fields.Float()
    weight_uom_id = fields.Many2one("uom.uom", string="Weight Unit of Measure")

    @api.onchange("move_id")
    def onchange_move_id(self):
        move = self.move_id
        # vezi `stock_picking.l10n_ro_compute_weight_lines`: `move.quantity` e
        # în `move.product_uom`, care poate diferi de UoM-ul de bază al
        # produsului (ex. cutie/palet) — se convertește înainte de înmulțirea
        # cu greutățile per unitate de bază.
        qty_base = move.product_uom._compute_quantity(move.quantity, move.product_id.uom_id, raise_if_failure=False)
        self.net_weight = move.product_id.l10n_ro_net_weight * qty_base
        self.gross_weight = move.product_id.weight * qty_base
        self.weight_uom_id = self.env["product.template"]._get_weight_uom_id_from_ir_config_parameter()
