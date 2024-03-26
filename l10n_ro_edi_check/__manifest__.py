# ©  2024-now Dan Stoica <danila(@)terrabit(.)ro
# See README.rst file on addons root folder for license details
{
    "name": "Romania - EDI data check",
    "license": "AGPL-3",
    "version": "14.0.0.1.0",
    "author": "Terrabit," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "category": "Tools",
    "depends": [
        "l10n_ro_account_edi_ubl",
    ],
    "data": [
        "data/ir_cron.xml",
        "views/account_move.xml",
    ],
    "installable": True,
}
