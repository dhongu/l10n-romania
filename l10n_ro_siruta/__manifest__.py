# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Romania - Siruta",
    "summary": "Romania - Siruta",
    "version": "13.0.1.0.0",
    "category": "Localization",
    "author": "Terrabit," "NextERP Romania, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-romania",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["contacts", "l10n_ro_city"],
    "data": [
        "views/partner_view.xml",
        "views/siruta_view.xml",
        "views/assets.xml",
        "security/ir.model.access.csv",
    ],
    "post_init_hook": "post_init_hook",
    "maintainers": ["dhongu"],
}
