# ©  2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "eFactura Enhancement",
    "version": "19.0.0.3.16",
    "author": "Terrabit, Dorin Hongu, Odoo Community Association (OCA)",
    "website": "https://www.terrabit.ro",
    "summary": "eFactura Enhancement",
    "countries": ["ro"],
    "category": "Localization",
    "depends": [
        "l10n_ro_edi",
        "l10n_ro_config",
        "spreadsheet_dashboard",
        "l10n_ro_message_spv",
        "account_edi_ubl_cii",
        "spreadsheet_dashboard_account",
        # "l10n_ro_efactura",
    ],
    "license": "AGPL-3",
    # "price": 25.00,
    # "currency": "EUR",
    "data": [
        # "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "data/efactura_spreadsheet_dashboard.xml",
        "data/ir_cron.xml",
        "data/server_action.xml",
        "data/mail_template_spv_cron_report.xml",
        "views/account_move.xml",
        "views/res_config_settings_views.xml",
        # "views/efactura_dashboard_views.xml",  # TODO: re-activat după testare pe live
    ],
    "oca_data_manual": [
        "data/efactura_spreadsheet_dashboard.xml",
        "views/efactura_dashboard_views.xml",
    ],
    "images": ["static/description/main_screenshot.png"],
    "development_status": "Production/Stable",
    "maintainers": ["dhongu"],
    "extra_buy": True,
}
