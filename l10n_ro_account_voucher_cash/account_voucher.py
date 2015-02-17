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


from lxml import etree

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare
import openerp

import time
from datetime import datetime, timedelta, date


class account_bank_statement_line(osv.osv):
    _name = "account.bank.statement.line"
    _inherit = "account.bank.statement.line"

    _columns = {
        'voucher_id': fields.many2one(
            'account.voucher', 'Voucher', ondelete='restrict'),
    }


class account_journal(osv.osv):
    _name = "account.journal"
    _inherit = "account.journal"

    _columns = {
        "receipts_sequence_id": fields.many2one(
            'ir.sequence', 'Voucher Sequence',
            help="""This field contains the information related to the
            numbering of the vouchers (receipts) of this journal."""),
    }


class account_voucher(osv.osv):
    _name = 'account.voucher'
    _inherit = 'account.voucher'

    def account_move_get(self, cr, uid, voucher_id, context=None):
        '''
        This method prepare the creation of the account move related to the
        given voucher.

        :param voucher_id: Id of voucher for which we are creating
        account_move.
        :return: mapping between fieldname and value of account move to create
        :rtype: dict
        '''
        seq_obj = self.pool.get('ir.sequence')
        voucher = self.pool.get('account.voucher').browse(
            cr, uid, voucher_id, context)
        if not voucher.number and voucher.journal_id.type == 'cash':
            if voucher.type == 'receipt':
                if voucher.journal_id.receipts_sequence_id:
                    if not voucher.journal_id.receipts_sequence_id.active:
                        raise osv.except_osv(_('Configuration Error !'),
                                             _('Please activate the receipts sequence of selected journal !'))
                    c = dict(context)
                    c.update(
                        {'fiscalyear_id': voucher.period_id.fiscalyear_id.id})
                    if not voucher.number:
                        number = seq_obj.next_by_id(
                            cr, uid,
                            voucher.journal_id.receipts_sequence_id.id, context=c)
                        self.write(
                            cr, uid, [voucher_id],
                            {'number': number, 'name': number})
                else:
                    raise osv.except_osv(_('Error!'),
                                         _('Please define a receipts sequence on the journal.'))
            else:
                if voucher.reference:
                    self.write(
                        cr, uid, [voucher_id],
                        {
                            'number': voucher.reference,
                            'name': voucher.reference
                        })
            voucher.refresh()
        return super(account_voucher, self).account_move_get(cr, uid, voucher_id, context=context)

    def action_move_line_create(self, cr, uid, ids, context=None):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        res = super(account_voucher, self).action_move_line_create(
            cr, uid, ids, context=context)
        # Create line in cash statement for voucher posted in cash journals.
        statement_obj = self.pool['account.bank.statement']
        statement_line_obj = self.pool['account.bank.statement.line']
        if context is None:
            context = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.journal_id.type == 'cash':
                bank_line = self.pool.get('account.bank.statement.line').search(
                    cr, uid, [('voucher_id', '=', voucher.id)])
                if not bank_line:
                    if voucher.type in ('sale', 'receipt'):
                        account_id = voucher.partner_id.property_account_receivable and voucher.partner_id.property_account_receivable.id
                        if not account_id:
                            account_id = voucher.company_id.property_customer_advance_account_id and voucher.company_id.property_customer_advance_account_id.id
                    else:
                        account_id = voucher.partner_id.property_account_payable and voucher.partner_id.property_account_payable.id
                        if not account_id:
                            account_id = voucher.company_id.property_supplier_advance_account_id and voucher.company_id.property_supplier_advance_account_id.id
                    statement_id = statement_obj.search(
                        cr, uid, [('journal_id', '=', voucher.journal_id.id), ('date', '=', voucher.date)])
                    if not statement_id:
                        vals = {
                            'journal_id': voucher.journal_id.id,
                            'state': 'draft',
                            'date': voucher.date,
                        }
                        statement_id = statement_obj.create(cr, uid, vals)
                        self.pool.get('account.bank.statement').onchange_journal_id(
                            cr, uid, [statement_id], voucher.journal_id.id, context=context)
                        self.pool.get('account.bank.statement').button_open(
                            cr, uid, [statement_id], context=context)
                    else:
                        statement_id = statement_id[0]
                    statement = statement_obj.browse(cr, uid, statement_id)
                    if statement.state != 'open':
                        raise osv.except_osv(_('Error!'), _('The cash statement of journal %s from date is not in open state, please open it \n'
                                                            'to create the line in  it "%s".') % (voucher.journal_id.name, voucher.date))
                    args = {
                        'amount': voucher.type == 'receipt' and voucher.amount or -voucher.amount,
                        'date':  voucher.date,
                        'name': str(voucher.number),
                        'account_id': account_id or False,
                        'partner_id': voucher.partner_id and voucher.partner_id.id or None,
                        'statement_id': statement.id,
                        'journal_id': statement.journal_id.id,
                        'ref': str(voucher.number),
                        'voucher_id': voucher.id,
                        'journal_entry_id': voucher.move_id.id,
                    }
                    statement_line_obj.create(cr, uid, args, context=context)
        return res
