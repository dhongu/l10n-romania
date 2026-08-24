# ©  2008-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Terrabit Sale Order Report",
    "summary": "Formular Factura Proformae",
    "version": "19.0.1.0.9",
    "author": "Terrabit, Dorin Hongu, Dan Stoica, Odoo Community Association (OCA)",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "countries": ["ro"],
    "depends": [
        "sale",
        "l10n_ro_report_common",
        # "deltatech_sale_payment"  # pentru ce e ?
    ],
    "license": "AGPL-3",
    "data": [
        "views/sale_order.xml",
        "views/res_config_view.xml",
    ],
    "images": ["images/main_screenshot.png"],
    "development_status": "Mature",
}
