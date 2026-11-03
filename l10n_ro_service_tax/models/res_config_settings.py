# © 2026 Terrabit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # aceleași nume ca în OCA l10n_ro_config: cele două module pot sta instalate împreună
    l10n_ro_serv_sale_tax_id = fields.Many2one(
        "account.tax",
        related="company_id.l10n_ro_account_serv_sale_tax_id",
        readonly=False,
    )
    l10n_ro_serv_purchase_tax_id = fields.Many2one(
        "account.tax",
        related="company_id.l10n_ro_account_serv_purchase_tax_id",
        readonly=False,
    )
