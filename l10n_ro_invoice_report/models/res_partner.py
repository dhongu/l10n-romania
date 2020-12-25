# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    info_for_invoice = fields.Html(string="Additional info for invoice")
