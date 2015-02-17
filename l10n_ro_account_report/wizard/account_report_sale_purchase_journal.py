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


class sale_purchase_journal_report(osv.osv_memory):
    _name = 'sale.purchase.journal.report'
    _description = 'Sale/Purchase Journal Report'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'journal': fields.selection(
            [('purchase', 'Purchase'), ('sale', 'Sale')],
            'Journal type',
            select=True
        ),
        'periods': fields.many2one('account.period', 'Period'),
    }

    _defaults = {
        "company_id": lambda obj, cr, uid, context: obj.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
        'journal': 'sale',
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        context['data'] = data
        context['landscape'] = True
        if data['journal'] == 'sale':
            return self.pool['report'].get_action(cr, uid, [], 'l10n_ro_account_report.report_sale_journal', data=data, context=context)
        else:
            return self.pool['report'].get_action(cr, uid, [], 'l10n_ro_account_report.report_purchase_journal', data=data, context=context)

    def print_html_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        context['data'] = data
        context['landscape'] = True
        if data['journal'] == 'sale':
            return self.pool['report'].get_action(cr, uid, [], 'l10n_ro_account_report.report_sale_journal_html', data=data, context=context)
        else:
            return self.pool['report'].get_action(cr, uid, [], 'l10n_ro_account_report.report_purchase_journal_html', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
