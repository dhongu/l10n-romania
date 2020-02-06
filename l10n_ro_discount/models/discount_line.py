from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class DiscountLine(models.Model):
    _name = 'account.invoice.discount.line'
    _description = 'Discount Line'

    discounted_invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Discounted invoice',
        help='Invoice containing the line which this discount was applied to',
        required=True,
        ondelete='cascade')

    discounted_invoice_line_id = fields.Many2one(
        comodel_name='account.invoice.line',
        string='Discounted invoice line',
        help='Invoice line to which this discount was applied',
        required=True,
        domain="[('invoice_id','=', discounted_invoice_id)]",
        ondelete='cascade',
        index=True)

    discount_id = fields.Many2one(
        comodel_name='account.invoice.discount',
        string='Discount',
        help='The main document which this line is a part of.',
        required=True,
        ondelete='cascade')

    amount = fields.Monetary(
        string='Applied Discount Amount',
        currency_field='company_currency_id',
        help='The amount of discount that has been applied to the discounted invoice line from the discounting invoice, which is present in the discount',
        required=True)

    company_id = fields.Many2one(
        comodel_name='res.company',
        related='discounted_invoice_id.company_id',
        string='Company',
        store=True,
        readonly=True)

    company_currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='company_id.currency_id',
        readonly=True,
        help='Utility field to express amount currency')

    @api.model
    def create(self, values):
        discount_line = super(DiscountLine, self).create(values)
        discount_line.apply_discount()
        return discount_line

    @api.multi
    def unlink(self):
        self.remove_discount()
        return super(DiscountLine, self).unlink()

    @api.constrains('amount')
    def _check_amount(self):
        if self.amount <= 0:
            raise ValidationError(_('Discount line amount is %f, which is not positive. Discount amounts should always be positive.' % self.amount))

    def apply_discount(self):
        _logger.info('Applying discount %f from discounting invoice %s to line %s of invoice %s'
                     %(self.amount, self.discount_id.discounting_invoice_id.number,
                       self.discounted_invoice_line_id.name, self.discounted_invoice_id.number))

        value = self._compute_invoice_line_value_with_all_discounts_applied()
        value_updated = self.discounted_invoice_line_id.modify_stock_move_value(value)

        if not value_updated:
            raise UserError(_('Could not apply discount %f from discounting invoice %s to line %s of invoice %s. '
                              'Probably the stock move was already consumed. You should contact your system administrator.'
                              %(self.amount, self.discount_id.discounting_invoice_id.number,
                                self.discounted_invoice_line_id.name, self.discounted_invoice_id.number)))

    def remove_discount(self):
        _logger.info('Removing discount %f from discounting invoice %s from line %s of invoice %s'
                     % (self.amount, self.discount_id.discounting_invoice_id.number,
                        self.discounted_invoice_line_id.name, self.discounted_invoice_id.number))

        current_value = self._compute_invoice_line_value_with_all_discounts_applied()

        value = current_value + self.amount
        value_updated = self.discounted_invoice_line_id.modify_stock_move_value(value)

        if not value_updated:
            raise UserError(_('Could not remove discount %f from discounting invoice %s from line %s of invoice %s. '
                              'Probably the stock move was already consumed. You should contact your system administrator.'
                              %(self.amount, self.discount_id.discounting_invoice_id.number,
                                self.discounted_invoice_line_id.name, self.discounted_invoice_id.number)))

    def _compute_invoice_line_value_with_all_discounts_applied(self):
        discount_lines_of_invoice_line = self.discounted_invoice_line_id.discount_line_ids
        invoice_line_value_whole = self.discounted_invoice_line_id.price_subtotal

        return invoice_line_value_whole - sum(discount_lines_of_invoice_line.mapped('amount'))
