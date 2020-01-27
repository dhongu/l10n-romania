from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_fifo_candidates_in_move(self):
        """ Find IN moves that can be used to value OUT moves.
                """
        _logger.info(_('Filtering out candidates that have not been evaluated yet'))
        candidates = super(ProductProduct, self)._get_fifo_candidates_in_move()
        return candidates.filtered(lambda m: m.value != 0.0)
