# ©  2015-2018 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import models


class PosOrder(models.Model):
    _inherit = "pos.order"

    def button_dummy(self):
        return True

    def _prepare_invoice(self):
        res = super(PosOrder, self)._prepare_invoice()
        res["reference"] = self.pos_reference
        res["pos_ref"] = self.pos_reference
        return res

    def action_pos_order_invoice(self):
        return super(
            PosOrder, self.with_context(allowed_change_product=True)
        ).action_pos_order_invoice()


# class PosOrderLine(models.Model):
# _inherit = "pos.order.line"
#
# tax_ids = fields.Many2many("account.tax", string="Taxes", readonly=False)
#
# # fix bug (oare care era problema ?)
# @api.onchange("product_id")
# def _onchange_product_id(self):
#     if self.product_id:
#         tax_ids = self.product_id.taxes_id.filtered(
#             lambda r: not self.company_id or r.company_id == self.company_id
#         )
#         fpos = self.order_id.fiscal_position_id
#         self.tax_ids_after_fiscal_position = (
#             fpos.map_tax(tax_ids, self.product_id, self.order_id.partner_id)
#             if fpos
#             else tax_ids
#         )
#     return super(PosOrderLine, self)._onchange_product_id()
