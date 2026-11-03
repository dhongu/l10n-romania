# Copyright (C) 2019 NextERP Romania
# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_ro_usage_location_id = fields.Many2one(
        "stock.location",
        string="Usage Location",
        readonly=True,
        copy=False,
        domain=[("usage", "=", "usage_giving")],
    )
    l10n_ro_consume_location_id = fields.Many2one(
        "stock.location",
        string="Consume Location",
        readonly=True,
        copy=False,
        domain=[("usage", "=", "consume")],
    )

    def _l10n_ro_stock_is_romanian(self):
        self.ensure_one()
        return self.account_fiscal_country_id.code == "RO"

    @api.model
    def l10n_ro_create_missing_stock_locations(self):
        """Create the usage and consume locations of the Romanian companies that
        do not have them yet (a database may already have them from OCA
        ``l10n_ro_stock``)."""
        companies = self.search([("account_fiscal_country_id.code", "=", "RO")])
        companies._l10n_ro_create_stock_locations()

    def _l10n_ro_create_stock_locations(self):
        locations = self.env["stock.location"]
        for company in self:
            if not company.l10n_ro_usage_location_id:
                usage = locations.search(
                    [("usage", "=", "usage_giving"), ("company_id", "=", company.id)],
                    limit=1,
                ) or locations.create(
                    {
                        "name": self.env._("Usage"),
                        "usage": "usage_giving",
                        "company_id": company.id,
                    }
                )
                company.l10n_ro_usage_location_id = usage
            if not company.l10n_ro_consume_location_id:
                consume = locations.search(
                    [("usage", "=", "consume"), ("company_id", "=", company.id)],
                    limit=1,
                ) or locations.create(
                    {
                        "name": self.env._("Consume"),
                        "usage": "consume",
                        "company_id": company.id,
                    }
                )
                company.l10n_ro_consume_location_id = consume

    def _create_per_company_locations(self):
        res = super()._create_per_company_locations()
        for company in self:
            if company._l10n_ro_stock_is_romanian():
                company._l10n_ro_create_stock_locations()
        return res
