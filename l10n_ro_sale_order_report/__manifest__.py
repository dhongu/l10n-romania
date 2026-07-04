# ©  2008-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Terrabit Sale Order Report",
    "summary": "Formular Factura Proformae",
    "version": "18.0.1.0.10",
    "author": "Dorin Hongu, Dan Stoica, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "category": "Localization",
    "countries": ["ro"],
    "depends": [
        "sale",
        "l10n_ro_report_common",
        # "deltatech_sale_payment"  # pentru ce e ?
    ],
    "license": "LGPL-3",
    "data": [
        "views/sale_order.xml",
        "views/res_config_view.xml",
    ],
    "images": ["images/main_screenshot.png"],
    "installable": True,
}
