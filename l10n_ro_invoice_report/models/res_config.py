# ©  2015-2023 Deltatech
# See README.rst file on addons root folder for license details


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    email_on_invoice_address = fields.Boolean(
        string="Show email", help="Show email on invoice address"
    )
    phone_on_invoice_address = fields.Boolean(
        string="Show phone", help="Show phone on invoice address"
    )
    marker_on_invoice_address = fields.Boolean(
        string="Show marker", help="Show marker on invoice address"
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    email_on_invoice_address = fields.Boolean(
        related="company_id.email_on_invoice_address",
        string="Show email",
        readonly=False,
        help="Show taxes values on reception report",
    )
    phone_on_invoice_address = fields.Boolean(
        related="company_id.phone_on_invoice_address",
        string="Show phone ",
        readonly=False,
        help="Show phone on invoice address",
    )
    marker_on_invoice_address = fields.Boolean(
        related="company_id.marker_on_invoice_address",
        string="Show marker",
        readonly=False,
        help="Show marker on invoice address",
    )
