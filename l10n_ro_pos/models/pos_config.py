# ©  2015-2018 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    is_installed_account_accountant = fields.Boolean(
        compute="_compute_is_installed_account_accountant"
    )

    def _compute_is_installed_account_accountant(self):
        for pos_config in self:
            pos_config.is_installed_account_accountant = True
