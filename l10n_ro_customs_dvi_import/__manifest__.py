# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Romania - Import DVI from the SNI PDF",
    "summary": "Fill in the DVI wizard from the customs import declaration PDF printed by the National Import System (SNI)",
    "license": "AGPL-3",
    "version": "19.0.1.1.0",
    "countries": ["ro"],
    "author": "Terrabit",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "depends": ["l10n_ro_customs_dvi"],
    "external_dependencies": {"python": ["pdfminer.six"]},
    "data": ["wizard/account_dvi_view.xml"],
    "images": ["static/description/main_screenshot.png"],
    "installable": True,
    "development_status": "Beta",
}
