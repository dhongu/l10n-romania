# © 2026 Terrabit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "Romania - Report Common",
    "summary": "Common QWeb building blocks for Romanian printed reports:"
    " company bank accounts and company identification header",
    "version": "19.0.1.0.0",
    "category": "Localization",
    "author": "Terrabit, Dorin Hongu",
    "maintainers": ["dhongu"],
    "website": "https://www.terrabit.ro",
    "countries": ["ro"],
    "depends": ["l10n_ro"],
    "data": [
        "views/report_templates.xml",
        "views/res_partner_bank_views.xml",
        "views/res_company_views.xml",
    ],
    "license": "LGPL-3",
    "development_status": "Mature",
    "installable": True,
}
