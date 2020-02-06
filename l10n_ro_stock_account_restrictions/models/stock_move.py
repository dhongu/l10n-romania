from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _get_price_unit(self):
        self.ensure_one()
        if self.purchase_line_id and self.product_id.id == self.purchase_line_id.product_id.id:
            _logger.info('Returning 0 as price_unit for product %s (%s) in purchase order %s' %(self.product_id.name, self.product_id.default_code, self.purchase_line_id.order_id.name))
            return 0
        return super(StockMove, self)._get_price_unit()
