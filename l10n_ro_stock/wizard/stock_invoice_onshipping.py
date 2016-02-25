# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2014 FOREST AND BIOMASS SERVICES ROMANIA SA (http://www.forbiom.eu).
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


class stock_invoice_onshipping(osv.osv_memory):
    _name = "stock.invoice.onshipping"
    _inherit = "stock.invoice.onshipping"

    def _get_invoice_date(self, cr, uid, context=None):
        if context is None:
            context = {}
        res_ids = context and context.get('active_ids', [])
        pick_obj = self.pool.get('stock.picking')
        pickings = pick_obj.browse(cr, uid, res_ids, context=context)
        vals = []
        pick = pickings and pickings[0]
        return pick.date
    
    
    # metoda asta o fi buna pentru stornarea in rosu !
    """
    def _get_journal_type(self, cr, uid, context=None):
        journal_type = super(stock_invoice_onshipping, self)._get_journal_type(
            cr, uid, context=context)
        if context is None:
            context = {}
        res_ids = context and context.get('active_ids', [])
        pick_obj = self.pool.get('stock.picking')
        pickings = pick_obj.browse(cr, uid, res_ids, context=context)
        vals = []
        pick = pickings and pickings[0]
        if not pick or not pick.move_lines:
            return 'sale'
        src_usage = pick.move_lines[0].location_id.usage
        dest_usage = pick.move_lines[0].location_dest_id.usage
        type = pick.picking_type_id.code
        if type == 'outgoing' and dest_usage == 'supplier':
            journal_type = 'purchase'
        elif type == 'outgoing' and dest_usage == 'customer':
            journal_type = 'sale'
        elif type == 'incoming' and src_usage == 'supplier':
            journal_type = 'purchase'
        elif type == 'incoming' and src_usage == 'customer':
            journal_type = 'sale'
        else:
            journal_type = 'sale'
        return journal_type
    """
    
    _columns = {
        'invoice_date':   fields.date('Invoice Date'),
    }

    _defaults = {
        'invoice_date': _get_invoice_date,
    }
    
    
    # metoda asta este identica cu cea standard 
    """
    def create_invoice(self, cr, uid, ids, context=None):
        context = dict(context or {})
        picking_pool = self.pool.get('stock.picking')
        data = self.browse(cr, uid, ids[0], context=context)
        journal2type = {'sale': 'out_invoice', 'purchase': 'in_invoice',
                        'sale_refund': 'out_invoice', 'purchase_refund': 'in_invoice'}
        context['date_inv'] = data.invoice_date
        acc_journal = self.pool.get("account.journal")
        inv_type = journal2type.get(data.journal_type) or 'out_invoice'
        context['inv_type'] = inv_type

        active_ids = context.get('active_ids', [])
        res = picking_pool.action_invoice_create(cr, uid, active_ids,
                                                 journal_id=data.journal_id.id,
                                                 group=data.group,
                                                 type=inv_type,
                                                 context=context)
        return res
    """
