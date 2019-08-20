from odoo import models, api, fields, _
import logging

_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    has_discounting_invoice_lines = fields.Boolean(
        string='Is discount invoice',
        help='Evaluates to true if there is at least one line with account set to the received-discount account',
        compute='_compute_has_discounting_invoice_lines'
    )
    has_discounted_invoice_lines = fields.Boolean(
        string='Is discount invoice',
        help='Evaluates to true if there is at least one line that was discounted',
        compute='_compute_has_discounted_invoice_lines'
    )

    @api.depends('invoice_line_ids')
    def _compute_has_discounting_invoice_lines(self):
        discount_received_account = self.company_id.property_trade_discount_received_account_id
        discounting_invoice_lines = self.invoice_line_ids.filtered(lambda l: l.account_id == discount_received_account)
        self.has_discounting_invoice_lines = any(discounting_invoice_lines)

    @api.depends('invoice_line_ids')
    def _compute_has_discounted_invoice_lines(self):
        if self.invoice_line_ids:
            ids_of_invoice_lines = self.invoice_line_ids.mapped('id')
            discount_lines = self.env['account.invoice.discount.line'].search([('discounted_invoice_line_id', 'in', ids_of_invoice_lines)])
            self.has_discounted_invoice_lines = any(discount_lines)
        else:
            self.has_discounted_invoice_lines = False

    @api.multi
    def button_discount_from(self):
        discount = self.env['account.invoice.discount'].search([('discounting_invoice_id', '=', self.id)])
        if discount:
            return _open_existing_discount(discount.id)
        else:
            return _open_form_for_new_discount(self.id)

    @api.multi
    def button_discount_to(self):
        ids_of_invoice_lines = self.invoice_line_ids.mapped('id')
        discount_lines = self.env['account.invoice.discount.line'].search([('discounted_invoice_line_id', 'in', ids_of_invoice_lines)])
        ids_of_discounts = list(set(discount_lines.mapped('discount_id').mapped('id')))
        if len(ids_of_discounts) == 1:
            return _open_existing_discount(ids_of_discounts[0])
        else:
            return _open_list_of_discounts(ids_of_discounts)

    @api.multi
    def trade_discount_distribution(self, res):
        _logger.info('trade_discount_distribution() from l10n_ro_stock_account has been called but do not do anything because this module is installed')
        return res


def _open_existing_discount(discount_id):
    return {
        'name': _('Discounts'),
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'account.invoice.discount',
        'type': 'ir.actions.act_window',
        'res_id': discount_id
    }

def _open_form_for_new_discount(default_discounting_invoice_id):
    return {
        'name': _('Discounts'),
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'account.invoice.discount',
        'type': 'ir.actions.act_window',
        'context': {'default_discounting_invoice_id': default_discounting_invoice_id}
    }

def _open_list_of_discounts(ids_of_discounts):
    return {
        'name': _('Discounts'),
        'view_type': 'list',
        'view_mode': 'list',
        'res_model': 'account.invoice.discount',
        'type': 'ir.actions.act_window',
        'domain': [('id', 'in', ids_of_discounts)]
    }