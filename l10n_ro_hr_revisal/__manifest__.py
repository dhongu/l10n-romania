# ©  2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "HR Revisal",
    "version": "17.0.0.0.1",
    "author": "Terrabit, Dorin Hongu, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "summary": "Import revisal Data",
    "countries": ["ro"],
    "category": "Localization",
    "depends": [
        "hr",
    ],
    "license": "LGPL-3",
    "price": 25.00,
    "currency": "EUR",
    "data": [
        "wizard/hr_employee_revisal_view.xml",
        "security/ir.model.access.csv",
        "views/hr_job_view.xml",
    ],
    "images": ["static/description/main_screenshot.png"],
    "development_status": "Beta",
    "maintainers": ["dhongu"],
    "extra_buy": True,
}
