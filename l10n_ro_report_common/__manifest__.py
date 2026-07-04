# © 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Romania - Report Common",
    "summary": "Common QWeb building blocks for Romanian printed reports:"
    " company bank accounts and company identification header",
    "version": "18.0.1.0.0",
    "category": "Localization",
    "author": "Terrabit, Dorin Hongu, Odoo Community Association (OCA)",
    "maintainers": ["dhongu"],
    "website": "https://github.com/OCA/l10n-romania",
    "countries": ["ro"],
    "depends": ["l10n_ro"],
    "data": [
        "views/report_templates.xml",
        "views/res_partner_bank_views.xml",
        "views/res_company_views.xml",
    ],
    "license": "AGPL-3",
    "development_status": "Mature",
    "installable": True,
}
