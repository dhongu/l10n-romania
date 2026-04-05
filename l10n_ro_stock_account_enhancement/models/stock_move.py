# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import models
from odoo.exceptions import UserError
from odoo.tools.convert import safe_eval


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_price_unit(self):
        price = super()._get_price_unit()
        get_param = self.env["ir.config_parameter"].sudo().get_param
        skip_price_unit_check = get_param("l10n_ro_stock_account.skip_price_unit_check", default="False")
        skip_price_unit_check = safe_eval(skip_price_unit_check)
        if skip_price_unit_check:
            return price
        if not price:
            product = self.product_id
            raise UserError(self.env._(f"Price unit is not set for product {product.name}"))

        return price
