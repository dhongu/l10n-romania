# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_price_unit(self, product=None, include_consigned=False, include_consumable=False):
        price = super()._get_price_unit(
            product=product, include_consigned=include_consigned, include_consumable=include_consumable
        )
        # In 19.0 the COGS of an invoice line used `_get_cogs_price_unit` (not checked here);
        # in 20.0 it goes through `_get_price_unit(include_consigned=True)`: keep it unchecked.
        if include_consigned:
            return price
        skip_price_unit_check = (
            self.env["ir.config_parameter"].sudo().get_bool("l10n_ro_stock_account.skip_price_unit_check")
        )
        if skip_price_unit_check:
            return price
        if not price:
            product = product or self.product_id
            raise UserError(
                self.env._("Price unit is not set for product %s", ", ".join(product.mapped("display_name")))
            )

        return price
