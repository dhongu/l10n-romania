# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def write(self, vals):
        res = super().write(vals)
        if "list_price" in vals:
            self.env["l10n.ro.store.revaluation"]._l10n_ro_revaluate_products(self.product_variant_ids)
        return res

    def _get_product_accounts(self):
        accounts = super()._get_product_accounts()
        company = self.company_id or self.env.company
        if company.l10n_ro_accounting:
            accounts["l10n_ro_store_markup"] = self.categ_id.l10n_ro_property_store_markup_account_id
            accounts["l10n_ro_uneligible_tax"] = (
                self.categ_id.l10n_ro_property_store_uneligible_tax_account_id
                or company.l10n_ro_property_uneligible_tax_account_id
            )
        return accounts
