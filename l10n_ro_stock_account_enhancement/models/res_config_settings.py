# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_ro_check_storable_line_source = fields.Boolean(
        string="Check storable product line source",
        config_parameter="l10n_ro_stock_account.check_storable_line_source",
        help="Check if storable product lines have a reference to a sales or purchase order line.",
    )
