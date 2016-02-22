# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _

JOURNAL_TYPE_MAP = {
    ('outgoing', 'customer'): ['sale'],
    ('outgoing', 'supplier'): ['purchase_refund'],
    ('outgoing', 'transit'): ['sale', 'purchase_refund'],
    ('internal', 'in_custody'): ['purchase'],
    ('incoming', 'supplier'): ['purchase'],
    ('incoming', 'customer'): ['sale_refund'],
    ('incoming', 'transit'): ['purchase', 'sale_refund'],
}


class stock_invoice_onshipping(osv.osv_memory):
    _inherit = "stock.invoice.onshipping"

    def _get_journal_type(self, cr, uid, context=None):
        res = super(stock_invoice_onshipping, self)._get_journal_type(cr, uid, context)
        if context is None:
            context = {}
        res_ids = context and context.get('active_ids', [])
        pick_obj = self.pool.get('stock.picking')
        pickings = pick_obj.browse(cr, uid, res_ids, context=context)
        pick = pickings and pickings[0]
        type = pick.picking_type_id.code
        if type == 'internal' and pick.move_lines[0].location_id.usage == 'in_custody' and pick.move_lines[0].location_dest_id.usage == 'internal':
            usage = pick.move_lines[0].location_id.usage
            res = JOURNAL_TYPE_MAP.get((type, usage), ['sale'])[0]
        return res

    _defaults = {
        'journal_type': _get_journal_type,
    }
