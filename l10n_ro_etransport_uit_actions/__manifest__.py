# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "eTransport UIT Actions",
    "version": "19.0.1.0.0",
    "author": "Terrabit, Dorin Hongu",
    "website": "https://www.terrabit.ro",
    "summary": "Delete, confirm or change the vehicle of an ANAF eTransport UIT",
    "countries": ["ro"],
    "category": "Localization",
    "depends": [
        "l10n_ro_etransport_enhancement",
    ],
    "license": "LGPL-3",
    "images": ["static/description/main_screenshot.png"],
    "data": [
        "security/ir.model.access.csv",
        "data/template_etransport_actions.xml",
        "data/ir_cron.xml",
        "views/etransport_event_view.xml",
        "wizards/etransport_action_wizard_view.xml",
        "views/stock_picking_view.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["dhongu"],
    "extra_buy": True,
}
