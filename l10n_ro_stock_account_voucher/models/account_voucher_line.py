import itertools
from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.tools import float_compare

class AccountVoucherLine(models.Model):
    _inherit = 'account.voucher.line'

    purchase_line_id = fields.Many2one(
        comodel_name='purchase.order.line',
        string='Purchase Order Line',
        help='When voucher is created as part of an purchase, this field links the voucher line to the origin purchase line')

    purchase_id = fields.Many2one(
        comodel_name='purchase.order',
        related='purchase_line_id.order_id',
        string='Purchase Order',
        store=False,
        readonly=True,
        related_sudo=False,
        help='Associated Purchase Order. Filled in automatically when a PO is chosen on the account voucher.')

    uom_id = fields.Many2one(
        comodel_name='product.uom',
        string='Unit of Measure',
        ondelete='set null')

    def modify_stock_move_value(self, value):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        should_modify_stock_value = bool(self.product_id and \
                                         self.product_id.valuation == 'real_time' and \
                                         self.product_id.type == 'product' and \
                                         self.product_id.cost_method != 'standard' and \
                                         self.purchase_line_id and \
                                         float_compare(self.quantity, 0.0, precision_digits=precision) > 0)

        if should_modify_stock_value:
            if value < 0:
                raise UserError(_('Your action would have the consequence that a stock move is to be evaluated to %s, which is less than 0 and hence impossible' % str(value)))
            evaluated_stock_moves = self.env['stock.move'].search([('voucher_line_evaluated_by', '=', self.id)])
            if evaluated_stock_moves:
                return self._evaluate_moves(evaluated_stock_moves, value)
            else:
                stock_moves = self.env['stock.move'].search([
                    ('purchase_line_id', '=', self.purchase_line_id.id),
                    ('state', '=', 'done'), ('product_qty', '!=', 0.0),
                    ('voucher_line_evaluated_by', '=', False)])
                return self._evaluate_moves(stock_moves, value)
        return False

    def _evaluate_moves(self, stock_moves, value):
        stock_moves = self._ensure_total_matches_line_quantity(stock_moves)

        total_received_quantity = sum(stock_moves.mapped('product_qty'))
        for move in stock_moves:
            current_move_received_quantity = move.product_qty
            current_move_value = (current_move_received_quantity / total_received_quantity) * value

            move.write({
                'value': current_move_value,
                'remaining_value': current_move_value / current_move_received_quantity * move.remaining_qty,
                'price_unit': current_move_value / current_move_received_quantity,
                'voucher_line_evaluated_by': self.id})

        self.product_id.update_fifo_cost(self.company_id)
        return stock_moves

    def _ensure_total_matches_line_quantity(self, stock_moves):
        if stock_moves:
            stock_quantity = sum(stock_moves.mapped('product_uom_qty'))
            if self.quantity == stock_quantity:
                return stock_moves
            elif self.quantity > stock_quantity:
                raise UserError(_('It is not allowed to record a voucher for a quantity bigger than %s') % str(stock_quantity))
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
            raise UserError(_('No combination of incoming stock moves to sum quantity: %s') % str(searched_sum))
