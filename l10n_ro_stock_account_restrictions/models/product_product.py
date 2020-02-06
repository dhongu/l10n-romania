from odoo import models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_fifo_candidates_in_move(self):
        candidates = super(ProductProduct, self)._get_fifo_candidates_in_move()
        _ensure_all_candidates_are_evaluated(candidates)

        return candidates


def _ensure_all_candidates_are_evaluated(candidates):
    if any(candidates.filtered(lambda m: m.value == 0.0)):
        product_name = next(iter(set(candidates.mapped('product_id').mapped('name'))))
        raise UserError(_('You cannot continue this action because there are stock units that have not been evaluated. The culprit is %s') %product_name)