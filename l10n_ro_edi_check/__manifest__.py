# ©  2024-now Dan Stoica <danila(@)terrabit(.)ro
# See README.rst file on addons root folder for license details
{
    "name": "Romania - EDI data check and queue",
    "license": "AGPL-3",
    "version": "14.0.0.0.4",
    "author": "Terrabit," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "category": "Tools",
    "depends": [
        "l10n_ro_account_edi_ubl",
        "queue_job",
        "queue_job_cron_jobrunner",
    ],
    "data": [
        "data/cron.xml",
        "views/account_move.xml",
    ],
    "installable": True,
}
