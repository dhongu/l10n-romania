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
                sale_orders |= picking.sale_id

        if sale_orders:
            invoices = sale_orders.sudo()._create_invoices()
            invoices.action_post()
