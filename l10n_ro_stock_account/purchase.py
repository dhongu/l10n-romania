# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2014 FOREST AND BIOMASS SERVICES ROMANIA SA
#    (http://www.forbiom.eu).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _


class purchase_order(osv.osv):
    _inherit = 'purchase.order'

    def _prepare_order_line_move(self, cr, uid, order, order_line,
                                 picking_id, group_id, context=None):
        ''' prepare the stock move data from the PO line. This function '''
        ''' returns a list of dictionary ready to be used in stock.move's '''
        ''' create()'''
        res = super(purchase_order, self)._prepare_order_line_move(
            cr, uid, order, order_line, picking_id, group_id, context=context)
        product_uom = self.pool.get('product.uom')
        price_unit = order_line.price_unit
        if order_line.product_uom.id != order_line.product_id.uom_id.id:
            price_unit *= order_line.product_uom.factor / \
                            order_line.product_id.uom_id.factor
        ctx = dict(context)
        ctx.update({'date': order.date_order})
        if order.currency_id.id != order.company_id.currency_id.id:
            #we don't round the price_unit, as we may want to store the
            #standard price with more digits than allowed by the currency
            price_unit = self.pool.get('res.currency').compute(
            cr, uid, order.currency_id.id, order.company_id.currency_id.id,
            price_unit, round=False, context=ctx)
        for line in res:
            line['price_unit'] = price_unit
        return res
