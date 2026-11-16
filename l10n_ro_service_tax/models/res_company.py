# © 2026 Terrabit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    # aceleași nume de câmp ca în OCA l10n_ro_config, pentru continuitatea
    # datelor la clienții care migrează de pe stack-ul OCA (aceeași coloană)
    l10n_ro_account_serv_sale_tax_id = fields.Many2one(
        "account.tax",
        string="Default Services Sale Tax",
        help="Sale tax set on a product when its type becomes Service.",
    )
    l10n_ro_account_serv_purchase_tax_id = fields.Many2one(
        "account.tax",
        string="Default Services Purchase Tax",
        help="Purchase tax set on a product when its type becomes Service.",
    )
