from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    battery_type = fields.Selection(
        [("new", "New battery"), ("old", "Old battery"), ("waste", "Waste")], string="Battery Type"
    )


class ProductTemplate(models.Model):
    _inherit = "product.template"

    old_product_id = fields.Many2one("product.product")
