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
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, api


class product_category(osv.Model):
    _name = "product.category"
    _inherit = "product.category"

    _columns = {
        'property_account_creditor_price_difference_categ': fields.property(
            type='many2one',
            relation='account.account',
            string="Price Difference Account",
            help="This account will be used to value price difference between purchase price and cost price."),
    }


class product_template(osv.Model):
    _name = "product.template"
    _inherit = "product.template"

    _columns = {
        'property_account_creditor_price_difference': fields.property(
            type='many2one',
            relation='account.account',
            string="Price Difference Account",
            help="This account will be used to value price difference between purchase price and cost price."),
    }

    def get_product_accounts(self, cr, uid, product_id, context=None):
        """ To get the stock input account, stock output account and stock journal related to product.
        @param product_id: product id
        @return: dictionary which contains information regarding stock input account, stock output account and stock journal
        """
        if context is None:
            context = {}
        product_obj = self.browse(cr, uid, product_id, context=context)

        stock_input_acc = product_obj.property_stock_account_input and product_obj.property_stock_account_input.id or False
        if not stock_input_acc:
            stock_input_acc = product_obj.categ_id.property_stock_account_input_categ and product_obj.categ_id.property_stock_account_input_categ.id or False

        stock_output_acc = product_obj.property_stock_account_output and product_obj.property_stock_account_output.id or False
        if not stock_output_acc:
            stock_output_acc = product_obj.categ_id.property_stock_account_output_categ and product_obj.categ_id.property_stock_account_output_categ.id or False

        journal_id = product_obj.categ_id.property_stock_journal and product_obj.categ_id.property_stock_journal.id or False
        account_valuation = product_obj.categ_id.property_stock_valuation_account_id and product_obj.categ_id.property_stock_valuation_account_id.id or False

        return {
            'stock_account_input': stock_input_acc,
            'stock_account_output': stock_output_acc,
            'stock_journal': journal_id,
            'property_stock_valuation_account_id': account_valuation
        }

# ----------------------------------------------------------
# Stock Location
# ----------------------------------------------------------


class stock_location(osv.Model):
    _name = "stock.location"
    _inherit = "stock.location"

    _columns = {
        'usage': fields.selection([
            ('supplier', 'Supplier Location'),
            ('view', 'View'),
            ('internal', 'Internal Location'),
            ('customer', 'Customer Location'),
            ('inventory', 'Inventory'),
            ('procurement', 'Procurement'),
            ('production', 'Production'),
            ('transit', 'Transit Location'),
            ('usage_giving', 'Usage Giving'),
            ('consume', 'Consume')],
            'Location Type', required=True,
            help="""* Supplier Location: Virtual location representing the source location for products coming from your suppliers
                       \n* View: Virtual location used to create a hierarchical structures for your warehouse, aggregating its child locations ; can't directly contain products
                       \n* Internal Location: Physical locations inside your own warehouses,
                       \n* Customer Location: Virtual location representing the destination location for products sent to your customers
                       \n* Inventory: Virtual location serving as counterpart for inventory operations used to correct stock levels (Physical inventories)
                       \n* Procurement: Virtual location serving as temporary counterpart for procurement operations when the source (supplier or production) is not known yet. This location should be empty when the procurement scheduler has finished running.
                       \n* Production: Virtual counterpart location for production operations: this location consumes the raw material and produces finished products
                       \n* Transit Location: Counterpart location that should be used in inter-companies or inter-warehouses operations
                      """, select=True),
        'merchandise_type': fields.selection([("store", "Store"), ("warehouse", "Warehouse")], "Merchandise type"),
        'property_stock_account_input_location': fields.property(
            type='many2one',
            relation='account.account',
            string='Stock Input Account',
            help="When doing real-time inventory valuation, counterpart journal items for all incoming stock moves will be posted in this account, unless "
                 "there is a specific valuation account set on the source location. When not set on the product, the one from the product category is used."),
        'property_stock_account_output_location': fields.property(
            type='many2one',
            relation='account.account',
            string='Stock Output Account',
            help="When doing real-time inventory valuation, counterpart journal items for all outgoing stock moves will be posted in this account, unless "
                 "there is a specific valuation account set on the destination location. When not set on the product, the one from the product category is used."),
        'property_account_creditor_price_difference_location': fields.property(
            type='many2one',
            relation='account.account',
            string="Price Difference Account",
            help="This account will be used to value price difference between purchase price and cost price."),
        'property_account_income_location': fields.property(
            type='many2one',
            relation='account.account',
            string="Income Account",
            help="This account will be used to value outgoing stock using sale price."),
        'property_account_expense_location': fields.property(
            type='many2one',
            relation='account.account',
            string="Expense Account",
            help="This account will be used to value outgoing stock using cost price."),
    }

    _defaults = {
        'merchandise_type': 'warehouse'
    }


class stock_move(osv.Model):
    _name = "stock.move"
    _inherit = "stock.move"

    _columns = {
        'acc_move_id': fields.many2one('account.move', string='Account move', copy=False),
        'acc_move_line_ids': fields.one2many('account.move.line', 'stock_move_id', string='Account move lines'),
    }


    # Fix date on stock move from stock picking
    def onchange_date(self, cr, uid, ids, date, date_expected, context=None):
        """ On change of Scheduled Date gives a Move date.
        @param date_expected: Scheduled Date
        @param date: Move Date
        @return: Move Date
        """
        if ids:
            move = self.browse(cr, uid, ids[0], context=context)
            if move.picking_id:
                date_expected = move.picking_id.date 
        super(stock_move, self).onchange_date(cr, uid, ids, date, date_expected, context=context)


    def create_account_move_lines(self, cr, uid, ids, context=None):
        quant_obj = self.pool.get('stock.quant')
        acc_move_obj = self.pool.get('account.move')
        acc_move_line_obj = self.pool.get('account.move.line')
        if context is None:
            context = {}
        for move in self.browse(cr, uid, ids):
            period_id = context.get('force_period', self.pool.get(
                'account.period').find(cr, uid, move.date, context=context)[0])
            journal_id, acc_src, acc_dest, acc_valuation = quant_obj._get_accounting_data_for_valuation(
                cr, uid, move, context=context)
            acc_move_lines = []
            if move.state == 'done':
                for quant in move.quant_ids:
                    lines = quant_obj._account_entry_move(
                        cr, uid, [quant], move, context=context)
                    if lines:
                        for line in lines:
                            line_vals = line[2]
                            line_vals['stock_move_id'] = move.id
                            acc_move_lines += [(0, 0, line_vals)]
            if acc_move_lines != []:
                move_id = acc_move_obj.create(cr, uid, {'journal_id': journal_id,
                                                        'line_id': acc_move_lines,
                                                        'period_id': period_id,
                                                        'date': move.date,
                                                        'ref': move.name,
                                                        'name': move.picking_id and move.picking_id.name or '/'
                                                        }, context=context)
                self.write(cr, uid, [move.id], {'acc_move_id': move_id})
        return True

    def action_done(self, cr, uid, ids, context=None):
        res = super(stock_move, self).action_done(
            cr, uid, ids, context=context)
        for move in self.browse(cr, uid, ids, context=context):
            if move.picking_id:
                self.write(cr, uid, [move.id], {'date': move.picking_id.date})
            if not move.acc_move_id:
                self.create_account_move_lines(
                    cr, uid, [move.id], context=context)
        return res

    def action_cancel(self, cr, uid, ids, context=None):
        acc_move_obj = self.pool.get('account.move.line')
        for move in self.browse(cr, uid, ids, context=context):
            if move.acc_move_id:
                acc_move_obj.cancel(cr, uid, [move.acc_move_id.id])
                acc_move_obj.unlink(cr, uid, [move.acc_move_id.id])
        return super(stock_move, self).action_cancel(cr, uid, ids, context=context)

    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type, context=None):
        res = super(stock_move, self)._get_invoice_line_vals(
            cr, uid, move, partner, inv_type, context=context)
        fp_obj = self.pool.get('account.fiscal.position')

        # For receptions, get the stock account, instead of the expense one.
        account_id = res['account_id']
        if inv_type in ('in_invoice', 'in_refund'):
            account_id = move.product_id.property_stock_account_input and move.product_id.property_stock_account_input.id
            if not account_id:
                account_id = move.product_id.categ_id.property_stock_account_input_categ and move.product_id.categ_id.property_stock_account_input_categ.id
            if move.origin_returned_move_id:
                if move.location_id.property_stock_account_input_location:
                    account_id = move.location_id.property_stock_account_input_location and move.location_id.property_stock_account_input_location.id
            else:
                if move.location_dest_id.property_stock_account_input_location:
                    account_id = move.location_dest_id.property_stock_account_input_location and move.location_dest_id.property_stock_account_input_location.id
        if move.picking_id and move.picking_id.notice:
            if inv_type in ('in_invoice', 'in_refund'):
                account_id = move.company_id and move.company_id.property_stock_picking_payable_account_id and move.company_id.property_stock_picking_payable_account_id.id
            else:
                account_id = move.company_id and move.company_id.property_stock_picking_receivable_account_id and move.company_id.property_stock_picking_receivable_account_id.id
        fiscal_position = partner.property_account_position
        account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)
        res['account_id'] = account_id

        # If it is a returned stock move, change quantity in invoice with minus
        # (probably to be done in account_storno)
        if move.origin_returned_move_id:
            res['quantity'] = -1 * res['quantity']
        return res

# ----------------------------------------------------------
# Stock Quant
# ----------------------------------------------------------


class stock_quant(osv.Model):
    _name = "stock.quant"
    _inherit = "stock.quant"


    def _account_entry_move(self, cr, uid, quants, move, context=None):
        """
        Accounting Valuation Entries

        quants: browse record list of Quants to create accounting valuation entries for. Unempty and all quants are supposed to have the same location id (thay already moved in)
        move: Move to use. browse record
        """
        if context is None:
            context = {}
        location_obj = self.pool.get('stock.location')
        location_from = move.location_id
        location_to = quants[0].location_id
        company_from = location_obj._location_owner(
            cr, uid, location_from, context=context)
        company_to = location_obj._location_owner(
            cr, uid, location_to, context=context)

        res = []
        if move.product_id.valuation != 'real_time':
            return False
        for q in quants:
            if q.owner_id:
                # if the quant isn't owned by the company, we don't make any
                # valuation entry
                return False
            if q.qty <= 0:
                # we don't make any stock valuation for negative quants because the valuation is already made for the counterpart.
                # At that time the valuation will be made at the product cost price and afterward there will be new accounting entries
                # to make the adjustments when we know the real cost price.
                return False

        # in case of routes making the link between several warehouse of the same company, the transit location belongs to this company, so we don't need to create accounting entries
        # Create Journal Entry for stock moves
        ctx = context.copy()
        if company_to:
            if move.location_id.usage in ('supplier', 'customer'):
                ctx['force_company'] = company_to.id
        if company_from:
            if move.location_dest_id.usage in ('supplier', 'customer'):
                ctx['force_company'] = company_from.id

        # Put notice in context if the picking is a notice
        ctx['notice'] = move.picking_id and move.picking_id.notice

        # Create account moves for price difference and uneligible VAT is inventory of one the location is kept at list price.
        # To do : intercompany moves.
        if (move.location_id.usage == 'internal' and move.location_id.merchandise_type == 'store') or (move.location_dest_id.usage == 'internal' and move.location_dest_id.merchandise_type == 'store'):
            # Create moves for entry to stock location with merchandise type ==
            # store
            if (move.location_id.usage != 'internal' or (move.location_id.usage == 'internal' and move.location_id.merchandise_type != 'store')) and (move.location_dest_id.usage == 'internal' and move.location_dest_id.merchandise_type == 'store'):
                ctx['type'] = 'reception_diff'
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(
                    cr, uid, move, context=ctx)
                if acc_src and acc_dest and acc_src != acc_dest:
                    res += self._create_account_move_line(
                        cr, uid, quants, move, acc_src, acc_dest, journal_id, context=ctx)
                ctx['type'] = 'reception_diff_vat'
                if move.location_id.usage != 'supplier':
                    journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(
                        cr, uid, move, context=ctx)
                    if acc_src and acc_dest and acc_src != acc_dest:
                        res += self._create_account_move_line(
                            cr, uid, quants, move, acc_src, acc_dest, journal_id, context=ctx)

            # Create moves for outgoing from stock
            if (move.location_dest_id.usage != 'internal' or (move.location_dest_id.usage == 'internal' and move.location_dest_id.merchandise_type != 'store')) and (move.location_id.usage == 'internal' and move.location_id.merchandise_type == 'store'):
                ctx['type'] = 'delivery_diff'
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(
                    cr, uid, move, context=ctx)
                if acc_src and acc_dest and acc_src != acc_dest:
                    res += self._create_account_move_line(
                        cr, uid, quants, move, acc_src, acc_dest, journal_id, context=ctx)
                ctx['type'] = 'delivery_diff_vat'
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(
                    cr, uid, move, context=ctx)
                if acc_src and acc_dest and acc_src != acc_dest:
                    res += self._create_account_move_line(
                        cr, uid, quants, move, acc_src, acc_dest, journal_id, context=ctx)

        # Create account moves for deliveries with notice (e.g. 418 = 707)
        if move.picking_id and move.picking_id.notice and move.location_id.usage == 'internal' and move.location_dest_id.usage == 'customer':
            ctx['type'] = 'delivery_notice'
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(
                cr, uid, move, context=ctx)
            if acc_src and acc_dest and acc_src != acc_dest:
                res += self._create_account_move_line(
                    cr, uid, quants, move, acc_src, acc_dest, journal_id, context=ctx)
            # Change context to create account moves for cost of goods sold
            # (e.g. 607 = 371)
            ctx['notice'] = False
            ctx['type'] = 'delivery'

        # Change context to create account moves for cost of goods sold in case
        # of refund (e.g. 371 = 607)
        if not move.picking_id.notice and move.location_id.usage == 'customer' and move.location_dest_id.usage == 'internal':
            ctx['type'] = 'delivery_refund'

        if not move.picking_id.notice and move.location_id.usage == 'internal' and move.location_dest_id.usage not in ('supplier', 'transit'):
            # Change context to create account moves for cost of goods
            # delivered  (e.g. 607 = 371)
            ctx['notice'] = False
            ctx['type'] = 'delivery'
            # Change context to create account moves for collected VAT in case
            # of minus in inventory  (e.g. 635 = 4427)
            if move.location_dest_id.usage == 'inventory':
                ctx['type'] = 'inventory_vat'
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(
                    cr, uid, move, context=ctx)
                if acc_src and acc_dest and acc_src != acc_dest:
                    res += self._create_account_move_line(
                        cr, uid, quants, move, acc_src, acc_dest, journal_id, context=ctx)
                # Change context to create account moves for minus in inventory
                # (e.g. 607 = 371 with VAT collected based)
                ctx['type'] = 'inventory_exp'
            # Change context to create account moves for usage giving  (e.g.
            # 8035 = 8035)
            if move.location_dest_id.usage == 'usage_giving':
                ctx['type'] = 'usage_giving'
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(
                    cr, uid, move, context=ctx)
                if acc_src and acc_dest and ctx['type'] == 'usage_giving':
                    res += self._create_account_move_line(
                        cr, uid, quants, move, acc_src, acc_dest, journal_id, context=ctx)
                # Change context to create account moves for cost of goods
                # delivered  (e.g. 607 = 371)
                ctx['type'] = 'delivery'

        # Change context to create account moves for plus in inventory  (e.g.
        # -607 = -371)
        if not move.picking_id.notice and move.location_id.usage == 'inventory' and move.location_dest_id.usage == 'internal':
            ctx['notice'] = False
            ctx['type'] = 'inventory'

        journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(
            cr, uid, move, context=ctx)
        if acc_src and acc_dest and acc_src != acc_dest:
            res += self._create_account_move_line(
                cr, uid, quants, move, acc_src, acc_dest, journal_id, context=ctx)
        return res

    def _prepare_account_move_line(self, cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=None):
        res = super(stock_quant, self)._prepare_account_move_line(
            cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=context)
        debit_line_vals = res[0][2]
        credit_line_vals = res[1][2]
        if context is None:
            context = {}
        currency_obj = self.pool.get('res.currency')

        # Calculate VAT base and amount for price differences and associate it
        # to account move lines
        if context.get('type', False) and context.get('type') in ('reception_diff', 'reception_diff_vat', 'delivery_diff', 'delivery_diff_vat'):
            if context.get('force_valuation_amount'):
                valuation_amount = context.get('force_valuation_amount')
            else:
                valuation_amount = move.product_id.cost_method == 'real' and cost or move.product_id.standard_price
            list_price = move.product_id.list_price or 0.00
            if list_price <= valuation_amount:
                raise osv.except_osv(_('Error!'), _(
                    "You cannot receive products if list price is lower than cost price. Pleasu update list price to suit to be upper than %s." % valuation_amount))
            else:
                # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
                # the company currency... so we need to use round() before
                # creating the accounting entries.
                valuation_amount = list_price * qty - \
                    currency_obj.round(
                        cr, uid, move.company_id.currency_id, valuation_amount * qty)
                taxes = []
                if move.product_id.taxes_id:
                    taxes = self.pool.get('account.tax')._unit_compute(
                        cr, uid, move.product_id.taxes_id[0], valuation_amount)
                if taxes:
                    tax = taxes[0]
                    if context.get('type') in ('reception_diff', 'reception_diff_vat'):
                        # Receptions in location with inventory kept at list
                        # price
                        if context.get('type') == 'reception_diff':
                            debit_line_vals['tax_code_id'] = self.pool.get('account.tax.code').browse(cr, uid, tax['base_code_id']).uneligible_tax_code_id and self.pool.get(
                                'account.tax.code').browse(cr, uid, tax['base_code_id']).uneligible_tax_code_id.id or False
                            debit_line_vals['tax_amount'] = valuation_amount
                            debit_line_vals['debit'] = valuation_amount
                            debit_line_vals['credit'] = 0.00
                            credit_line_vals['credit'] = valuation_amount
                            credit_line_vals['debit'] = 0.00
                        else:
                            debit_line_vals['tax_code_id'] = self.pool.get('account.tax.code').browse(cr, uid, tax['tax_code_id']).uneligible_tax_code_id and self.pool.get(
                                'account.tax.code').browse(cr, uid, tax['tax_code_id']).uneligible_tax_code_id.id or False
                            debit_line_vals['tax_amount'] = tax['amount']
                            debit_line_vals['debit'] = tax[
                                'amount'] > 0 and round(tax['amount'], 2) or 0.00
                            debit_line_vals['credit'] = tax[
                                'amount'] < 0 and -1 * round(tax['amount'], 2) or 0.00
                            credit_line_vals['credit'] = tax[
                                'amount'] > 0 and round(tax['amount'], 2) or 0.00
                            credit_line_vals['debit'] = tax[
                                'amount'] < 0 and -1 * round(tax['amount'], 2) or 0.00
                    if context.get('type') in ('delivery_diff', 'delivery_diff_vat'):
                        # Deliveries from location with inventory kept at list
                        # price
                        if context.get('type') == 'delivery_diff':
                            credit_line_vals['tax_code_id'] = self.pool.get('account.tax.code').browse(cr, uid, tax['base_code_id']).uneligible_tax_code_id and self.pool.get(
                                'account.tax.code').browse(cr, uid, tax['base_code_id']).uneligible_tax_code_id.id or False
                            credit_line_vals['tax_amount'] = valuation_amount
                            debit_line_vals['debit'] = valuation_amount
                            debit_line_vals['credit'] = 0.00
                            credit_line_vals['credit'] = valuation_amount
                            credit_line_vals['debit'] = 0.00
                        else:
                            credit_line_vals['tax_code_id'] = self.pool.get('account.tax.code').browse(cr, uid, tax['tax_code_id']).uneligible_tax_code_id and self.pool.get(
                                'account.tax.code').browse(cr, uid, tax['tax_code_id']).uneligible_tax_code_id.id or False
                            credit_line_vals['tax_amount'] = tax['amount']
                            debit_line_vals['debit'] = tax[
                                'amount'] > 0 and round(tax['amount'], 2) or 0.00
                            debit_line_vals['credit'] = tax[
                                'amount'] < 0 and -1 * round(tax['amount'], 2) or 0.00
                            credit_line_vals['credit'] = tax[
                                'amount'] > 0 and round(tax['amount'], 2) or 0.00
                            credit_line_vals['debit'] = tax[
                                'amount'] < 0 and -1 * round(tax['amount'], 2) or 0.00

        # Calculate VAT base and amount for minus in inventories and associate
        # it to account move lines
        if context.get('type', False) and (context.get('type') == 'inventory_exp' or context.get('type') == 'inventory_vat'):
            if context.get('force_valuation_amount'):
                valuation_amount = context.get('force_valuation_amount')
            else:
                valuation_amount = move.product_id.cost_method == 'real' and cost or move.product_id.standard_price
            # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
            # the company currency... so we need to use round() before creating
            # the accounting entries.
            valuation_amount = currency_obj.round(
                cr, uid, move.company_id.currency_id, valuation_amount * qty)
            taxes = []
            if move.product_id.taxes_id:
                taxes = self.pool.get('account.tax')._unit_compute(
                    cr, uid, move.product_id.taxes_id[0], valuation_amount)
            if taxes:
                tax = taxes[0]
                if context.get('type') == 'inventory_exp':
                    credit_line_vals['tax_code_id'] = tax['base_code_id']
                    credit_line_vals['tax_amount'] = valuation_amount
                else:
                    credit_line_vals['tax_code_id'] = tax['tax_code_id']
                    credit_line_vals['tax_amount'] = tax['amount']
                    credit_line_vals['account_id'] = tax[
                        'account_collected_id']
                    debit_line_vals['debit'] = tax[
                        'amount'] > 0 and round(tax['amount'], 2) or 0.00
                    debit_line_vals['credit'] = tax[
                        'amount'] < 0 and -1 * round(tax['amount'], 2) or 0.00
                    credit_line_vals['credit'] = tax[
                        'amount'] > 0 and round(tax['amount'], 2) or 0.00
                    credit_line_vals['debit'] = tax[
                        'amount'] < 0 and -1 * round(tax['amount'], 2) or 0.00

        # Change the amounts to be with minus in case of delivery refund
        if context.get('type', False) and context.get('type') == 'delivery_refund':
            debit_line_vals['debit'] = -1 * debit_line_vals['debit']
            debit_line_vals['credit'] = -1 * debit_line_vals['credit']
            credit_line_vals['credit'] = -1 * credit_line_vals['credit']
            credit_line_vals['debit'] = -1 * credit_line_vals['debit']
        # Change the amount in case of delivery with notice to price unit
        # invoice
        if context.get('type', False) and context.get('type') == 'delivery_notice':
            valuation_amount = cost
            if move.procurement_id and move.procurement_id.sale_line_id:
                sale_line = move.procurement_id.sale_line_id
                if move.product_id.id != sale_line.product_id.id:
                    price_invoice = self.pool['product.pricelist'].price_get(
                        cr, uid, [sale_line.order_id.pricelist_id.id],
                        move.product_id.id, move.product_uom_qty or 1.0,
                        sale_line.order_id.partner_id, context=context)[sale_line.order_id.pricelist_id.id]
                else:
                    price_invoice = sale_line.price_unit
                price_invoice = currency_obj._get_conversion_rate(
                    cr, uid, sale_line.order_id.currency_id, move.company_id.currency_id, context=context) * price_invoice
                valuation_amount = price_invoice * qty
            debit_line_vals['debit'] = valuation_amount
            debit_line_vals['credit'] = 0.00
            credit_line_vals['credit'] = valuation_amount
            credit_line_vals['debit'] = 0.00

        return [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

    def _get_accounting_data_for_valuation(self, cr, uid, move, context=None):
        """
        Return the accounts and journal to use to post Journal Entries for the real-time
        valuation of the quant.

        :param context: context dictionary that can explicitly mention the company to consider via the 'force_company' key
        :returns: journal_id, source account, destination account, valuation account
        :raise: osv.except_osv() is any mandatory account or journal is not defined.
        """
        journal_id, acc_src, acc_dest, acc_valuation = super(
            stock_quant, self)._get_accounting_data_for_valuation(cr, uid, move, context=context)

        if move.location_id.property_stock_account_output_location:
            acc_src = move.location_id.property_stock_account_output_location.id
        if move.location_dest_id.property_stock_account_input_location:
            acc_dest = move.location_dest_id.property_stock_account_input_location.id

        # Change accounts to suit romanian stock account moves.
        if context.get('type', False):
            move_type = context.get('type')
            if move_type == 'delivery_notice':
                # Change the account to the income one (70x) to suit move 418 =
                # 70x
                acc_src = move.product_id.property_account_income and move.product_id.property_account_income.id or False
                if not acc_src:
                    acc_src = move.product_id.categ_id.property_account_income_categ and move.product_id.categ_id.property_account_income_categ.id
                if move.location_id.property_account_income_location:
                    acc_src = move.location_id.property_account_income_location.id
            if move_type == 'usage_giving':
                # Change the account to the usage giving one defined in
                # company: usualy 8035
                acc_src = acc_dest = move.company_id.property_stock_usage_giving_account_id and move.company_id.property_stock_usage_giving_account_id.id or False
            if move_type == 'delivery':
                # Change the account to the expense one (6xx) to suit move: 6xx
                # = 3xx
                acc_dest = move.product_id.property_account_expense and move.product_id.property_account_expense.id or False
                if not acc_dest:
                    acc_dest = move.product_id.categ_id.property_account_expense_categ and move.product_id.categ_id.property_account_expense_categ.id
                if move.location_id.property_account_expense_location:
                    acc_dest = move.location_id.property_account_expense_location.id
            if move_type == 'inventory':
                # Inventory in plus
                # Change the account to the expense one (6xx) to suit move: 3xx
                # = 6xx
                acc_src = move.product_id.property_account_expense and move.product_id.property_account_expense.id or False
                if not acc_src:
                    acc_src = move.product_id.categ_id.property_account_expense_categ and move.product_id.categ_id.property_account_expense_categ.id
                if move.location_dest_id.property_account_expense_location:
                    acc_src = move.location_dest_id.property_account_expense_location.id
            if move_type in ('inventory_exp', 'delivery_refund'):
                # Inventory with minus and return of delivery
                # Change the account to the expense one (6xx) to suit move: 6xx
                # = 3xx
                if move_type == 'delivery_refund':
                    acc_src = acc_dest
                acc_dest = move.product_id.property_account_expense and move.product_id.property_account_expense.id or False
                if not acc_dest:
                    acc_dest = move.product_id.categ_id.property_account_expense_categ and move.product_id.categ_id.property_account_expense_categ.id
                if move.location_id.property_account_expense_location:
                    acc_dest = move.location_id.property_account_expense_location.id
            if move_type == 'inventory_vat':
                # Inventory with minus - collect vat
                # Change the accounts with the vat one (442700) and
                # undeductible one defined in company (usualy 635000) to suit
                # move: 635000 = 442700
                if move.product_id.taxes_id and move.product_id.taxes_id[0].account_collected_id:
                    acc_src = move.product_id.taxes_id[
                        0].account_collected_id.id or False
                if move.company_id.property_account_undeductible:
                    acc_dest = move.company_id and move.company_id.property_undeductible_tax_account_id and move.company_id.property_undeductible_tax_account_id.id or False
            if move_type == 'reception_diff':
                # Receptions in location with inventory kept at list price
                # Change the accounts with the price difference one (3x8) to
                # suit move: 3xx = 3x8
                acc_src = move.product_id.property_account_creditor_price_difference and move.product_id.property_account_creditor_price_difference.id or False
                if not acc_src:
                    acc_src = move.product_id.categ_id.property_account_creditor_price_difference_categ and move.product_id.categ_id.property_account_creditor_price_difference_categ.id
                if move.location_dest_id.property_account_creditor_price_difference_location:
                    acc_src = move.location_dest_id.property_account_creditor_price_difference_location.id
            if move_type == 'reception_diff_vat':
                # Receptions in location with inventory kept at list price
                # Change the accounts with the uneligible vat one (442810) to
                # suit move: 3xx = 442810
                if move.product_id.taxes_id and move.product_id.taxes_id[0].account_collected_id and move.product_id.taxes_id[0].account_collected_id.uneligible_account_id:
                    acc_src = move.product_id.taxes_id[
                        0].account_collected_id.uneligible_account_id.id
                else:
                    acc_src = False
            if move_type == 'delivery_diff':
                # Deliveries from location with inventory kept at list price
                # Change the accounts with the price difference one (3x8) to
                # suit move: 3x8 = 3xx
                acc_dest = move.product_id.property_account_creditor_price_difference and move.product_id.property_account_creditor_price_difference.id or False
                if not acc_dest:
                    acc_dest = move.product_id.categ_id.property_account_creditor_price_difference_categ and move.product_id.categ_id.property_account_creditor_price_difference_categ.id
                if move.location_dest_id.property_account_creditor_price_difference_location:
                    acc_dest = move.location_dest_id.property_account_creditor_price_difference_location.id
            if move_type == 'delivery_diff_vat':
                # Deliveries from location with inventory kept at list price
                # Change the accounts with the uneligible vat one (442810) to
                # suit move: 442810 = 3xx
                if move.product_id.taxes_id and move.product_id.taxes_id[0].account_collected_id and move.product_id.taxes_id[0].account_collected_id.uneligible_account_id:
                    acc_dest = move.product_id.taxes_id[
                        0].account_collected_id.uneligible_account_id.id
                else:
                    acc_dest = False

        # If it is a notice, check if picking type is incoming or outgoing and
        # replace the stock accounts with the payable / receivable notice
        # accounts
        if context.get('notice', False):
            if move.location_id.usage == 'supplier':
                acc_src = move.company_id and move.company_id.property_stock_picking_payable_account_id and move.company_id.property_stock_picking_payable_account_id.id
            if move.location_dest_id.usage == 'supplier':
                acc_dest = move.company_id and move.company_id.property_stock_picking_payable_account_id and move.company_id.property_stock_picking_payable_account_id.id
            if move.location_dest_id.usage == 'customer':
                acc_dest = move.company_id and move.company_id.property_stock_picking_receivable_account_id and move.company_id.property_stock_picking_receivable_account_id.id
            if move.location_id.usage == 'customer':
                acc_src = move.company_id and move.company_id.property_stock_picking_receivable_account_id and move.company_id.property_stock_picking_receivable_account_id.id

        return journal_id, acc_src, acc_dest, acc_valuation

    def _create_account_move_line(self, cr, uid, quants, move, credit_account_id, debit_account_id, journal_id, context=None):
        res = []
        for quant in quants:
            res += self._prepare_account_move_line(
                cr, uid, move, quant.qty, quant.cost, credit_account_id, debit_account_id, context=context)
        return res


class stock_picking(osv.Model):
    _name = 'stock.picking'
    _inherit = 'stock.picking'

    _columns = {
        'acc_move_line_ids': fields.one2many('account.move.line', 'stock_picking_id', string='Generated accounting lines'),
        'notice': fields.boolean('Is a notice', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),               
    }

    _defaults = {
        'notice': False,
    }


    def get_account_move_lines(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for pick in self.browse(cr, uid, ids, context=context):
            acc_move_lines = []
            for move in pick.move_lines:
                if move.acc_move_id:
                    acc_move_lines += [
                        aml.id for aml in move.acc_move_id.line_id]
            if acc_move_lines != []:
                self.pool.get('account.move.line').write(
                    cr, uid, acc_move_lines, {'stock_picking_id': pick.id})
        return True

    @api.cr_uid_ids_context
    def do_transfer(self, cr, uid, picking_ids, context=None):
        for pick in self.browse(cr, uid, picking_ids, context=context):
            self.write(cr, uid, pick.id, {'date_done': pick.date})
        res = super(stock_picking, self).do_transfer(
            cr, uid, picking_ids, context=context)
        self.get_account_move_lines(cr, uid, picking_ids, context=context)
        return res

    def action_done(self, cr, uid, picking_ids, context=None):
        for pick in self.browse(cr, uid, picking_ids, context=context):
            self.write(cr, uid, pick.id, {'date_done': pick.date})
        res = super(stock_picking, self).action_done(
            cr, uid, picking_ids, context=context)
        self.get_account_move_lines(cr, uid, picking_ids, context=context)
        return res

    def action_cancel(self, cr, uid, ids, context=None):
        acc_move_obj = self.pool.get('account.move')
        acc_move_line_obj = self.pool.get('account.move.line')
        for pick in self.browse(cr, uid, ids, context=context):
            for move in pick.move_lines:
                if move.acc_move_id:
                    acc_move_obj.cancel(cr, uid, [move.acc_move_id.id])
                    acc_move_obj.unlink(cr, uid, [move.acc_move_id.id])
        return super(stock_picking, self).action_cancel(cr, uid, ids, context=context)

    def action_unlink(self, cr, uid, ids, context=None):
        acc_move_obj = self.pool.get('account.move')
        for pick in self.browse(cr, uid, ids, context=context):
            for move in pick.move_lines:
                if move.acc_move_id:
                    acc_move_obj.cancel(cr, uid, [move.acc_move_id.id])
                    acc_move_obj.unlink(cr, uid, [move.acc_move_id.id])
        return super(stock_picking, self).action_unlink(cr, uid, ids, context=context)

    def action_invoice_create(self, cr, uid, ids, journal_id, group=False, type='out_invoice', context=None):
        res = super(stock_picking, self).action_invoice_create(
            cr, uid, ids, journal_id, group, type, context=context)
        self.write(cr, uid, ids, {'notice': False})
        return res


class stock_inventory(osv.Model):
    _name = "stock.inventory"
    _inherit = "stock.inventory"

    _columns = {
        'acc_move_line_ids': fields.one2many('account.move.line', 'stock_inventory_id', string='Generated accounting lines'),
    }

    def get_account_move_lines(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for inv in self.browse(cr, uid, ids, context=context):
            acc_move_lines = []
            for move in inv.move_ids:
                if move.acc_move_id:
                    acc_move_lines += [
                        aml.id for aml in move.acc_move_id.line_id]
            if acc_move_lines != []:
                self.pool.get('account.move.line').write(
                    cr, uid, acc_move_lines, {'stock_inventory_id': inv.id})
        return True

    def post_inventory(self, cr, uid, inv, context=None):
        res = super(stock_inventory, self).post_inventory(
            cr, uid, inv, context=context)
        self.get_account_move_lines(cr, uid, [inv.id], context=context)
        return res

    def action_cancel_draft(self, cr, uid, ids, context=None):
        acc_move_obj = self.pool.get('account.move')
        for inv in self.browse(cr, uid, ids, context=context):
            for move in inv.move_ids:
                if move.acc_move_id:
                    acc_move_obj.cancel(cr, uid, [move.acc_move_id.id])
                    acc_move_obj.unlink(cr, uid, [move.acc_move_id.id])
        return super(stock_inventory, self).action_cancel_draft(cr, uid, ids, context=context)
