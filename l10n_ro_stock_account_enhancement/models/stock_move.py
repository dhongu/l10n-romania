from odoo import _, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_price_unit(self):
        price = super()._get_price_unit()

        if not price:
            product = self.product_id
            raise UserError(_(f"Price unit is not set for product {product.name}"))

        return price
