# © 2026 Terrabit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "Romania - Service Taxes",
    "summary": "Default sale and purchase taxes for service products",
    "version": "20.0.1.0.0",
    "category": "Localization",
    "author": "Terrabit, Dorin Hongu",
    "maintainers": ["dhongu"],
    "website": "https://www.terrabit.ro",
    "countries": ["ro"],
    "depends": ["l10n_ro"],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "images": ["static/description/main_screenshot.png"],
    "license": "LGPL-3",
    "development_status": "Beta",
    "installable": True,
}
