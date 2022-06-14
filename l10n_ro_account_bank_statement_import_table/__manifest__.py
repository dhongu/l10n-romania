# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Import CSV Bank Statement",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Terrabit,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "depends": ["account_bank_statement_import", "base_import"],
    "data": [
        "views/account_bank_statement_import_templates.xml",
    ],
    "installable": True,
    "auto_install": False,
    "maintainers": ["dhongu"],
    "development_status": "Alpha",
}
