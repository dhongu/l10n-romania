# ©  2008-2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    partner_lock_with_invoice = fields.Boolean(
        string="Lock Partner with Invoice",
        help="If enabled, it is not possible to change the type of contact or the VAT "
        "if there are already invoices on it.",
        default=False,
    )
