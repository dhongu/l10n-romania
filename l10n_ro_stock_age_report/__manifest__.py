# Copyright (C) 2022 NextERP Romania
# Copyright (C) 2022 Saai SOFT
# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Romania - Stock Aged Report",
    "version": "19.0.0.0.3",
    "category": "Localization",
    "summary": "Romania - Stock Aged Report",
    "author": "Terrabit, NextERP Romania,Dakai Soft,Terrabit,Odoo Community Association (OCA)",
    "website": "https://www.terrabit.ro",
    # doar stock_account (core) e necesar: property_stock_valuation_account_id pe
    # categorie; câmpul OCA per-produs e citit defensiv cu hasattr în wizard
    "depends": ["stock_account"],
    "development_status": "Production/Stable",
    "license": "AGPL-3",
    "data": [
        "wizard/stock_age_report.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
    "maintainers": ["feketemihai", "mcojocaru", "adrian-dks", "dhongu"],
}
