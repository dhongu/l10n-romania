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

import time

from datetime import datetime
from datetime import timedelta

from openerp.osv import osv
from openerp.report import report_sxw
from common_report_header import common_report_header


class account_balance_romania(report_sxw.rml_parse, common_report_header):
    _name = 'report.l10n_ro_account_report.account.balance.romania'

    def __init__(self, cr, uid, name, context=None):
        super(account_balance_romania, self).__init__(
            cr, uid, name, context=context)
        self.sum_debit_op = 0.00
        self.sum_credit_op = 0.00
        self.sum_debit_init = 0.00
        self.sum_credit_init = 0.00
        self.sum_debit = 0.00
        self.sum_credit = 0.00
        self.sum_balance = 0.00
        self.sum_debit_fy = 0.00
        self.sum_credit_fy = 0.00
        self.sum_balance_fy = 0.00
        self.date_lst = []
        self.date_lst_string = ''
        self.result_acc = []
        self.user = self.pool.get('res.users').browse(cr, uid, uid)
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'get_fiscalyear': self._get_fiscalyear,
            'get_filter': self._get_filter,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_account': self._get_account,
            'get_journal': self._get_journal,
            'get_start_date': self._get_start_date,
            'get_end_date': self._get_end_date,
            'get_target_move': self._get_target_move,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] and [
                data['form']['chart_account_id']] or []
            objects = self.pool.get('account.account').browse(
                self.cr, self.uid, new_ids)
        return super(account_balance_romania, self).set_context(objects, data, new_ids, report_type=report_type)

    def _get_account(self, data):
        if data['model'] == 'account.account':
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['id']).company_id.name
        return super(account_balance_romania, self)._get_account(data)

    def lines(self, form, ids=None, done=None):
        def _process_child(accounts, disp_acc, parent):
            account_rec = [
                acct for acct in accounts if acct['id'] == parent][0]
            currency_obj = self.pool.get('res.currency')
            acc_id = self.pool.get('account.account').browse(
                self.cr, self.uid, account_rec['id'])
            currency = acc_id.currency_id and acc_id.currency_id or acc_id.company_id.currency_id
            res = {
                'id': account_rec['id'],
                'type': account_rec['type'],
                'code': account_rec['code'],
                'name': account_rec['name'],
                'level': account_rec['level'],
                'debit': account_rec['debit'],
                'credit': account_rec['credit'],
                'balance': account_rec['balance'],
                'parent_id': account_rec['parent_id'],
                'bal_type': '',
            }
            self.sum_debit += account_rec['debit']
            self.sum_credit += account_rec['credit']
            if account_rec['child_id']:
                for child in account_rec['child_id']:
                    _process_child(accounts, disp_acc, child)

        account_obj = self.pool.get('account.account')
        currency_obj = self.pool.get('res.currency')
        period_obj = self.pool.get('account.period')
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        company_id = user.company_id and user.company_id.id
        company = self.pool.get('res.company').browse(
            self.cr, self.uid, company_id)
        if not ids:
            ids = self.ids
        if not ids:
            return []
        if not done:
            done = {}

        ctx = self.context.copy()

        if form.get('fiscalyear_id'):
            fiscalyear = fiscalyear_obj.browse(
                self.cr, self.uid, form['fiscalyear_id'])
        else:
            fiscalyear = fiscalyear_obj.browse(
                self.cr, self.uid, fiscalyear_obj.find(self.cr, self.uid))
        ctx['fiscalyear'] = form['fiscalyear_id']
        if form['filter'] == 'filter_period':
            ctx['period_from'] = form['period_from']
            ctx['period_to'] = form['period_to']
        elif form['filter'] == 'filter_date':
            ctx['date_from'] = form['date_from']
            ctx['date_to'] = form['date_to']
        else:
            ctx['period_from'] = period_obj.browse(
                self.cr, self.uid, period_obj.find(self.cr, self.uid, dt=False))[0].id
            ctx['period_to'] = period_obj.browse(
                self.cr, self.uid, period_obj.find(self.cr, self.uid, dt=False))[0].id
        ctx['state'] = form['target_move']
        parents = ids
        child_ids = account_obj._get_children_and_consol(
            self.cr, self.uid, ids, ctx)
        if child_ids:
            ids = child_ids
        accounts = account_obj.read(self.cr, self.uid, ids, [
                                    'type', 'code', 'name', 'debit', 'credit', 'balance', 'parent_id', 'level', 'child_id'], ctx)

        #
        # Calculate the final year Balance
        # (fy balance minus the balance from the start of the selected period
        #  to the end of the year)
        #
        ctx = self.context.copy()
        ctx['state'] = form['target_move']
        ctx['fiscalyear'] = form['fiscalyear_id']
        ctx['periods'] = period_obj.search(
            self.cr, self.uid, [('fiscalyear_id', '=', fiscalyear.id)])

        fy_debit = {}
        fy_credit = {}
        fy_balance = {}
        for acc in account_obj.read(self.cr, self.uid, ids, ['debit', 'credit', 'balance'], ctx):
            fy_debit[acc['id']] = acc['debit']
            fy_credit[acc['id']] = acc['credit']
            fy_balance[acc['id']] = acc['balance']

        #
        # Calculate the opening period Debit/Credit
        # (from the selected period or all the non special periods in the fy)
        #
        ctx = self.context.copy()
        ctx['state'] = form['target_move']
        ctx['fiscalyear'] = form['fiscalyear_id']
        ctx['periods'] = period_obj.search(self.cr, self.uid, [(
            'fiscalyear_id', '=', fiscalyear.id), ('special', '=', True), ('date_start', '=', fiscalyear.date_start)])

        period_creditop = {}
        for acc in account_obj.read(self.cr, self.uid, ids, ['credit'], ctx):
            period_creditop[acc['id']] = acc['credit']
        period_debitop = {}
        for acc in account_obj.read(self.cr, self.uid, ids, ['debit'], ctx):
            period_debitop[acc['id']] = acc['debit']

        #
        # Calculate the period initial Balance
        # (fy balance minus the balance from the start of the selected period
        #  to the end of the year)
        #
        ctx = self.context.copy()
        ctx['state'] = form['target_move']
        ctx['fiscalyear'] = fiscalyear.id
        if form['filter'] == 'filter_period':
            periods = []
            for period in period_obj.browse(self.cr, self.uid, period_obj.search(self.cr, self.uid, [('fiscalyear_id', '=', fiscalyear.id)])):
                if period.date_stop <= period_obj.browse(self.cr, self.uid, form['period_from']).date_start:
                    periods.append(period.id)
                ctx['periods'] = periods
        elif form['filter'] == 'filter_date':
            ctx['date_from'] = str(fiscalyear.date_start)
            ctx['date_to'] = str(
                (datetime.strptime(form['date_from'], '%Y-%m-%d') + timedelta(days=-1)).date())
        else:
            period_now = period_obj.browse(
                self.cr, self.uid, period_obj.find(self.cr, self.uid, dt=False))[0]

            ctx['date_from'] = str(fiscalyear.date_start)
            ctx['date_to'] = str(
                (datetime.strptime(period_now.date_start, '%Y-%m-%d') + timedelta(days=-1)).date())

        period_balanceinit = {}
        for acc in account_obj.read(self.cr, self.uid, ids, ['balance'], ctx):
            period_balanceinit[acc['id']] = acc['balance']
        period_creditinit = {}
        for acc in account_obj.read(self.cr, self.uid, ids, ['credit'], ctx):
            period_creditinit[acc['id']] = acc['credit']
        period_debitinit = {}
        for acc in account_obj.read(self.cr, self.uid, ids, ['debit'], ctx):
            period_debitinit[acc['id']] = acc['debit']

        result = []
        for parent in parents:
            if parent in done:
                continue
            done[parent] = 1
            _process_child(accounts, form['display_account'], parent)

        for account in accounts:
            account_id = account['id']

            if account_id in done:
                continue

            done[account_id] = 1

            #
            # Calculate the account level
            #
            fy_credit1 = period_creditinit[account_id] + account['credit']
            fy_debit1 = period_debitinit[account_id] + account['debit']
            fy_balance1 = fy_debit1 - fy_credit1
            if fy_balance1 < 0:
                fy_balance_de1 = 0
                fy_balance_cr1 = -fy_balance1
            else:
                fy_balance_cr1 = 0
                fy_balance_de1 = fy_balance1
            res = {
                'id': account_id,
                'type': account['type'],
                'code': account['code'],
                'name': account['name'],
                'level': account['level'],
                'credit_op': period_creditop[account_id],
                'debit_op': period_debitop[account_id],
                'credit_init': period_creditinit[account_id],
                'debit_init': period_debitinit[account_id],
                'debit': account['debit'],
                'credit': account['credit'],
                'debit_fy': fy_debit1,
                'credit_fy': fy_credit1,
                'balance_de_fy': fy_balance_de1,
                'balance_cr_fy': fy_balance_cr1,
                'parent_id': account['parent_id'],
                'bal_type': '',
            }
            if form['display_account'] == 'movement':
                if period_creditop[account_id] != 0.00 or period_debitop[account_id] != 0.00 or period_creditinit[account_id] != 0.00 or period_debitinit[account_id] != 0.00 or account['debit'] != 0.00 or account['credit'] != 0.00 or fy_debit1 != 0.00 or fy_credit1 != 0.00 or fy_balance_de1 != 0.00 or fy_balance_cr1 != 0.00:
                    self.result_acc.append(res)
            elif form['display_account'] == 'not_zero':
                if fy_balance1 != 0.00:
                    self.result_acc.append(res)
            else:
                self.result_acc.append(res)
        return self.result_acc


class report_trialbalance(osv.AbstractModel):
    _name = 'report.l10n_ro_account_report.report_trialbalance'
    _inherit = 'report.abstract_report'
    _template = 'l10n_ro_account_report.report_trialbalance'
    _wrapped_report_class = account_balance_romania


class report_trialbalance_html(osv.AbstractModel):
    _name = 'report.l10n_ro_account_report.report_trialbalance_html'
    _inherit = 'report.abstract_report'
    _template = 'l10n_ro_account_report.report_trialbalance_html'
    _wrapped_report_class = account_balance_romania

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
