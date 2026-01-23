# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    info_for_invoice = fields.Html(string="Additional info for invoice")
    mean_transp = fields.Char(string="Mean transport")
    payment_bank_id = fields.Many2one(
        "res.partner.bank",
        company_dependent=True,
        domain="['|', ('company_id', '=', company_id), ('company_id', '=', False)]",
        help="The bank account in which this partner will pay."
        "Will be sent in the SPV and will be printed on the invoice",
    )
