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

from odoo import models, fields, api, _

"""
class account_partner_ledger(models.TransientModel):

    _inherit = 'account.partner.ledger'

    def _print_report(self,   data ):
        if data.get('form', False) and data['form'].get('period_to', False):
            data['date_stop'] = self.env['account.period'].browse(data['form']['period_to']).name
        else:
            if data.get('form', False) and data['form'].get('fiscalyear_id', False):
                data['date_stop'] = self.env['account.fiscalyear'].browse( data['form']['fiscalyear_id']).date_stop
            else:
                data['date_stop'] = False
        return super(account_partner_ledger,self)._print_report(  data )
 
"""


class account_partner_statement(models.TransientModel):
    """
        This wizard will provide the partner balance report by periods, between any two dates.
    """
    _inherit = 'account.common.partner.report'
    _name = 'account.partner.statement'
    _description = 'Print Account Partner Statement '

    display_partner = fields.Selection([('non-zero_balance', 'With balance is not equal to 0'), ('all', 'All Partners')]
                                       , string='Display Partners', default='non-zero_balance')
    journal_ids = fields.Many2many('account.journal', 'account_partner_statement_journal_rel', 'account_id',
                                   'journal_id', string='Journals', required=True)

    """
    def _print_report(self, data):

        data = self.pre_print_report(data)
        data['form'].update(self.read(['display_partner'])[0])
        if data.get('form', False) and data['form'].get('period_to', False):
            data['date_stop'] = self.env['account.period'].browse(data['form']['period_to']).name
        else:
            if data.get('form', False) and data['form'].get('fiscalyear_id', False):
                data['date_stop'] = self.env['account.fiscalyear'].browse(data['form']['fiscalyear_id']).date_stop
            else:
                data['date_stop'] = False
        return self.env['report'].get_action([], 'l10n_ro_account_report.report_partnerstatement', data=data)
    """

