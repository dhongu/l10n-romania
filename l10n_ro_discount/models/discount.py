from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class Discount(models.Model):
    _name = 'account.invoice.discount'
    _description = 'Discount'
    _sql_constraints = [
        ('unique_invoice', 'UNIQUE(discounting_invoice_id)', _("There is already a discount for this invoice"))
    ]

    discounting_invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Discount invoice',
        help='The invoice that contains one or more lines that are discounts',
        required=True,
        ondelete='cascade',
        index=True
    )
    discount_line_ids = fields.One2many(
        comodel_name='account.invoice.discount.line',
        inverse_name='discount_id',
        string='Discount Lines',
        help='Discount lines. The sum of their amount should be equal to the initial_amount field.'
    )
    initial_amount = fields.Monetary(
        string='Initial Discount',
        currency_field='company_currency_id',
        help='Total amount of discount',
        required=True
    )
    remaining_amount = fields.Monetary(
        string='Remaining Discount',
        currency_field='company_currency_id',
        help='Amount of discount that is left to be applied to invoice lines',
        compute='_compute_remaining_amount'
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        related='discounting_invoice_id.company_id',
        string='Company',
        store=True,
        readonly=True
    )
    company_currency_id = fields.Many2one(
        comodel_name= 'res.currency',
        related='company_id.currency_id',
        readonly=True,
        help='Utility field to express amount currency'
    )
    state = fields.Selection(
        selection = [('open', 'Open'), ('applied', 'Applied')],
        string='State',
        default='open',
        help='If the entire initial amount has been applied, then the state is Applied. Otherwise, Opened',
        compute='_compute_state'
    )

    @api.multi
    def unlink(self):
        for discount_line in self.discount_line_ids:
            discount_line.remove_discount()
        return super(Discount, self).unlink()

    @api.constrains('initial_amount')
    def _check_initial_amount(self):
        if self.initial_amount <= 0:
            raise ValidationError(_('Initial amount is %d, which is not positive. Discount amounts should always be positive.' %self.initial_amount))

    @api.constrains('discount_line_ids')
    def _check_discount_line_ids(self):
        total_applied = sum(self.discount_line_ids.mapped('amount'))
        if self.initial_amount < total_applied:
            _logger.info('Discount application failed for %s because an amount greater than initial amount has been tried to be applied.' %self.discounting_invoice_id.number)
            raise UserError(_('You are trying to apply a total discount of %d, which is more than the initial value of %d' %(total_applied, self.initial_amount)))

    @api.depends('discount_line_ids', 'initial_amount')
    def _compute_remaining_amount(self):
        for discount in self:
            total_applied = sum(discount.discount_line_ids.mapped('amount'))
            discount.remaining_amount = discount.initial_amount - total_applied

    @api.depends('remaining_amount')
    def _compute_state(self):
        for discount in self:
            discount.state = 'applied' if discount.remaining_amount == 0 else 'open'

    @api.onchange('discounting_invoice_id')
    def _when_onchange_invoice(self):
        self._ensure_no_lines_exist()
        self._update_amounts()

    def _ensure_no_lines_exist(self):
        if len(self.discount_line_ids) != 0:
            raise UserError(_('Discount invoice cannot be changed when there are discount lines already. Delete them first.'))

    def _update_amounts(self):
        discount_received_account = self.company_id.property_trade_discount_received_account_id
        discount_amount = sum(self.discounting_invoice_id.invoice_line_ids \
                              .filtered(lambda l: l.account_id == discount_received_account) \
                              .mapped('price_total'))
        self.initial_amount = -discount_amount