# © 2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Self-Billing Message SPV",
    "version": "19.0.1.0.0",
    "author": "Terrabit, Dorin Hongu, Odoo Community Association (OCA)",
    "website": "https://www.terrabit.ro",
    "summary": "Number self-billed documents with the number allocated by the customer, taken from the SPV message",
    "countries": ["ro"],
    "category": "Localization",
    "depends": ["l10n_ro_message_spv"],
    "license": "AGPL-3",
    "support": "support@terrabit.ro",
    "data": [
        "views/account_journal_views.xml",
    ],
    "development_status": "Production/Stable",
    "maintainers": ["dhongu"],
}
