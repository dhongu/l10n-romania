# Copyright (C) 2015 Forest and Biomass Romania
# Copyright (C) 2020 NextERP Romania
# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Romania - Partner Base",
    "summary": "Romanian VAT/CUI handling on partners and partner data from ANAF/VIES",
    "license": "AGPL-3",
    "countries": ["ro"],
    "version": "19.0.0.0.1",
    "category": "Localization",
    "author": "Terrabit, Dorin Hongu",
    "maintainers": ["dhongu"],
    "website": "https://www.terrabit.ro",
    "depends": ["l10n_ro"],
    "external_dependencies": {"python": ["requests", "zeep"]},
    "data": [
        "security/ir.model.access.csv",
        "wizard/get_partner_data_views.xml",
        "views/res_partner_view.xml",
        "views/res_company_view.xml",
        "views/res_config_settings_view.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "installable": True,
    "development_status": "Beta",
}
