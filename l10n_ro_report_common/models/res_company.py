# © 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    # același nume de câmp ca în OCA l10n_ro_config, pentru continuitatea
    # datelor la clienții care migrează de pe stack-ul OCA (aceeași coloană)
    l10n_ro_share_capital = fields.Float(
        string="Share Capital",
        digits="Account",
        help="Company share capital, printed on Romanian report headers.",
    )
