# © 2009-2016 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class res_company(models.Model):
    _inherit = "res.company"

    @api.multi
    def _compute_multi_curr_enable(self):
        "check if multi company currency is enabled"
        company_currency = self.env["res.currency"].search([])
        for company in self:
            company.multi_company_currency_enable = 1 if company_currency else 0

    @api.one
    def button_refresh_currency(self):
        self.services_to_use.refresh_currency()

    # Function field that allows to know the
    # multi company currency implementation
    multi_company_currency_enable = fields.Boolean(
        string="Multi company currency",
        translate=True,
        compute="_compute_multi_curr_enable",
        help="When this option is unchecked it will allow users " "to set a distinct currency updates on each company.",
    )

    # Activate the currency update
    auto_currency_up = fields.Boolean(
        string="Automatic Currency Rates Download",
        default=True,
        help="Automatic download of currency rates for this company",
    )

    services_to_use = fields.One2many("currency.rate.update.service", "company_id", string="Currency update services")
