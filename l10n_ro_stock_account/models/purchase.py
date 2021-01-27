# ©  2008-2018 Fekete Mihai <mihai.fekete@forbiom.eu>
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import fields, models

"""
class purchase_order(models.Model):
    _inherit = 'purchase.order'

    # todo: care o fi metoda in Odoo10  - pregateste  pretul cu care se va face intrare in stoc
    @api.model
    def _prepare_order_line_move(self, order, order_line,  picking_id, group_id ):
        '''
        prepare the stock move data from the PO line. This function
        returns a list of dictionary ready to be used in stock.move's
        create()
        '''

        res = super(purchase_order, self)._prepare_order_line_move(  order, order_line, picking_id, group_id)
        product_uom = self.pool.get('uom.uom')
        price_unit = order_line.price_unit
        if order_line.product_uom.id != order_line.product_id.uom_id.id:
            price_unit *= order_line.product_uom.factor /  order_line.product_id.uom_id.factor
        ctx = dict(self.env.context)
        ctx.update({'date': order.date_order})
        if order.currency_id.id != order.company_id.currency_id.id:
            #we don't round the price_unit, as we may want to store the
            #standard price with more digits than allowed by the currency
            price_unit = self.pool.get('res.currency').compute(  order.currency_id.id, order.company_id.currency_id.id,  price_unit, round=False)
        for line in res:
            line['price_unit'] = price_unit
        return res
"""
