# ©  2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_ro_spv_cron_no_email = fields.Boolean(
        string="Trimite in SPV fara email (cron)",
        default=False,
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_ro_spv_cron_no_email = fields.Boolean(
        related="company_id.l10n_ro_spv_cron_no_email",
        readonly=False,
        string="Trimite in SPV fara email (cron)",
    )
