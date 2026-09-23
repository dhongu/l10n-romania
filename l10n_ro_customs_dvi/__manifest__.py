# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
{
    "name": "Romania - Customs Import Declaration (DVI)",
    "summary": "Record the customs import declaration (DVI) as a landed cost: customs duty, commission and import VAT",
    "license": "AGPL-3",
    "version": "19.0.2.0.0",
    "countries": ["ro"],
    "author": "Terrabit",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "depends": [
        "stock_account",
        "account",
        "sale",
        "l10n_ro",  # pentru determinarea contului 446
        "purchase_stock",
        "stock_landed_costs",
    ],
    "excludes": ["l10n_ro_dvi"],
    "data": [
        "views/account_invoice_view.xml",
        "views/stock_landed_cost_view.xml",
        "wizard/account_dvi_view.xml",
        "security/ir.model.access.csv",
    ],
    "pre_init_hook": "pre_init_hook",
    "installable": True,
    "development_status": "Production/Stable",
}
