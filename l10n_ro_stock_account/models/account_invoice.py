# -*- coding: utf-8 -*-
# ©  2008-2018 Fekete Mihai <mihai.fekete@forbiom.eu>
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare
import itertools


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # nu trebuie sa se schimbe locatia la receptie
    stock_location_id = fields.Many2one('stock.location', readonly=True, states={'draft': [('readonly', False)]})

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.stock_location_id:
            self.stock_location_id = self.purchase_id.picking_type_id.default_location_dest_id
        res = super(AccountInvoice, self).purchase_order_change()
        return res

    # todo: poate ca e mai bine sa determina contrul in metoda get_invoice_line_account

    def _prepare_invoice_line_from_po_line(self, line):
        data = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)

        if self.type in ['in_invoice', 'in_refund']:
            if 'account_id' not in data:
                data['account_id'] = False  # daca ne e facuta configurarea conturilor
            if line.product_id.purchase_method == 'receive':  # receptia in baza cantitatilor primite
                if line.product_id.type == 'product':
                    notice = False
                    for picking in line.order_id.picking_ids:
                        if picking.notice:
                            notice = True

                    if notice:  # daca e stocabil si exista un document facut
                        data['account_id'] = line.company_id.property_stock_picking_payable_account_id.id or \
                                             line.product_id.property_stock_account_input.id or \
                                             line.product_id.categ_id.property_stock_account_input_categ_id.id or \
                                             data['account_id']
                    else:
                        data['account_id'] = line.product_id.property_stock_account_input.id or \
                                             line.product_id.categ_id.property_stock_account_input_categ_id.id or \
                                             data['account_id']

                else:  # daca nu este stocabil trebuie sa fie un cont de cheltuiala
                    data['account_id'] = line.product_id.property_account_expense_id.id or \
                                         line.product_id.categ_id.property_account_expense_categ_id.id or \
                                         data['account_id']
            else:
                if line.product_id.type == 'product':
                    data['account_id'] = line.product_id.property_stock_account_input.id or \
                                         line.product_id.categ_id.property_stock_account_input_categ_id.id or \
                                         data['account_id']

        return data

    @api.model
    def invoice_line_move_line_get(self):

        res = super(AccountInvoice, self).invoice_line_move_line_get()

        if not self.env.user.company_id.anglo_saxon_accounting:
            if self.type in ['in_invoice', 'in_refund']:

                for i_line in self.invoice_line_ids:
                    i_line.modify_stock_move_value(i_line.price_subtotal)

        if self.type in ['in_invoice', 'in_refund']:
            res = self.trade_discount_distribution(res)

        for line in res:
            line['stock_location_id'] = self.stock_location_id.id

        return res

    @api.multi
    def trade_discount_distribution(self, res):

        # distribuire valaore de pe linii cu discount comerical
        account_id = self.company_id.property_trade_discount_received_account_id

        discounts = {}
        discount_lines = self.invoice_line_ids.filtered(lambda x: x.account_id.id == account_id.id)
        for line in discount_lines:
            discounts[line.id] = {
                'line_id': line,
                'amount': line.price_subtotal,
                'rap': 0.0,
                'lines': self.env['account.invoice.line']
            }
            for aml in res:
                if aml.get('invl_id') == line.id:
                    discounts[line.id]['aml'] = aml

        invoice_lines = []
        for line in self.invoice_line_ids:
            invoice_lines.insert(0, line)
        # pentru ce linii sunt aferente aceste discounturi - sunt luate in calcul liniile de inaintea discountului
        discount = False
        for line in invoice_lines:  ##self.invoice_line_ids.sorted(key=lambda r: r.sequence, reverse=True):
            if line.account_id.id == account_id.id:
                discount = discounts[line.id]
            else:
                # eventual se va adauga o conditie petnru a utiliza dosr conturle care sunt de stoc
                if discount and line.product_id.type == 'product':
                    discount['lines'] |= line

        for line_id in discounts:
            value = 0
            for line in discounts[line_id]['lines']:
                value += line.price_subtotal
            if value:
                rap = discounts[line_id]['amount'] / value
                discounts[line_id]['rap'] = rap

                for line in discounts[line_id]['lines']:
                    for aml in res:
                        if aml.get('invl_id') == line.id:
                            val = aml['price'] * discounts[line_id]['rap']
                            aml['price'] += val
                            discounts[line_id]['aml']['price'] += -val
                            # todo: modify_stock_move_value() primeste acum intreaga valoare, nu doar diferenta
                            # todo: deci trebuie schimbat cum este chemata mai jos, dar nu inteleg functia asta deci nu stiu cum sa o schimb
                            line.modify_stock_move_value(val)

        for aml in res:
            if aml['price'] == 0:
                res.remove(aml)
        return res

    # @api.multi
    # def finalize_invoice_move_lines(self, move_lines):
    #     move_lines  = super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
    #
    #     for line in move_lines:
    #         if self.type in ['in_invoice','out_refund']:
    #             line[2]['stock_location_dest_id'] = self.stock_location_id.id
    #         else:
    #             line[2]['stock_location_id'] = self.stock_location_id.id
    #
    #     return move_lines


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    def modify_stock_move_value(self, value):
        if value < 0:
            raise UserError(_('Your action would have the consequence that a stock move is to be evaluated to %s, which is less than 0 and hence impossible' %str(value)))
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        should_modify_stock_value = bool(self.product_id and \
                                    self.product_id.valuation == 'real_time' and \
                                    self.product_id.type == 'product' and \
                                    self.product_id.cost_method != 'standard' and \
                                    self.purchase_line_id and \
                                    float_compare(self.quantity, 0.0, precision_digits=precision) > 0)

        if should_modify_stock_value:
            evaluated_stock_moves = self.env['stock.move'].search([('invoice_line_evaluated_by', '=', self.id)])
            if evaluated_stock_moves:
                return self._evaluate_moves(evaluated_stock_moves, value)
            else:
                stock_moves = self.env['stock.move'].search([
                    ('purchase_line_id', '=', self.purchase_line_id.id),
                    ('state', '=', 'done'), ('product_qty', '!=', 0.0),
                    ('invoice_line_evaluated_by', '=', False)])
                return self._evaluate_moves(stock_moves, value)
        return False

    def _evaluate_moves(self, stock_moves, value):
        if self.invoice_id.type == 'in_refund':
            stock_moves = stock_moves.filtered(lambda m: m._is_out())
        elif self.invoice_id.type == 'in_invoice':
            stock_moves = stock_moves.filtered(lambda m: m._is_in())

        stock_moves = self._ensure_total_matches_line_quantity(stock_moves)

        total_received_quantity = sum(stock_moves.mapped('product_qty'))
        for move in stock_moves:
            current_move_received_quantity = move.product_qty
            current_move_value = (current_move_received_quantity / total_received_quantity) * value

            move.write({
                'value': current_move_value,
                'remaining_value': current_move_value / current_move_received_quantity * move.remaining_value,
                'price_unit': current_move_value / current_move_received_quantity,
                'invoice_line_evaluated_by': self.id})

        self.product_id.update_fifo_cost(self.company_id)
        return stock_moves

    def _ensure_total_matches_line_quantity(self, stock_moves):
        if stock_moves:
            stock_quantity = sum(stock_moves.mapped('product_uom_qty'))
            if self.quantity == stock_quantity:
                return stock_moves
            elif self.quantity > stock_quantity:
                raise UserError(_('It is not allowed to record an invoice for a quantity bigger than %s') % str(stock_quantity))
            else:
                return self._find_subset_of_moves_with_total_quantity(stock_moves)
        else:
            return stock_moves

    def _find_subset_of_moves_with_total_quantity(self, stock_moves):
        stock_moves_list = list(stock_moves)
        searched_sum = self.quantity
        permutations = list(itertools.product([0, 1], repeat=len(stock_moves_list)))

        solution = ()
        for permutation in permutations:
            current_sum = 0
            for i in range(len(stock_moves_list)):
                current_sum += stock_moves_list[i].product_uom_qty * permutation[i]
            if current_sum == searched_sum:
                solution = permutation
                break

        if solution:
            solution_stock_moves = self.env['stock.move']
            for i in range(len(stock_moves_list)):
                should_include = solution[i]
                if should_include:
                    solution_stock_moves |= stock_moves_list[i]
            return solution_stock_moves
        else:
            raise UserError(_('No combination of incoming stock moves to sum quantity: %s') %str(searched_sum))

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.invoice_id.type not in ['in_refund', 'out_refund']:
            allowed_change_product = self.env.context.get('allowed_change_product', False)
            if self.product_id and self.product_id.type == 'product' and not allowed_change_product:
                raise UserError(_('It is not allowed to change a stored product!'))
        return super(AccountInvoiceLine, self)._onchange_product_id()

    # this method creates a constraint such that we cannot invoice a quantity that we did not receive yet
    @api.onchange('quantity')
    def _onchange_quantity(self):
        message = ''
        if self.invoice_id.type in ['in_refund', 'out_refund']:
            return
        if self.product_id and self.product_id.type == 'product':

            if self.purchase_line_id:
                qty_invoiced = 0
                for inv_line in self.purchase_line_id.invoice_lines:
                    if not isinstance(inv_line.id, models.NewId) and inv_line.invoice_id.state not in ['cancel']:
                        if inv_line.invoice_id.type == 'in_invoice':
                            qty_invoiced += inv_line.uom_id._compute_quantity(inv_line.quantity,
                                                                              self.purchase_line_id.product_uom)
                        elif inv_line.invoice_id.type == 'in_refund':
                            qty_invoiced -= inv_line.uom_id._compute_quantity(inv_line.quantity,
                                                                              self.purchase_line_id.product_uom)

                invoiceable_qty = self.purchase_line_id.qty_received - qty_invoiced
                invoiceable_uom_qty = self.purchase_line_id.product_uom._compute_quantity(invoiceable_qty, self.uom_id)

                if invoiceable_uom_qty < self.quantity:
                    raise UserError(_('It is not allowed to record an invoice for a quantity bigger than %s') % str(
                        invoiceable_uom_qty))
            else:
                message = _('It is not indicated to change the quantity of a stored product!')
        if message:
            return {
                'warning': {'title': "Warning", 'message': message},
            }
