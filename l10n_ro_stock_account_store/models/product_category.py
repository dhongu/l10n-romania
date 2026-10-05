# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    l10n_ro_property_store_markup_account_id = fields.Many2one(
        "account.account",
        string="Romania - Store Markup Account",
        company_dependent=True,
        ondelete="restrict",
        help="Trade markup account (378) used when the goods enter or leave a location valued at sale price (store).",
    )
    l10n_ro_property_store_uneligible_tax_account_id = fields.Many2one(
        "account.account",
        string="Romania - Store Uneligible VAT Account",
        company_dependent=True,
        ondelete="restrict",
        help="Uneligible VAT account (4428) for the goods kept at sale price. "
        "Use a dedicated analytic account (e.g. 4428.02) to keep it apart from "
        "the VAT on payment. If empty, the Not Eligible Tax Account of the "
        "company is used.",
    )
