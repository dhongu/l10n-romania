
from odoo import models

class ProductProduct(models.Model):
    _inherit = "product.product"

    def write(self, vals):
        if "standard_price" in vals:
            if vals["standard_price"] <= 0:
                raise ValueError("Standard price must be greater than zero.")
        return super().write(vals)
