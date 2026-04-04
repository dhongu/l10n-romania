# ©  2008-2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    partner_lock_with_invoice = fields.Boolean(
        related="company_id.partner_lock_with_invoice",
        readonly=False,
    )
