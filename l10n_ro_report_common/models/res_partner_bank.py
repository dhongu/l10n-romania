# © 2026 Terrabit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    # același nume de câmp ca în OCA l10n_ro_config, pentru continuitatea
    # datelor la clienții care migrează de pe stack-ul OCA (aceeași coloană)
    l10n_ro_print_report = fields.Boolean(
        string="Romania - Print in Report",
        help="If checked, this bank account is printed on Romanian report headers.",
    )
