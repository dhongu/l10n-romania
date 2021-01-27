# ©  2008-2018 Fekete Mihai <mihai.fekete@forbiom.eu>
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import _, api, fields, models
from odoo.tools.float_utils import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrderLine, self)._prepare_invoice()
        invoice_vals["stock_location_id"] = self.warehouse_id.lot_stock_id.id
        return invoice_vals

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if self.product_id.invoice_policy == "delivery":
            notice = False
            for picking in self.order_id.picking_ids:
                if picking.notice:
                    notice = True
            if notice:
                res["account_id"] = self.company_id.property_stock_picking_receivable_account_id.id or res["account_id"]

        return res
