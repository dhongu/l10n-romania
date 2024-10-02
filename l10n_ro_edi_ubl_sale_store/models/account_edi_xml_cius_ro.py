# ©  2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import models


class AccountEdiXmlCIUSRO(models.Model):
    _inherit = "account.edi.xml.cius_ro"

    def _export_invoice_vals(self, invoice):
        vals_list = super()._export_invoice_vals(invoice)
        if invoice.receipt_print:
            vals_list["vals"]["invoice_type_code"] = 751
        return vals_list
