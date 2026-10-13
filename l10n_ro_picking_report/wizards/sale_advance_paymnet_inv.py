from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoices(self, sale_orders):
        res = super()._create_invoices(sale_orders)
        for order in sale_orders:
            pickings = order.picking_ids.filtered(lambda p: p.state == "done")
            if not pickings:
                pickings = order.picking_ids.filtered(lambda p: p.state not in ["cancel"])
            if pickings:
                picking = pickings[0]
                invoices = res.filtered(lambda i: i.invoice_origin == order.name)
                if not invoices:
                    invoices = res
                invoices.write(
                    {
                        "delegate_id": picking.delegate_id.id if picking.delegate_id else False,
                        "mean_transp": picking.mean_transp,
                    }
                )
        return res
