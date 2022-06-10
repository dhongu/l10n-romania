# ©  2015-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _prepare_in_svl_vals(self, quantity, unit_cost):
        vals = super(ProductProduct, self)._prepare_in_svl_vals(quantity, unit_cost)
        if self.env.context.get("use_move_price_unit", False):
            move = self.env.context["move"]
            price = move._get_price_unit()
            vals["value"] = vals["quantity"] * price
            vals["unit_cost"] = price

        return vals

    def _prepare_out_svl_vals(self, quantity, company):
        vals = super(ProductProduct, self)._prepare_out_svl_vals(quantity, company)
        if self.env.context.get("use_move_price_unit", False):
            move = self.env.context["move"]
            price = -1 * move._get_price_unit_from_svl()
            vals["value"] = vals["quantity"] * price
            vals["unit_cost"] = price
        return vals
