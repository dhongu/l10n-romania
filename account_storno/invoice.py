# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: account_storno
#    Author: Goran Kliska
#    mail:   gkliskaATgmail.com
#    Copyright (C) 2013- Slobodni programi d.o.o., Zagreb
#    Contributions:
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


import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp


class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(account_invoice, self).line_get_convert(line, part, date)
        ctx = dict(self._context)
        if self.journal_id.posting_policy == 'storno':
            credit = debit = 0.0
            if self.type in ('out_invoice', 'out_refund'):
                if line.get('type', 'src') == 'dest':
                    # for OUT_invoice dest (tot. amount goes to debit)
                    debit = line['price']
                else:  # in('src','tax')
                    credit = line['price'] * (-1)
            else:  # in ('in_invoice', 'in_refund')
                if line.get('type', 'src') == 'dest':
                    credit = line['price'] * (-1)
                else:
                    if line.get('tax_amount',0) != 0 and line['tax_amount']<0 and line['price']>0 and line['quantity']>0:
                        credit = line['price'] * (-1)
                    elif line.get('tax_amount',0) != 0 and line['tax_amount']>0 and line['price']<0 and line['quantity']>0:
                        credit = line['price'] * (-1)
                    else:
                        debit = line['price']

            res['debit'] = debit
            res['credit'] = credit
            if self and self.currency_id.id != self.company_id.currency_id.id:
                # KGB tired, alternative implementation with pg trigger
                if abs(res['tax_amount']) > 0.00:
                    res['tax_amount'] = res['debit'] + res['credit']
        return res

    def group_lines(self, iml, line):
        """Merge account move lines (and hence analytic lines) if invoice line hashcodes are equals"""
        if self.journal_id.group_invoice_lines:
            if self.journal_id.posting_policy == 'contra':
                return super(account_invoice, self).group_lines(iml, line)
            if self.journal_id.posting_policy == 'storno':
                line2 = {}
                for x, y, l in line:
                    hash = self.inv_line_characteristic_hashcode(l)
                    side = abs(l['credit']) > 0.0 and 'credit' or 'debit'
                    if l['credit'] == 0.00 and l['debit'] == 0:
                        tmp_c = '-'.join((hash, 'credit'))
                        side = (tmp_c in line2) and 'credit' or side
                    tmp = '-'.join((hash, side))
                    if tmp in line2:
                        line2[tmp]['debit'] += l['debit'] or 0.0
                        line2[tmp]['credit'] += l['credit'] or 0.00
                        line2[tmp]['tax_amount'] += l['tax_amount']
                        line2[tmp]['analytic_lines'] += l['analytic_lines']
                        line2[tmp]['amount_currency'] += l['amount_currency']
                        line2[tmp]['quantity'] += l['quantity']
                    else:
                        line2[tmp] = l
                line = []
                for key, val in line2.items():
                    line.append((0, 0, val))
        return line
        
    @api.one
    @api.depends(
        'state', 'currency_id', 'invoice_line.price_subtotal',
        'move_id.line_id.account_id.type',
        'move_id.line_id.amount_residual',
        # Fixes the fact that move_id.line_id.amount_residual, being not stored and old API, doesn't trigger recomputation
        'move_id.line_id.reconcile_id',
        'move_id.line_id.amount_residual_currency',
        'move_id.line_id.currency_id',
        'move_id.line_id.reconcile_partial_id.line_partial_ids.invoice.type',
    )
    # An invoice's residual amount is the sum of its unreconciled move lines and,
    # for partially reconciled move lines, their residual amount divided by the
    # number of times this reconciliation is used in an invoice (so we split
    # the residual amount between all invoice)
    def _compute_residual(self):
        self.residual = 0.0
        # Each partial reconciliation is considered only once for each invoice it appears into,
        # and its residual amount is divided by this number of invoices
        partial_reconciliations_done = []
        residual = 0.00
        for line in self.sudo().move_id.line_id:
            if line.account_id.id == self.account_id.id:
                # Get the correct line residual amount
                if line.currency_id == self.currency_id:
                    line_amount = line.currency_id and line.amount_residual_currency or line.amount_residual
                else:
                    from_currency = line.company_id.currency_id.with_context(date=line.date)
                    line_amount = from_currency.compute(line.amount_residual, self.currency_id)
                # For partially reconciled lines, split the residual amount
                if line.reconcile_partial_id:
                    partial_reconciliation_invoices = set()
                    for pline in line.reconcile_partial_id.line_partial_ids:
                        if pline.invoice and self.type == pline.invoice.type:
                            partial_reconciliation_invoices.update([pline.invoice.id])
                    line_amount = self.currency_id.round(line_amount / len(partial_reconciliation_invoices))
                    partial_reconciliations_done.append(line.reconcile_partial_id.id)
                residual += line_amount
        self.residual = residual
