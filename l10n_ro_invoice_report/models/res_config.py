# ©  2015-2023 Deltatech
# See README.rst file on addons root folder for license details


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    email_on_invoice_address = fields.Boolean(string="Show email", help="Show email on invoice address")
    phone_on_invoice_address = fields.Boolean(string="Show phone", help="Show phone on invoice address")
    marker_on_invoice_address = fields.Boolean(string="Show marker", help="Show marker on invoice address")
    index_line_on_invoice = fields.Boolean(string="Show index line", help="Show index line on invoice")
    show_total_amount_with_taxes = fields.Boolean(
        string="Show total amount with taxes", help="Show total amount with taxes"
    )
    hide_invoice_payment_communication = fields.Boolean(string="Hide invoice payment communication")
    hide_pickings_in_invoice = fields.Boolean(string="Hide picking in invoice")
    remove_product_name_from_invoice_line = fields.Boolean(string="Remove product name from invoice line")
    show_invoice_delegate = fields.Boolean(string="Show invoice delegate")


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

    index_line_on_invoice = fields.Boolean(
        related="company_id.index_line_on_invoice",
        string="Show index line",
        readonly=False,
        help="Show index line on invoice",
    )
    show_total_amount_with_taxes = fields.Boolean(
        related="company_id.show_total_amount_with_taxes",
        string="Show total amount with taxes",
        readonly=False,
        help="Show total amount with taxes",
    )

    hide_invoice_payment_communication = fields.Boolean(
        related="company_id.hide_invoice_payment_communication", string="Hide invoice comments", readonly=False
    )

    hide_pickings_in_invoice = fields.Boolean(
        related="company_id.hide_pickings_in_invoice", string="Show picking in invoice", readonly=False
    )

    remove_product_name_from_invoice_line = fields.Boolean(
        related="company_id.remove_product_name_from_invoice_line",
        string="Remove product name from invoice line if line has description",
        readonly=False,
    )
    show_invoice_delegate = fields.Boolean(
        related="company_id.show_invoice_delegate", string="Show invoice delegate", readonly=False
    )
