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
import datetime
import dateutil.relativedelta

class sale_purchase_journal_report(osv.osv_memory):
    _name = 'sale.purchase.journal.report'
    _description = 'Sale/Purchase Journal Report'

    def onchange_period_id(self, cr, uid, ids, period_id=False, context=None):
        res = {}
        if period_id:
            period = self.pool.get('account.period').browse(cr, uid, period_id, context=context)
            res['value'] = {'date_from': period.date_start, 'date_to': period.date_stop}
        return res
    
    
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'journal': fields.selection(
            [('purchase', 'Purchase'), ('sale', 'Sale')],
            'Journal type',
            select=True
        ),
        'periods': fields.many2one('account.period', 'Period', required=True),
        'date_from': fields.date("Start Date", required=True),
        'date_to': fields.date("End Date", required=True),        
    }

    def _get_period(self, cr, uid, context=None):
        if context is None:
            context = {}
        now = datetime.date.today()
        periods = self.pool.get('account.period').find(cr, uid, now + dateutil.relativedelta.relativedelta(months=-1))
        return periods and periods[0] or False

    _defaults = {
        "company_id": lambda obj, cr, uid, context: obj.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
        'journal': 'sale',
        'periods': _get_period,
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        context['data'] = data
        context['landscape'] = True
        period = self.pool.get('account.period').browse(cr, uid, data['periods'][0], context=context)
        if data['date_from'] < period.date_start or data['date_from'] > period.date_stop or \
                data['date_to'] < period.date_start or data['date_to'] > period.date_stop:
            raise osv.except_osv(_('Error!'),_('Dates selected must be in the same period.'))
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
