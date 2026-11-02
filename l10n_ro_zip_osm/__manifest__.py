# Copyright (C) 2026 Terrabit
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
# The street data in data/res_zip_osm.sql is © OpenStreetMap contributors, under the ODbL.

{
    "name": "Romania - Postal Codes, Streets of Small Towns",
    "summary": "Streets of the Romanian towns with a single postal code, from OpenStreetMap",
    "countries": ["ro"],
    "images": ["static/description/main_screenshot.png"],
    "license": "LGPL-3",
    "version": "19.0.1.0.0",
    "author": "Terrabit",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "depends": ["l10n_ro_zip"],
    "data": [],
    "development_status": "Beta",
    "installable": True,
    "auto_install": True,
    "maintainers": ["dhongu"],
    "post_init_hook": "post_init_hook",
}
