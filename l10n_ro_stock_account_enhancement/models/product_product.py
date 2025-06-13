from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def write(self, vals):
        if "standard_price" in vals:
            self = self.with_context(disable_auto_svl=True)
            # if vals["standard_price"] <= 0:
            #     raise ValueError("Standard price must be greater than zero.")
        return super().write(vals)
