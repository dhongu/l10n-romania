# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "eTransport UIT Actions - Batch",
    "version": "19.0.1.0.0",
    "author": "Terrabit, Dorin Hongu",
    "website": "https://www.terrabit.ro",
    "summary": "Delete, confirm or change the vehicle of a UIT issued for a transfer batch",
    "countries": ["ro"],
    "category": "Localization",
    "depends": [
        "l10n_ro_etransport_uit_actions",
        "l10n_ro_edi_stock_batch",
    ],
    "license": "LGPL-3",
    "data": [
        "views/etransport_event_view.xml",
        "views/stock_picking_batch_view.xml",
    ],
    "auto_install": True,
    "development_status": "Beta",
    "maintainers": ["dhongu"],
}
