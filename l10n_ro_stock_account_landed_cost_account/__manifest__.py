# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Romania - Stock Accounting Landed Cost Account",
    "version": "19.0.1.1.0",
    "category": "Localization",
    "countries": ["ro"],
    "summary": "Romania - Stock Accounting Landed Cost account determination",
    "author": "Terrabit,Dorin Hongu,Odoo Community Association (OCA)",
    "website": "https://www.terrabit.ro",
    "depends": [
        "stock_landed_costs",
        "l10n_ro_stock_account",
        "l10n_ro_config",
    ],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "development_status": "Mature",
    "maintainers": ["dhongu"],
}
