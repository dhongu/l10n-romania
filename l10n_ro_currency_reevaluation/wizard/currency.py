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

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

import time
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


class currency_reevaluation(models.TransientModel):
    _name = 'currency.reevaluation'

    period_id = fields.Many2one(
        'account.period', 'Period', help="The period to compute moves.", required=True)
    journal_id = fields.Many2one(
        'account.journal', 'Journal', help="The journal to post the entries.", required=True)
    company_id = fields.Many2one('res.company', 'Company', help="The company for which is the reevaluation.", required=True,
                                 change_default=True, default=lambda self: self.env['res.company']._company_default_get('currency.reevaluation'))

    @api.one
    def compute_difference(self):

        form = self[0]
        move_obj = self.env['account.move']
        account_obj = self.env['account.account']
        journal_obj = self.env['account.journal']
        move_line_obj = self.env['account.move.line']
        period_obj = self.env['account.period']
        curr_obj = self.env['res.currency']

        # get current period from company
        company = form.company_id
        period = form.period_id
        journal = form.journal_id

        company_currency = company.currency_id
        reevaluation_date = period.date_stop
        account_ids = [account.id for account in account_obj.search(
            [('currency_reevaluation', '=', True), ('company_id', '=', company.id)])]

        date1 = datetime.strptime(
            reevaluation_date, "%Y-%m-%d") + relativedelta(day=1, months=+1)

        ctx = dict(self._context)
        ctx1 = dict(self._context)
        ctx.update({'date': date1})

        # get account move lines with foreign currency posted before reevaluation date (end of period)
        # balance and foreign balance are not taking in consideration newwer
        # reconciliations
        query = """ SELECT DISTINCT sub.id, sub.date, sub.account_id, sub.journal_id, sub.partner_id, sub.currency_id,
                    COALESCE(SUM(sub.balance),0) + COALESCE(SUM(sub.pay_amount),0) as balance,
                    COALESCE(SUM(sub.foreign_balance),0) + COALESCE(SUM(sub.foreign_pay_amount),0) as foreign_balance
                    FROM (SELECT l.id as id, l.date as date, COALESCE(partner.id,0) AS partner_id,
                    account.id as account_id, l.journal_id as journal_id, COALESCE(SUM(l.debit - l.credit),0) / (CASE WHEN EXISTS(select lrec.id from account_move_line lrec WHERE l.reconcile_partial_id = lrec.reconcile_partial_id and l.id != lrec.id AND lrec.date <= %(reevaluation_date)s::date) THEN COUNT(lrec.id) ELSE 1 END) as balance,
                    COALESCE(SUM(l.amount_currency),0) / (CASE WHEN EXISTS(select lrec.id from account_move_line lrec WHERE l.reconcile_partial_id = lrec.reconcile_partial_id and l.id != lrec.id AND lrec.date <= %(reevaluation_date)s::date) THEN COUNT(lrec.id) ELSE 1 END) as foreign_balance,
                    COALESCE(SUM(lrec.debit - lrec.credit),0) as pay_amount,
                    COALESCE(SUM(lrec.amount_currency),0) as foreign_pay_amount,
                    l.currency_id as currency_id
                    FROM account_move_line l
                    LEFT JOIN account_move am ON am.id = l.move_id
                    LEFT JOIN account_account account ON account.id = l.account_id
                    LEFT JOIN account_journal journal ON journal.id = l.journal_id
                    LEFT JOIN res_partner partner ON partner.id = l.partner_id
                    LEFT JOIN account_move_line lrec ON l.reconcile_partial_id = lrec.reconcile_partial_id and l.id != lrec.id AND lrec.date <= %(reevaluation_date)s::date
                    WHERE (journal.type::text != 'bank'::character varying::text AND journal.type::text != 'cash'::character varying::text) AND
                    account.company_id = %(company_id)s AND am.state::text = 'posted'::character varying::text AND account.id = ANY(%(account_ids)s) AND l.date <= %(reevaluation_date)s AND l.currency_id IS NOT NULL
                    GROUP BY l.id, account.id, partner.id, l.journal_id, l.currency_id
                    ORDER BY account_id, journal_id, partner_id, l.id) AS sub
                    WHERE sub.foreign_balance <> 0.00 AND sub.currency_id IS NOT NULL
                    GROUP BY partner_id, account_id, journal_id, date, sub.currency_id, sub.id
                    ORDER BY account_id, journal_id, partner_id, sub.id
                """
        params = {'reevaluation_date': reevaluation_date,
                  'account_ids': account_ids, 'company_id': company.id}
        self._cr.execute(query, params)
        lines = self._cr.dictfetchall()

        created_ids = []
        vals = {'name': 'Currency update ' + period.code,
                'journal_id': journal.id,
                'period_id': period.id,
                'date': period.date_stop}
        move_id = move_obj.create(vals)
        move = move_id[0]

        expense_acc = company.expense_currency_exchange_account_id.id
        income_acc = company.income_currency_exchange_account_id.id
        for line in lines:
            aml = move_line_obj.browse(line['id'])
            currency = curr_obj.browse(line['currency_id'])
            account = account_obj.browse(line['account_id'])

            new_amount = currency.with_context(ctx).compute(
                line['foreign_balance'], company_currency, round=True)
            rec_ids = []

            if datetime.strptime(line['date'], "%Y-%m-%d").month == datetime.strptime(reevaluation_date, "%Y-%m-%d").month:
                # get current currency rate
                date1 = datetime.strptime(line['date'], "%Y-%m-%d")
                ctx1.update({'date': date1})
            else:
                date1 = datetime.strptime(period.date_start, "%Y-%m-%d")
                ctx1.update({'date': date1})
            old_amount = currency.with_context(ctx1).compute(
                line['foreign_balance'], company_currency, round=True)
            amount = new_amount - old_amount
            if amount != 0.00:
                if amount > 0:
                    eval_account = income_acc
                    debit = abs(amount)
                    credit = 0.00
                    if account.user_type.code in ['payable', 'liability']:
                        partner_id = line[
                            'partner_id'] != 0 and line['partner_id']
                    else:
                        partner_id = False
                else:
                    eval_account = expense_acc
                    debit = 0.00
                    credit = abs(amount)
                    if account.user_type.code in ['payable', 'liability']:
                        partner_id = False
                    else:
                        partner_id = line[
                            'partner_id'] != 0 and line['partner_id']

                ref = 'Currency update ' + \
                    str(line['foreign_balance']) + ' ' + str(currency.name)
                valsm = {
                    'name': ref,
                    'ref': ref,
                    'move_id': move.id,
                    'journal_id': journal.id,
                    'account_id': account.id,
                    'partner_id': line['partner_id'],
                    'period_id': period.id,
                    'debit': debit,
                    'credit': credit,
                    'amount_currency': 0.00,
                    'currency_id': currency.id,
                    'date': period.date_stop,
                }
                part_move = move_line_obj.create(valsm)
                valsm = {
                    'name': ref,
                    'ref': ref,
                    'move_id': move.id,
                    'journal_id': journal.id,
                    'account_id': eval_account,
                    'partner_id': False,
                    'period_id': period.id,
                    'debit': credit,
                    'credit': debit,
                    'amount_currency': 0.00,
                    'currency_id': currency.id,
                    'date': period.date_stop,
                }
                move_line_obj.create(valsm)

                move_lines = [
                    move_line.id for move_line in aml.reconcile_partial_id.line_partial_ids]
                move_lines.append(part_move[0].id)
                move_line_obj.browse(move_lines).reconcile_partial('auto')

        created_ids.append(move_id)

        lines = []
        query = """ SELECT DISTINCT ON (journal_id) j.id as journal_id, s.date AS date, s.balance_end_real as balance, c.id as currency_id
                       FROM account_bank_statement s
                       INNER JOIN account_journal j on s.journal_id = j.id
                       INNER JOIN res_company com on s.company_id = com.id
                       INNER JOIN res_currency c on ((j.currency is not null and j.currency = c.id))
                       INNER JOIN
                           (SELECT journal_id, max(date) as max_date FROM account_bank_statement
                               WHERE date <= %(reevaluation_date)s::date AND state = 'confirm'
                               GROUP BY journal_id) d ON (s.journal_id = d.journal_id AND s.date = d.max_date)
                       WHERE j.company_id = %(company_id)s
                       ORDER BY journal_id, date"""
        params = {
            'reevaluation_date': reevaluation_date, 'company_id': company.id}
        self._cr.execute(query, params)
        lines = self._cr.dictfetchall()
        for line in lines:
            currency = curr_obj.browse(line['currency_id'])
            journal = journal_obj.browse(line['journal_id'])

            new_amount = currency.with_context(ctx).compute(
                line['balance'], company_currency, round=True)
            rec_ids = []

            if datetime.strptime(line['date'], "%Y-%m-%d").month == datetime.strptime(reevaluation_date, "%Y-%m-%d").month:
                # get current currency rate
                date1 = datetime.strptime(line['date'], "%Y-%m-%d")
                ctx1.update({'date': date1})
            else:
                date1 = datetime.strptime(period.date_start, "%Y-%m-%d")
                ctx1.update({'date': date1})
            old_amount = currency.with_context(ctx1).compute(
                line['balance'], company_currency, round=True)
            amount = new_amount - old_amount
            if amount != 0.00:
                vals = {'name': 'Currency update ' + period.code,
                        'journal_id': journal.id,
                        'period_id': period.id,
                        'date': period.date_stop}
                move_id = move_obj.create(vals)
                move = move_id[0]

                if amount > 0:
                    eval_account = income_acc
                    journal_account = journal.default_debit_account_id
                    debit = abs(amount)
                    credit = 0.00
                else:
                    eval_account = expense_acc
                    journal_account = journal.default_credit_account_id
                    debit = 0.00
                    credit = abs(amount)

                valsm = {
                    'name': 'Currency update ' + str(line['balance']),
                    'ref': 'Currency update ' + str(line['balance']),
                    'move_id': move.id,
                    'journal_id': journal.id,
                    'account_id': journal_account.id,
                    'partner_id': False,
                    'period_id': period.id,
                    'debit': debit,
                    'credit': credit,
                    'amount_currency': 0.00,
                    'currency_id': currency.id,
                    'date': period.date_stop,
                }
                move_line_obj.create(valsm)
                valsm = {
                    'name': 'Update ' + str(line['balance']),
                    'ref': 'Update ' + str(line['balance']),
                    'move_id': move.id,
                    'journal_id': journal.id,
                    'account_id': eval_account,
                    'partner_id': False,
                    'period_id': period.id,
                    'debit': credit,
                    'credit': debit,
                    'amount_currency': 0.00,
                    'currency_id': currency.id,
                    'date': period.date_stop,
                }
                move_line_obj.create(valsm)
                created_ids.append(move_id)
        if created_ids:
            return {'domain': "[('id','in', %s)]" % (created_ids,),
                    'name': _("Created reevaluation lines"),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'auto_search': True,
                    'res_model': 'account.move',
                    'view_id': False,
                    'search_view_id': False,
                    'type': 'ir.actions.act_window'}
        else:
            raise except_orm(
                _("Warning"), _("No accounting entry have been posted."))
