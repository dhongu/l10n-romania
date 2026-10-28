# ©  2015-2022 Deltatech
# See README.rst file on addons root folder for license details


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    taxes_on_reception = fields.Boolean(
        string="Show taxes on reception report",
        default=True,
        help="Show taxes values on reception report",
    )
    banks_on_pickings = fields.Boolean(
        string="Show banks on picking report",
        default=True,
        help="Show banks on picking report",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    taxes_on_reception = fields.Boolean(
        related="company_id.taxes_on_reception",
        string="Show taxes on reception report",
        readonly=False,
        help="Show taxes values on reception report",
    )
    banks_on_pickings = fields.Boolean(
        related="company_id.banks_on_pickings",
        string="Show banks on picking report",
        readonly=False,
        help="Show banks on picking report",
    )
