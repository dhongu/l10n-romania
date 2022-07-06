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

from odoo.osv import fields, osv


class account_balance_report_romania(osv.osv_memory):
    _inherit = "account.balance.report"
    _name = 'account.balance.report.romania'
    _description = 'Trial Balance Report'

    _columns = {
        'journal_ids': fields.many2many(
            'account.journal',
            'account_balance_report_journal_rel_ro',
            'account_id',
            'journal_id',
            'Journals',
            required=True
        ),
    }

    _defaults = {
        'journal_ids': lambda self, cr, uid, c: self.pool.get('account.journal').search(cr, uid, [], context=c),
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        context['landscape'] = True
        return self.pool['report'].get_action(cr, uid, [], 'l10n_ro_account_report.report_trialbalance', data=data, context=context)


class account_balance_html_report_romania(osv.osv_memory):
    _inherit = "account.balance.report"
    _name = 'account.balance.html.report.romania'
    _description = 'Trial Balance Report'

    _columns = {
        'journal_ids': fields.many2many(
            'account.journal',
            'account_balance_html_report_journal_rel_ro',
            'account_id',
            'journal_id',
            'Journals',
            required=True
        ),
    }

    _defaults = {
        'journal_ids': lambda self, cr, uid, c: self.pool.get('account.journal').search(cr, uid, [], context=c),
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        context['landscape'] = True
        return self.pool['report'].get_action(cr, uid, [], 'l10n_ro_account_report.report_trialbalance_html', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
