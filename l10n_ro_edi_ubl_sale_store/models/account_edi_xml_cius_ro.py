# ©  2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import models


class AccountEdiXmlUBLRO(models.AbstractModel):
    _name = "account.edi.xml.ubl_ro"
    _inherit = "account.edi.xml.ubl_ro"

    def _export_invoice_vals(self, invoice):
        # old helper
        vals_list = super()._export_invoice_vals(invoice)
        if invoice.receipt_print:
            vals_list["vals"]["document_type_code"] = 751
        return vals_list

    def _add_invoice_header_nodes(self, document_node, vals):
        """New helper"""
        res = super()._add_invoice_header_nodes(document_node, vals)
        invoice = vals["invoice"]
        if (
            "receipt_print" in invoice._fields
            and invoice.receipt_print
            and "cbc:InvoiceTypeCode" in document_node
            and document_node["cbc:InvoiceTypeCode"]["_text"] == 380
        ):
            document_node["cbc:InvoiceTypeCode"] = {"_text": 751}

        return res
