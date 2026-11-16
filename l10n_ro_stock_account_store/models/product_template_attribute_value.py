# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    def write(self, vals):
        res = super().write(vals)
        if "price_extra" in vals:
            products = self.env["product.product"].search([("product_template_variant_value_ids", "in", self.ids)])
            self.env["l10n.ro.store.revaluation"]._l10n_ro_revaluate_products(products)
        return res
