# ©  2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "eTransport Enhancement",
    "version": "19.0.0.7.0",
    "author": "Terrabit, Dorin Hongu, Odoo Community Association (OCA)",
    "website": "https://www.terrabit.ro",
    "summary": "eTransport enhancement",
    "countries": ["ro"],
    "category": "Localization",
    "depends": [
        "l10n_ro_edi",
        "l10n_ro_edi_stock",
    ],
    "license": "LGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "data/template_etransport.xml",
        "views/stock_picking_view.xml",
        "views/res_config_view.xml",
    ],
    "images": ["static/description/main_screenshot.png"],
    "development_status": "Mature",
    "maintainers": ["dhongu"],
    "extra_buy": True,
    "post_init_hook": "post_init_hook",
}
