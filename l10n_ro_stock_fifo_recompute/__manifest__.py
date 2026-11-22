# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Romania - FIFO Valuation Recompute",
    "version": "19.0.1.0.0",
    "category": "Localization",
    "countries": ["ro"],
    "summary": "Recompute the per-location FIFO valuation and post the correction",
    "author": "Terrabit",
    "website": "https://www.terrabit.ro",
    "depends": ["l10n_ro_stock_account"],
    "images": ["static/description/main_screenshot.png"],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "views/fifo_recompute_views.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["dhongu"],
    "consultant_sheet": "full",
}
