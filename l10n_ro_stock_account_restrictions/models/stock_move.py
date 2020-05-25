from odoo import models, api, _
import logging

from odoo.exceptions import UserError

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

    def _action_done(self):
        res = super(StockMove, self)._action_done()
        inv_location = self.env.ref('stock.location_inventory')
        for move in res.filtered(lambda m: m.location_id == inv_location):
            if (move.value == 0.0):
                raise UserError(_("Cannot validate inventory with product %s that has cost 0") % move.product_id.name)

        return res
