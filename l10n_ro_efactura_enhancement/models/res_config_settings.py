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
    l10n_ro_spv_cron_report_email = fields.Char(
        string="Email raport cron SPV",
        help="Adrese de email (separate prin virgula) care primesc statistica dupa "
        "fiecare rulare a cronului de trimitere in SPV. Daca e gol, se foloseste "
        "emailul companiei.",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_ro_spv_cron_no_email = fields.Boolean(
        related="company_id.l10n_ro_spv_cron_no_email",
        readonly=False,
        string="Trimite in SPV fara email (cron)",
    )
    l10n_ro_spv_cron_report_email = fields.Char(
        related="company_id.l10n_ro_spv_cron_report_email",
        readonly=False,
        string="Email raport cron SPV",
    )
