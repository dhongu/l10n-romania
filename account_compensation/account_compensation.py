# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2014 FOREST AND BIOMASS SERVICES ROMANIA SA
#    (http://www.forbiom.eu).
#    Modified account.voucher module
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

import time
from lxml import etree

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare
import openerp


class account_compensation(osv.osv):

    def _get_period(self, cr, uid, context=None):
        if context is None:
            context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        periods = self.pool.get('account.period').find(
            cr, uid, context=context)
        return periods and periods[0] or False

    def _make_journal_search(self, cr, uid, ttype, context=None):
        journal_pool = self.pool.get('account.journal')
        return journal_pool.search(cr, uid, [('type', '=', ttype)], limit=1)

    def _get_journal(self, cr, uid, context=None):
        if context is None:
            context = {}
        res = self._make_journal_search(cr, uid, 'general', context=context)
        return res and res[0] or False

    def _get_currency(self, cr, uid, context=None):
        if context is None:
            context = {}
        journal_pool = self.pool.get('account.journal')
        journal_id = context.get('journal_id', False)
        if journal_id:
            journal = journal_pool.browse(cr, uid, journal_id, context=context)
            if journal.currency:
                return journal.currency.id
        return self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.currency_id.id

    def _get_partner(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('partner_id', False)

    def _get_narration(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('narration', False)

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if context is None:
            context = {}
        return [(r['id'], (r['number'] or _('Compensation'))) for r in self.read(cr, uid, ids, ['number'], context, load='_classic_write')]

    def onchange_line_ids(self, cr, uid, ids, line_dr_ids, line_cr_ids, compensation_currency, context=None):
        context = context or {}
        if not line_dr_ids and not line_cr_ids:
            return {'value': {}}
        # resolve lists of commands into lists of dicts
        line_dr_ids = self.resolve_2many_commands(
            cr, uid, 'line_dr_ids', line_dr_ids, context)
        line_cr_ids = self.resolve_2many_commands(
            cr, uid, 'line_cr_ids', line_cr_ids, context)
        # compute the field is_multi_currency that is used to hide/display
        # options linked to secondary currency on the compensation
        is_multi_currency = False
        # loop on the compensation lines to see if one of these has a secondary
        # currency. If yes, we need to see the options
        for compensation_line in line_dr_ids + line_cr_ids:
            line_id = compensation_line.get('id') and self.pool.get('account.compensation.line').browse(
                cr, uid, compensation_line['id'], context=context).move_line_id.id or compensation_line.get('move_line_id')
            if line_id and self.pool.get('account.move.line').browse(cr, uid, line_id, context=context).currency_id:
                is_multi_currency = True
                break
        return {'value': {'is_multi_currency': is_multi_currency}}

    def _get_journal_currency(self, cr, uid, ids, name, args, context=None):
        res = {}
        for compensation in self.browse(cr, uid, ids, context=context):
            res[compensation.id] = compensation.journal_id.currency and compensation.journal_id.currency.id or compensation.company_id.currency_id.id
        return res

    _name = 'account.compensation'
    _description = 'Accounting Compensation'
    _inherit = ['mail.thread']
    _order = "date desc, id desc"
#    _rec_name = 'number'
    _track = {
        'state': {
            'account_compensation.mt_compensation_state_change': lambda self, cr, uid, obj, ctx=None: True,
        },
    }

    _columns = {
        'name': fields.char('Memo', readonly=True, states={'draft': [('readonly', False)]}),
        'date': fields.date('Date', readonly=True, select=True, states={'draft': [('readonly', False)]},
                            help="Effective date for accounting entries", copy=False),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, readonly=True, domain=[('type', '=', 'general')], states={'draft': [('readonly', False)]}),
        'line_ids': fields.one2many('account.compensation.line', 'compensation_id', 'Compensation Lines',
                                    readonly=True, copy=True,
                                    states={'draft': [('readonly', False)]}),
        'line_cr_ids': fields.one2many('account.compensation.line', 'compensation_id', 'Credits',
                                       domain=[('type', '=', 'cr')], context={'default_type': 'cr'}, readonly=True, states={'draft': [('readonly', False)]}),
        'line_dr_ids': fields.one2many('account.compensation.line', 'compensation_id', 'Debits',
                                       domain=[('type', '=', 'dr')], context={'default_type': 'dr'}, readonly=True, states={'draft': [('readonly', False)]}),
        'period_id': fields.many2one('account.period', 'Period', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'narration': fields.text('Notes', readonly=True, states={'draft': [('readonly', False)]}),
        'currency_id': fields.function(_get_journal_currency, type='many2one', relation='res.currency', string='Currency', readonly=True, required=True),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection(
            [('draft', 'Draft'),
             ('cancel', 'Cancelled'),
             ('proforma', 'Pro-forma'),
             ('posted', 'Posted')
             ], 'Status', readonly=True, track_visibility='onchange', copy=False,
            help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed compensation. \
                        \n* The \'Pro-forma\' when compensation is in Pro-forma status,compensation does not have an compensation number. \
                        \n* The \'Posted\' status is used when user create compensation,a compensation number is generated and compensation entries are created in account \
                        \n* The \'Cancelled\' status is used when user cancel compensation.'),
        'number': fields.char('Number', readonly=True, copy=False),
        'move_id': fields.many2one('account.move', 'Account Entry', copy=False),
        'move_ids': fields.related('move_id', 'line_id', type='one2many', relation='account.move.line', string='Journal Items', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Partner', change_default=1, readonly=True, states={'draft': [('readonly', False)]}),
        'is_multi_currency': fields.boolean('Multi Currency Compensation', help='Fields with internal purpose only that depicts if the compensation is a multi currency one or not')
    }
    _defaults = {
        'period_id': _get_period,
        'partner_id': _get_partner,
        'journal_id': _get_journal,
        'currency_id': _get_currency,
        'narration': _get_narration,
        'state': 'draft',
        'name': '',
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.compensation', context=c),
    }

    def onchange_journal_compensation(self, cr, uid, ids, line_ids=False, partner_id=False, journal_id=False, company_id=False, context=None):
        """price
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        default = {
            'value': {},
        }

        if not partner_id or not journal_id:
            return default

        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        vals = self.onchange_journal(
            cr, uid, ids, journal_id, line_ids, partner_id, company_id, context)
        default['value'].update(vals.get('value'))

        return default

    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, currency_id, date, context=None):
        if not journal_id:
            return {}
        if context is None:
            context = {}
        res = {
            'value': {},
        }
        # TODO: comment me and use me directly in the sales/purchases views
        ctx = context.copy()
        # not passing the payment_rate currency and the payment_rate in the
        # context but it's ok because they are reset in recompute_payment_rate
        ctx.update({'date': date})
        vals = self.recompute_compensation_lines(
            cr, uid, ids, partner_id, journal_id, currency_id, date, context=ctx)
        for key in vals.keys():
            res[key].update(vals[key])
        return res

    def recompute_compensation_lines(self, cr, uid, ids, partner_id, journal_id, currency_id, date, context=None):
        """
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        def _remove_noise_in_o2m():
            """if the line is partially reconciled, then we must pay attention to display it only once and
                in the good o2m.
                This function returns True if the line is considered as noise and should not be displayed
            """
            if line.reconcile_partial_id:
                if currency_id == line.currency_id.id:
                    if line.amount_residual_currency <= 0:
                        return True
                else:
                    if line.amount_residual <= 0:
                        return True
            return False

        if context is None:
            context = {}
        context_multi_currency = context.copy()

        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
        line_pool = self.pool.get('account.compensation.line')

        # set default values
        default = {
            'value': {'line_dr_ids': [], 'line_cr_ids': [], 'pre_line': False},
        }

        # drop existing lines
        line_ids = ids and line_pool.search(
            cr, uid, [('compensation_id', '=', ids[0])])
        for line in line_pool.browse(cr, uid, line_ids, context=context):
            if line.type == 'cr':
                default['value']['line_cr_ids'].append((2, line.id))
            else:
                default['value']['line_dr_ids'].append((2, line.id))

        if not partner_id or not journal_id:
            return default

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        currency_id = currency_id or journal.company_id.currency_id.id

        total_credit = 0.0
        total_debit = 0.0
        account_type = None
        ids = move_line_pool.search(cr, uid, [('state', '=', 'valid'), ('account_id.reconcile', '=', True), (
            'reconcile_id', '=', False), ('partner_id', '=', partner_id)], context=context)
        company_currency = journal.company_id.currency_id.id
        move_lines_found = []

        # order the lines by most old first
        ids.reverse()
        account_move_lines = move_line_pool.browse(
            cr, uid, ids, context=context)

        # compensation line creation
        for line in account_move_lines:

            if _remove_noise_in_o2m():
                continue

            if line.currency_id and currency_id == line.currency_id.id:
                amount_original = abs(line.amount_currency)
                amount_unreconciled = abs(line.amount_residual_currency)
            else:
                # always use the amount booked in the company currency as the
                # basis of the conversion into the compensation currency
                amount_original = currency_pool.compute(
                    cr, uid, company_currency, currency_id, line.credit or line.debit or 0.0, context=context_multi_currency)
                amount_unreconciled = currency_pool.compute(cr, uid, company_currency, currency_id, abs(
                    line.amount_residual), context=context_multi_currency)
            line_currency_id = line.currency_id and line.currency_id.id or company_currency
            rs = {
                'name': line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id': line.id,
                'account_id': line.account_id.id,
                'amount_original': amount_original,
                'amount': (line.id in move_lines_found) and amount_unreconciled or 0.0,
                'date_original': line.date,
                'date_due': line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
                'currency_id': line_currency_id,
            }
            if rs['amount_unreconciled'] == rs['amount']:
                rs['reconcile'] = True

            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)
        return default

    def onchange_date(self, cr, uid, ids, date, currency_id, company_id, context=None):
        """
        @param date: latest value from user input for field date
        @param args: other arguments
        @param context: context arguments, like lang, time zone
        @return: Returns a dict which contains new values, and context
        """
        if context is None:
            context = {}
        res = {'value': {}}
        # set the period of the compensation
        period_pool = self.pool.get('account.period')
        currency_obj = self.pool.get('res.currency')
        ctx = context.copy()
        ctx.update(
            {'company_id': company_id, 'account_period_prefer_normal': True})
        compensation_currency_id = currency_id or self.pool.get(
            'res.company').browse(cr, uid, company_id, context=ctx).currency_id.id
        pids = period_pool.find(cr, uid, date, context=ctx)
        if pids:
            res['value'].update({'period_id': pids[0]})
        return res

    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, partner_id, date, company_id, context=None):
        if context is None:
            context = {}
        if not journal_id:
            return False
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)

        vals = {'value': {}}
        if journal.currency:
            currency_id = journal.currency.id
        else:
            currency_id = journal.company_id.currency_id.id

        period_id = self.pool['account.period'].find(
            cr, uid, context=dict(context, company_id=company_id))
        vals['value'].update({
            'currency_id': currency_id,
            'period_id': period_id
        })
        if partner_id:
            res = self.onchange_partner_id(
                cr, uid, ids, partner_id, journal_id, currency_id, date, context)
            for key in res.keys():
                vals[key].update(res[key])
        return vals

    def onchange_company(self, cr, uid, ids, partner_id, journal_id, currency_id, company_id, context=None):
        """
        If the company changes, check that the journal is in the right company.
        If not, fetch a new journal.
        """
        journal_pool = self.pool['account.journal']
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        if journal.company_id.id != company_id:
            # can not guess type of journal, better remove it
            return {'value': {'journal_id': False}}
        return {}

    def button_proforma_compensation(self, cr, uid, ids, context=None):
        self.signal_workflow(cr, uid, ids, 'proforma_compensation')
        return {'type': 'ir.actions.act_window_close'}

    def proforma_compensation(self, cr, uid, ids, context=None):
        self.action_move_line_create(cr, uid, ids, context=context)
        return True

    def action_cancel_draft(self, cr, uid, ids, context=None):
        self.create_workflow(cr, uid, ids)
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def cancel_compensation(self, cr, uid, ids, context=None):
        reconcile_pool = self.pool.get('account.move.reconcile')
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        for compensation in self.browse(cr, uid, ids, context=context):
            # refresh to make sure you don't unlink an already removed move
            compensation.refresh()
            for line in compensation.move_ids:
                # refresh to make sure you don't unreconcile an already
                # unreconciled entry
                line.refresh()
                if line.reconcile_id:
                    move_lines = [
                        move_line.id for move_line in line.reconcile_id.line_id]
                    move_lines.remove(line.id)
                    reconcile_pool.unlink(cr, uid, [line.reconcile_id.id])
                    if len(move_lines) >= 2:
                        move_line_pool.reconcile_partial(
                            cr, uid, move_lines, 'auto', context=context)
                if line.reconcile_partial_id:
                    move_lines = [
                        move_line.id for move_line in line.reconcile_partial_id.line_partial_ids]
                    move_lines.remove(line.id)
                    reconcile_pool.unlink(
                        cr, uid, [line.reconcile_partial_id.id])
                    if len(move_lines) >= 2:
                        move_line_pool.reconcile_partial(
                            cr, uid, move_lines, 'auto', context=context)
            if compensation.move_id:
                move_pool.button_cancel(cr, uid, [compensation.move_id.id])
                move_pool.unlink(cr, uid, [compensation.move_id.id])
        res = {
            'state': 'cancel',
            'move_id': False,
        }
        self.write(cr, uid, ids, res)
        return True

    def unlink(self, cr, uid, ids, context=None):
        for t in self.read(cr, uid, ids, ['state'], context=context):
            if t['state'] not in ('draft', 'cancel'):
                raise osv.except_osv(_('Invalid Action!'), _(
                    'Cannot delete compensation(s) which are already opened or paid.'))
        return super(account_compensation, self).unlink(cr, uid, ids, context=context)

    def _sel_context(self, cr, uid, compensation_id, context=None):
        """
        Select the context to use accordingly if it needs to be multicurrency or not.

        :param compensation_id: Id of the actual compensation
        :return: The returned context will be the same as given in parameter if the compensation currency is the same
                 than the company currency, otherwise it's a copy of the parameter with an extra key 'date' containing
                 the date of the compensation.
        :rtype: dict
        """
        company_currency = self._get_company_currency(
            cr, uid, compensation_id, context)
        current_currency = self._get_current_currency(
            cr, uid, compensation_id, context)
        if current_currency != company_currency:
            context_multi_currency = context.copy()
            compensation = self.pool.get('account.compensation').browse(
                cr, uid, compensation_id, context)
            context_multi_currency.update({'date': compensation.date})
            return context_multi_currency
        return context

    def account_move_get(self, cr, uid, compensation_id, context=None):
        '''
        This method prepare the creation of the account move related to the given compensation.

        :param compensation_id: Id of compensation for which we are creating account_move.
        :return: mapping between fieldname and value of account move to create
        :rtype: dict
        '''
        seq_obj = self.pool.get('ir.sequence')
        compensation = self.pool.get('account.compensation').browse(
            cr, uid, compensation_id, context)
        if compensation.number:
            name = compensation.number
        elif compensation.journal_id.sequence_id:
            if not compensation.journal_id.sequence_id.active:
                raise osv.except_osv(_('Configuration Error !'),
                                     _('Please activate the sequence of selected journal !'))
            c = dict(context)
            c.update(
                {'fiscalyear_id': compensation.period_id.fiscalyear_id.id})
            name = seq_obj.next_by_id(
                cr, uid, compensation.journal_id.sequence_id.id, context=c)
        else:
            raise osv.except_osv(_('Error!'),
                                 _('Please define a sequence on the journal.'))
        move = {
            'name': name,
            'journal_id': compensation.journal_id.id,
            'narration': compensation.narration,
            'date': compensation.date,
            'ref': name.replace('/', ''),
            'period_id': compensation.period_id.id,
        }
        return move

    def _get_exchange_lines(self, cr, uid, line, move_id, amount_residual, company_currency, current_currency, context=None):
        '''
        Prepare the two lines in company currency due to currency rate difference.

        :param line: browse record of the compensation.line for which we want to create currency rate difference accounting
            entries
        :param move_id: Account move wher the move lines will be.
        :param amount_residual: Amount to be posted.
        :param company_currency: id of currency of the company to which the compensation belong
        :param current_currency: id of currency of the compensation
        :return: the account move line and its counterpart to create, depicted as mapping between fieldname and value
        :rtype: tuple of dict
        '''
        if amount_residual > 0:
            account_id = line.compensation_id.company_id.expense_currency_exchange_account_id
            if not account_id:
                model, action_id = self.pool['ir.model.data'].get_object_reference(
                    cr, uid, 'account', 'action_account_form')
                msg = _(
                    "You should configure the 'Loss Exchange Rate Account' to manage automatically the booking of accounting entries related to differences between exchange rates.")
                raise openerp.exceptions.RedirectWarning(
                    msg, action_id, _('Go to the configuration panel'))
        else:
            account_id = line.compensation_id.company_id.income_currency_exchange_account_id
            if not account_id:
                model, action_id = self.pool['ir.model.data'].get_object_reference(
                    cr, uid, 'account', 'action_account_form')
                msg = _(
                    "You should configure the 'Gain Exchange Rate Account' to manage automatically the booking of accounting entries related to differences between exchange rates.")
                raise openerp.exceptions.RedirectWarning(
                    msg, action_id, _('Go to the configuration panel'))
        # Even if the amount_currency is never filled, we need to pass the foreign currency because otherwise
        # the receivable/payable account may have a secondary currency, which
        # render this field mandatory
        if line.account_id.currency_id:
            account_currency_id = line.account_id.currency_id.id
        else:
            account_currency_id = company_currency != current_currency and current_currency or False
        move_line = {
            'journal_id': line.compensation_id.journal_id.id,
            'period_id': line.compensation_id.period_id.id,
            'name': _('change') + ': ' + (line.name or '/'),
            'account_id': line.account_id.id,
            'move_id': move_id,
            'partner_id': line.compensation_id.partner_id.id,
            'currency_id': account_currency_id,
            'amount_currency': 0.0,
            'quantity': 1,
            'credit': amount_residual > 0 and amount_residual or 0.0,
            'debit': amount_residual < 0 and -amount_residual or 0.0,
            'date': line.compensation_id.date,
        }
        move_line_counterpart = {
            'journal_id': line.compensation_id.journal_id.id,
            'period_id': line.compensation_id.period_id.id,
            'name': _('change') + ': ' + (line.name or '/'),
            'account_id': account_id.id,
            'move_id': move_id,
            'amount_currency': 0.0,
            'partner_id': line.compensation_id.partner_id.id,
            'currency_id': account_currency_id,
            'quantity': 1,
            'debit': amount_residual > 0 and amount_residual or 0.0,
            'credit': amount_residual < 0 and -amount_residual or 0.0,
            'date': line.compensation_id.date,
        }
        return (move_line, move_line_counterpart)

    def _convert_amount(self, cr, uid, amount, compensation_id, context=None):
        '''
        This function convert the amount given in company currency.

        :param amount: float. The amount to convert
        :param compensation: id of the compensation on which we want the conversion
        :param context: to context to use for the conversion. It may contain the key 'date' set to the compensation date
            field in order to select the good rate to use.
        :return: the amount in the currency of the compensation's company
        :rtype: float
        '''
        if context is None:
            context = {}
        currency_obj = self.pool.get('res.currency')
        compensation = self.browse(cr, uid, compensation_id, context=context)
        return currency_obj.compute(cr, uid, compensation.currency_id.id, compensation.company_id.currency_id.id, amount, context=context)

    def compensation_move_line_create(self, cr, uid, compensation_id, move_id, company_currency, current_currency, context=None):
        '''
        Create one account move line, on the given account move, per compensation line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).

        :param compensation_id: Compensation id what we are working with
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the compensation belong
        :param current_currency: id of currency of the compensation
        :return: Tuple build as (remaining amount not allocated on compensation lines, list of account_move_line created in this method)
        :rtype: tuple(float, list of int)
        '''
        if context is None:
            context = {}
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        rec_lst_ids = []

        date = self.read(
            cr, uid, [compensation_id], ['date'], context=context)[0]['date']
        ctx = context.copy()
        ctx.update({'date': date})
        compensation = self.pool.get('account.compensation').browse(
            cr, uid, compensation_id, context=ctx)
        compensation_currency = compensation.journal_id.currency or compensation.company_id.currency_id
        prec = self.pool.get('decimal.precision').precision_get(
            cr, uid, 'Account')
        for line in compensation.line_ids:
            # create one move line per compensation line where amount is not 0.0
            # AND (second part of the clause) only if the original move line
            # was not having debit = credit = 0 (which is a legal value)
            if not line.amount and not (line.move_line_id and not float_compare(line.move_line_id.debit, line.move_line_id.credit, precision_digits=prec) and not float_compare(line.move_line_id.debit, 0.0, precision_digits=prec)):
                continue
            # convert the amount set on the compensation line into the currency of the compensation's company
            # this calls res_curreny.compute() with the right context, so that
            # it will take either the rate on the compensation if it is
            # relevant or will use the default behaviour
            amount = self._convert_amount(
                cr, uid, line.amount, compensation.id, context=ctx)
            # if the amount encoded in compensation is equal to the amount unreconciled, we need to compute the
            # currency rate difference
            if line.amount == line.amount_unreconciled:
                if not line.move_line_id:
                    raise osv.except_osv(_('Wrong compensation line'), _(
                        "The invoice you are willing to pay is not valid anymore."))
                sign = line.type == 'dr' and -1 or 1
                currency_rate_difference = sign * \
                    (line.move_line_id.amount_residual - amount)
            else:
                currency_rate_difference = 0.0
            move_line = {
                'journal_id': compensation.journal_id.id,
                'period_id': compensation.period_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': compensation.partner_id.id,
                'currency_id': line.move_line_id and (company_currency != line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                'quantity': 1,
                'credit': 0.0,
                'debit': 0.0,
                'date': compensation.date
            }
            if amount < 0:
                amount = -amount
                if line.type == 'dr':
                    line.type = 'cr'
                else:
                    line.type = 'dr'

            if (line.type == 'dr'):
                move_line['debit'] = amount
            else:
                move_line['credit'] = amount

            # compute the amount in foreign currency
            foreign_currency_diff = 0.0
            amount_currency = False
            if line.move_line_id:
                # We want to set it on the account move line as soon as the
                # original line had a foreign currency
                if line.move_line_id.currency_id and line.move_line_id.currency_id.id != company_currency:
                    # we compute the amount in that foreign currency.
                    if line.move_line_id.currency_id.id == current_currency:
                        # if the compensation and the compensation line share
                        # the same currency, there is no computation to do
                        sign = (
                            move_line['debit'] - move_line['credit']) < 0 and -1 or 1
                        amount_currency = sign * (line.amount)
                    else:
                        # if the rate is specified on the compensation, it will be used thanks to the special keys in the context
                        # otherwise we use the rates of the system
                        amount_currency = currency_obj.compute(cr, uid, company_currency, line.move_line_id.currency_id.id, move_line[
                                                               'debit'] - move_line['credit'], context=ctx)
                if line.amount == line.amount_unreconciled:
                    foreign_currency_diff = line.move_line_id.amount_residual_currency - \
                        abs(amount_currency)

            move_line['amount_currency'] = amount_currency
            compensation_line = move_line_obj.create(cr, uid, move_line)
            rec_ids = [compensation_line, line.move_line_id.id]

            if not currency_obj.is_zero(cr, uid, compensation.company_id.currency_id, currency_rate_difference):
                # Change difference entry in company currency
                exch_lines = self._get_exchange_lines(
                    cr, uid, line, move_id, currency_rate_difference, company_currency, current_currency, context=context)
                new_id = move_line_obj.create(cr, uid, exch_lines[0], context)
                move_line_obj.create(cr, uid, exch_lines[1], context)
                rec_ids.append(new_id)

            if line.move_line_id and line.move_line_id.currency_id and not currency_obj.is_zero(cr, uid, line.move_line_id.currency_id, foreign_currency_diff):
                # Change difference entry in compensation currency
                move_line_foreign_currency = {
                    'journal_id': line.compensation_id.journal_id.id,
                    'period_id': line.compensation_id.period_id.id,
                    'name': _('change') + ': ' + (line.name or '/'),
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': line.compensation_id.partner_id.id,
                    'currency_id': line.move_line_id.currency_id.id,
                    'amount_currency': -1 * foreign_currency_diff,
                    'quantity': 1,
                    'credit': 0.0,
                    'debit': 0.0,
                    'date': line.compensation_id.date,
                }
                new_id = move_line_obj.create(
                    cr, uid, move_line_foreign_currency, context=context)
                rec_ids.append(new_id)
            if line.move_line_id.id:
                rec_lst_ids.append(rec_ids)
        return rec_lst_ids

    def _get_company_currency(self, cr, uid, compensation_id, context=None):
        '''
        Get the currency of the actual company.

        :param compensation_id: Id of the compensation what i want to obtain company currency.
        :return: currency id of the company of the compensation
        :rtype: int
        '''
        return self.pool.get('account.compensation').browse(cr, uid, compensation_id, context).journal_id.company_id.currency_id.id

    def _get_current_currency(self, cr, uid, compensation_id, context=None):
        '''
        Get the currency of the compensation.

        :param compensation_id: Id of the compensation what i want to obtain current currency.
        :return: currency id of the compensation
        :rtype: int
        '''
        compensation = self.pool.get('account.compensation').browse(
            cr, uid, compensation_id, context)
        return compensation.currency_id.id or self._get_company_currency(cr, uid, compensation.id, context)

    def action_move_line_create(self, cr, uid, ids, context=None):
        '''
        Confirm the compensations given in ids and create the journal entries for each of them
        '''
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        for compensation in self.browse(cr, uid, ids, context=context):
            local_context = dict(
                context, force_company=compensation.journal_id.company_id.id)
            if compensation.move_id:
                continue
            company_currency = self._get_company_currency(
                cr, uid, compensation.id, context)
            current_currency = self._get_current_currency(
                cr, uid, compensation.id, context)
            # we select the context to use accordingly if it's a multicurrency
            # case or not
            context = self._sel_context(cr, uid, compensation.id, context)
            # But for the operations made by _convert_amount, we always need to
            # give the date in the context
            ctx = context.copy()
            ctx.update({'date': compensation.date})
            # Create the account move record.
            move_id = move_pool.create(cr, uid, self.account_move_get(
                cr, uid, compensation.id, context=context), context=context)
            # Get the name of the account_move just created
            name = move_pool.browse(cr, uid, move_id, context=context).name
            # Create one move line per compensation line where amount is not
            # 0.0
            rec_list_ids = self.compensation_move_line_create(
                cr, uid, compensation.id, move_id, company_currency, current_currency, context)

            # We post the compensation.
            self.write(cr, uid, [compensation.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            if compensation.journal_id.entry_posted:
                move_pool.post(cr, uid, [move_id], context={})
            # We automatically reconcile the account move lines.
            reconcile = False
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    reconcile = move_line_pool.reconcile_partial(
                        cr, uid, rec_ids, 'auto')
        return True


class account_compensation_line(osv.osv):
    _name = 'account.compensation.line'
    _description = 'Compensation Lines'
    _order = "move_line_id"

    # If the payment is in the same currency than the invoice, we keep the same amount
    # Otherwise, we compute from invoice currency to payment currency
    def _compute_balance(self, cr, uid, ids, name, args, context=None):
        currency_pool = self.pool.get('res.currency')
        rs_data = {}
        for line in self.browse(cr, uid, ids, context=context):
            ctx = context.copy()
            ctx.update({'date': line.compensation_id.date})
            res = {}
            company_currency = line.compensation_id.journal_id.company_id.currency_id.id
            compensation_currency = line.compensation_id.currency_id and line.compensation_id.currency_id.id or company_currency
            move_line = line.move_line_id or False

            if not move_line:
                res['amount_original'] = 0.0
                res['amount_unreconciled'] = 0.0
            elif move_line.currency_id and compensation_currency == move_line.currency_id.id:
                res['amount_original'] = abs(move_line.amount_currency)
                res['amount_unreconciled'] = abs(
                    move_line.amount_residual_currency)
            else:
                # always use the amount booked in the company currency as the
                # basis of the conversion into the compensation currency
                res['amount_original'] = currency_pool.compute(
                    cr, uid, company_currency, compensation_currency, move_line.credit or move_line.debit or 0.0, context=ctx)
                res['amount_unreconciled'] = currency_pool.compute(
                    cr, uid, company_currency, compensation_currency, abs(move_line.amount_residual), context=ctx)

            rs_data[line.id] = res
        return rs_data

    def _currency_id(self, cr, uid, ids, name, args, context=None):
        '''
        This function returns the currency id of a compensation line. It's either the currency of the
        associated move line (if any) or the currency of the compensation or the company currency.
        '''
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            move_line = line.move_line_id
            if move_line:
                res[
                    line.id] = move_line.currency_id and move_line.currency_id.id or move_line.company_id.currency_id.id
            else:
                res[
                    line.id] = line.compensation_id.currency_id and line.compensation_id.currency_id.id or line.compensation_id.company_id.currency_id.id
        return res

    _columns = {
        'compensation_id': fields.many2one('account.compensation', 'Compensation', required=1, ondelete='cascade'),
        'name': fields.char('Description',),
        'account_id': fields.many2one('account.account', 'Account', required=True),
        'partner_id': fields.related('compensation_id', 'partner_id', type='many2one', relation='res.partner', string='Partner'),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account')),
        'reconcile': fields.boolean('Full Reconcile'),
        'type': fields.selection([('dr', 'Debit'), ('cr', 'Credit')], 'Dr/Cr'),
        'move_line_id': fields.many2one('account.move.line', 'Journal Item', copy=False),
        'date_original': fields.related('move_line_id', 'date', type='date', relation='account.move.line', string='Date', readonly=1),
        'date_due': fields.related('move_line_id', 'date_maturity', type='date', relation='account.move.line', string='Due Date', readonly=1),
        'amount_original': fields.function(_compute_balance, multi='dc', type='float', string='Original Amount', store=True, digits_compute=dp.get_precision('Account')),
        'amount_unreconciled': fields.function(_compute_balance, multi='dc', type='float', string='Open Balance', store=True, digits_compute=dp.get_precision('Account')),
        'company_id': fields.related('compensation_id', 'company_id', relation='res.company', type='many2one', string='Company', store=True, readonly=True),
        'currency_id': fields.function(_currency_id, string='Currency', type='many2one', relation='res.currency', readonly=True),
    }
    _defaults = {
        'name': '',
    }

    def onchange_reconcile(self, cr, uid, ids, reconcile, amount, amount_unreconciled, context=None):
        vals = {'amount': 0.0}
        if reconcile:
            vals = {'amount': amount_unreconciled}
        return {'value': vals}

    def onchange_amount(self, cr, uid, ids, amount, amount_unreconciled, context=None):
        vals = {}
        if amount:
            vals['reconcile'] = (amount == amount_unreconciled)
        return {'value': vals}

    def onchange_move_line_id(self, cr, user, ids, move_line_id, context=None):
        """
        Returns a dict that contains new values and context

        @param move_line_id: latest value from user input for field move_line_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        res = {}
        move_line_pool = self.pool.get('account.move.line')
        if move_line_id:
            move_line = move_line_pool.browse(
                cr, user, move_line_id, context=context)
            if move_line.credit:
                ttype = 'dr'
            else:
                ttype = 'cr'
            res.update({
                'account_id': move_line.account_id.id,
                'type': ttype,
                'currency_id': move_line.currency_id and move_line.currency_id.id or move_line.company_id.currency_id.id,
            })
        return {
            'value': res,
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
