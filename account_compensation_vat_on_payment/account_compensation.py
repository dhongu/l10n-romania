# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Domsense s.r.l. (<http://www.domsense.com>).
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
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
# from openerp.tools import float_compare
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class account_compensation(osv.Model):
    _inherit = "account.compensation"

    def is_vat_on_payment(self, compensation):
        vat_on_p = 0
        for line in compensation.line_ids:
            if line.amount:
                if line.move_line_id and line.move_line_id.invoice and line.move_line_id.invoice.vat_on_payment:
                    vat_on_p += 1
        return vat_on_p

    def action_move_line_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        inv_pool = self.pool.get('account.invoice')
        journal_pool = self.pool.get('account.journal')
        move_line_pool = self.pool.get('account.move.line')
        move_pool = self.pool.get('account.move')
        account_obj = self.pool.get('account.account')
        tax_obj = self.pool.get('account.tax')
        currency_obj = self.pool.get('res.currency')
        res = False
        for compensation in self.browse(cr, uid, ids, context):
            entry_posted = compensation.journal_id.entry_posted
            # disable the 'skip draft state' option because "mixed" entry
            # (shadow + real) won't pass validation. Anyway every entry will be
            # posted later (if 'entry_posted' is enabled)
            if entry_posted:
                journal_pool.write(
                    cr, uid, compensation.journal_id.id, {'entry_posted': False})
            res = super(account_compensation, self).action_move_line_create(
                cr, uid, [compensation.id], context)
            # because 'move_id' has been updated by 'action_move_line_create'
            compensation.refresh()
            if entry_posted:
                journal_pool.write(
                    cr, uid, compensation.journal_id.id, {'entry_posted': True})
            if self.is_vat_on_payment(compensation):
                lines_to_create = []
                amounts_by_invoice = self.allocated_amounts_grouped_by_invoice(
                    cr, uid, compensation, context)
                for inv_id in amounts_by_invoice:
                    invoice = inv_pool.browse(cr, uid, inv_id, context)
                    for acc_move_line in invoice.move_id.line_id:
                        if acc_move_line.real_tax_code_id:
                            # compute the VAT or base line proportionally to
                            # the paid amount
                            new_line_amount = currency_obj.round(cr, uid, compensation.company_id.currency_id, ((amounts_by_invoice[invoice.id][
                                                                 'allocated'] + amounts_by_invoice[invoice.id]['write-off']) / amounts_by_invoice[invoice.id]['total']) * acc_move_line.tax_amount)
                            acc = acc_move_line.real_account_id and acc_move_line.real_account_id.id or acc_move_line.account_id.id
                            # prepare the real move line
                            vals = {
                                'name': invoice.number + ' - ' + acc_move_line.name,
                                'account_id': acc,
                                'credit': acc_move_line.credit and new_line_amount or 0.0,
                                'debit': acc_move_line.debit and new_line_amount or 0.0,
                                'date': compensation.date,
                                'partner_id': acc_move_line.partner_id and acc_move_line.partner_id.id or False,
                                'tax_code_id': acc_move_line.real_tax_code_id.id,
                                'tax_amount': new_line_amount
                            }
                            if acc_move_line.product_id:
                                vals['debit'] = vals['credit'] = 0.00
                            lines_to_create.append(vals)
                            # prepare the shadow move line
                            vals = {
                                'name': invoice.number + ' - ' + acc_move_line.name,
                                'account_id': acc_move_line.account_id.id,
                                'credit': acc_move_line.debit and new_line_amount or 0.0,
                                'debit': acc_move_line.credit and new_line_amount or 0.0,
                                'date': compensation.date,
                                'partner_id': acc_move_line.partner_id and acc_move_line.partner_id.id or False,
                                'tax_code_id': acc_move_line.tax_code_id.id,
                                'tax_amount': -new_line_amount
                            }
                            if acc_move_line.product_id:
                                vals['debit'] = vals['credit'] = 0.00
                            lines_to_create.append(vals)
                for line_to_create in lines_to_create:
                    line_to_create['move_id'] = compensation.move_id.id
                    move_line_pool.create(cr, uid, line_to_create, context)
            self.balance_move(cr, uid, compensation.move_id.id, context)
            move_pool.post(cr, uid, [compensation.move_id.id], context=context)
        return res

    def balance_move(self, cr, uid, move_id, context=None):
        currency_obj = self.pool.get('res.currency')
        move = self.pool.get('account.move').browse(cr, uid, move_id, context)
        amount = 0.0
        for line in move.line_id:
            amount += line.debit - line.credit
        amount = currency_obj.round(
            cr, uid, move.company_id.currency_id, amount)
        # check if balance differs for more than 1 decimal according to account
        # decimal precision
        if abs(amount * 10 ** dp.get_precision('Account')(cr)[1]) > 1:
            raise osv.except_osv(_('Error'), _(
                'The generated payment entry is unbalanced for more than 1 decimal'))
        if not currency_obj.is_zero(cr, uid, move.company_id.currency_id, amount):
            for line in move.line_id:
                # adjust the first move line that's not receivable, payable or
                # liquidity
                if line.account_id.type != 'receivable' and line.account_id.type != 'payable' and line.account_id.type != 'liquidity':
                    if line.credit:
                        line.write({
                            'credit': line.credit + amount,
                        }, update_check=False)
                    elif line.debit:
                        line.write({
                            'debit': line.debit - amount,
                        }, update_check=False)
                    if line.tax_amount:
                        line.write({
                            'tax_amount': line.tax_amount + amount,
                        }, update_check=False)
                    break
        return amount

    def get_invoice_total(self, invoice):
        res = 0.0
        for inv_move_line in invoice.move_id.line_id:
            if inv_move_line.account_id.id == invoice.account_id.id:
                # can both be presents?
                res += inv_move_line.debit or inv_move_line.credit
        return res

    def allocated_amounts_grouped_by_invoice(self, cr, uid, compensation, context=None):
        '''

        this method builds a dictionary in the following form

        {
            first_invoice_id: {
                'allocated': 120.0,
                'total': 120.0,
                'write-off': 20.0,
                }
            second_invoice_id: {
                'allocated': 50.0,
                'total': 100.0,
                'write-off': 0.0,
                }
        }

        every amout is expressed in company currency.

        In order to compute cashed amount correctly, write-off will be subtract to reconciled amount.
        If more than one invoice is paid with this compensation, we distribute write-off equally (if allowed)

        '''
        res = {}
        company_currency = super(account_compensation, self)._get_company_currency(
            cr, uid, compensation.id, context)
        current_currency = super(account_compensation, self)._get_current_currency(
            cr, uid, compensation.id, context)
        for line in compensation.line_ids:
            if line.amount and line.move_line_id and line.move_line_id.invoice:
                if line.move_line_id.invoice.id not in res:
                    res[line.move_line_id.invoice.id] = {
                        'allocated': 0.0,
                        'total': 0.0,
                        'write-off': 0.0, }
                current_amount = line.amount
                if company_currency != current_currency:
                    current_amount = super(account_compensation, self)._convert_amount(
                        cr, uid, line.amount, compensation.id, context)
                res[line.move_line_id.invoice.id][
                    'allocated'] += current_amount
                res[line.move_line_id.invoice.id][
                    'total'] = self.get_invoice_total(line.move_line_id.invoice)
        return res
