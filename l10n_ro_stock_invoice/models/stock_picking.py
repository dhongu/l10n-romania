# ©  2015-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        super(StockPicking, self)._action_done()
        sale_orders = self.env["sale.order"]
        for picking in self:
            if (
                picking.sale_id
                and not picking.notice
                and picking.location_dest_id.usage == "customer"
                and picking.location_id.usage == "internal"
            ):
                sale_order = picking.sale_id
                is_downpayment = sale_order.order_line.filtered(
                    lambda sale_order_line: sale_order_line.is_downpayment
                )
                if not is_downpayment:
                    sale_orders |= picking.sale_id

        # if len(sale_orders) == 1:
        #     sale_order = sale_orders
        #     is_downpayment = sale_order.order_line.filtered(
        #         lambda sale_order_line: sale_order_line.is_downpayment
        #     )
        #     if is_downpayment:
        #         action_obj = self.env.ref("sale.action_view_sale_advance_payment_inv")
        #         action = action_obj.read()[0]
        #         action["context"] = {
        #             "force_period_date": picking.date,
        #             "active_model": "sale.order",
        #             "active_id": sale_orders.id,
        #         }
        #         return action

        if sale_orders:
            invoices = sale_orders.sudo()._create_invoices()
            invoices.action_post()
