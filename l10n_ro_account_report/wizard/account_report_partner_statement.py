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

class account_partner_ledger(osv.osv_memory):

    _inherit = 'account.partner.ledger'

    def _print_report(self, cr, uid, ids, data, context=None):
        if data.get('form', False) and data['form'].get('period_to', False):
            data['date_stop'] = self.pool.get('account.period').browse(cr, uid, data['form']['period_to']).name
        else:
            if data.get('form', False) and data['form'].get('fiscalyear_id', False):
                data['date_stop'] = self.pool.get('account.fiscalyear').browse(cr, uid, data['form']['fiscalyear_id']).date_stop
            else:
                data['date_stop'] = False
        return super(account_partner_ledger,self)._print_report( cr, uid, ids, data, context)
 
 
class account_partner_statement(osv.osv_memory):
    """
        This wizard will provide the partner balance report by periods, between any two dates.
    """
    _inherit = 'account.common.partner.report'
    _name = 'account.partner.statement'
    _description = 'Print Account Partner Statement '
    _columns = {
        'display_partner': fields.selection([('non-zero_balance', 'With balance is not equal to 0'), ('all', 'All Partners')]
                                    ,'Display Partners'),
        'journal_ids': fields.many2many('account.journal', 'account_partner_statement_journal_rel', 'account_id', 'journal_id', 'Journals', required=True),
    }

    _defaults = {
        'display_partner': 'non-zero_balance',
    }

    """
    metoda asta e mai buna
    def get_end_period(self, data):
        if data.get('form', False) and data['form'].get('period_to', False):
            return self.pool.get('account.period').browse(self.cr, self.uid, data['form']['period_to']).name
        else:
            if data.get('form', False) and data['form'].get('fiscalyear_id', False):
                return self.pool.get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).date_stop
                
        return ''
    """


    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['display_partner'])[0])
        if data.get('form', False) and data['form'].get('period_to', False):
            data['date_stop'] = self.pool.get('account.period').browse(cr, uid, data['form']['period_to']).name
        else:
            if data.get('form', False) and data['form'].get('fiscalyear_id', False):
                data['date_stop'] = self.pool.get('account.fiscalyear').browse(cr, uid, data['form']['fiscalyear_id']).date_stop
            else:
                data['date_stop'] = False         
        return self.pool['report'].get_action(cr, uid, [], 'l10n_ro_account_report.report_partnerstatement', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
