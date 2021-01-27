# ©  2017 Deltatech
# See README.rst file on addons root folder for license details


from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    vat_subjected = fields.Boolean("VAT Legal Statement")
    split_vat = fields.Boolean("Split VAT")
    vat_on_payment = fields.Boolean("VAT on Payment")
