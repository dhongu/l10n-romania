from odoo import models, fields

import logging
_logger = logging.getLogger(__name__)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    discount_line_ids = fields.One2many(
        comodel_name='account.invoice.discount.line',
        inverse_name='discounted_invoice_line_id',
        string='Discount Lines',
        help='Discount lines that have been applied to this invoice line')