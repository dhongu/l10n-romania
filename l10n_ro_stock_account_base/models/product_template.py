# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.addons.account.models.product import ACCOUNT_DOMAIN


class ProductTemplate(models.Model):
    _inherit = "product.template"

    l10n_ro_property_stock_valuation_account_id = fields.Many2one(
        "account.account",
        string="Stock Valuation Account",
        ondelete="restrict",
        company_dependent=True,
        domain=ACCOUNT_DOMAIN,
        help="In Romania accounting is only one account for valuation/input/"
        "output. If this value is set, we will use it, otherwise will "
        "use the category value. ",
    )
