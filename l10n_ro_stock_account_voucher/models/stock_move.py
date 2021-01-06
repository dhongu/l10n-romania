import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    voucher_line_evaluated_by = fields.Many2one(
        comodel_name='account.voucher.line',
        string='Evaluating Voucher Line',
        help='The voucher line that is used to evaluate purchased stock moves',
        readonly=True)
