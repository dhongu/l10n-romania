import base64
from xml.sax.saxutils import escape, quoteattr

from lxml import etree

from odoo import api, fields, models
from odoo.tools import cleanup_xml_node


class AccountMoveSend(models.TransientModel):
    _inherit = "account.move.send"

    l10n_ro_edi_resend_enable = fields.Boolean(compute="_compute_l10n_ro_edi_resend_enable")

    @api.depends("l10n_ro_edi_send_enable")
    def _compute_l10n_ro_edi_resend_enable(self):
        for wizard in self:
            wizard.l10n_ro_edi_resend_enable = any(
                not move._need_ubl_cii_xml() and move.country_code == "RO" and move.invoice_pdf_report_id
                for move in wizard.move_ids
            )

    def action_resend(self):
        self.ensure_one()
        invoice_pdf_report_ids = self.move_ids.mapped("invoice_pdf_report_id")
        invoice_pdf_report_ids.unlink()

        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "views": [(False, "form")],
            "target": "new",
        }

    def _compute_l10n_ro_edi_send_enable(self):
        res = super()._compute_l10n_ro_edi_send_enable()
        for wizard in self:
            wizard.l10n_ro_edi_send_enable = wizard.l10n_ro_edi_send_enable and any(
                move.commercial_partner_id.country_id.code == "RO" for move in wizard.move_ids
            )
        return res

    @api.model
    def _postprocess_invoice_ubl_xml(self, invoice, invoice_data):
        # Adding the PDF to the XML
        # Rewrite to remove <cbc:IssueDate>{invoice.invoice_date}</cbc:IssueDate>
        tree = etree.fromstring(invoice_data["ubl_cii_xml_attachment_values"]["raw"])
        anchor_elements = tree.xpath("//*[local-name()='AccountingSupplierParty']")
        if not anchor_elements:
            return

        xmlns_move_type = "Invoice" if invoice.move_type == "out_invoice" else "CreditNote"
        pdf_values = invoice_data.get("pdf_attachment_values") or invoice_data["proforma_pdf_attachment_values"]
        filename = pdf_values["name"]
        content = pdf_values["raw"]

        doc_type_node = ""
        edi_model = invoice_data["ubl_cii_xml_options"]["builder"]
        doc_type_code_vals = edi_model._get_document_type_code_vals(invoice, invoice_data)
        if doc_type_code_vals["value"]:
            doc_type_code_attrs = " ".join(f'{name}="{value}"' for name, value in doc_type_code_vals["attrs"].items())
            doc_type_node = (
                f"<cbc:DocumentTypeCode {doc_type_code_attrs}>{doc_type_code_vals['value']}</cbc:DocumentTypeCode>"
            )
        to_inject = f"""
                <cac:AdditionalDocumentReference
                    xmlns="urn:oasis:names:specification:ubl:schema:xsd:{xmlns_move_type}-2"
                    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
                    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
                    <cbc:ID>{escape(filename)}</cbc:ID>
                    {doc_type_node}
                    <cac:Attachment>
                        <cbc:EmbeddedDocumentBinaryObject
                            mimeCode="application/pdf"
                            filename={quoteattr(filename)}>
                            {base64.b64encode(content).decode()}
                        </cbc:EmbeddedDocumentBinaryObject>
                    </cac:Attachment>
                </cac:AdditionalDocumentReference>
            """

        anchor_index = tree.index(anchor_elements[0])
        tree.insert(anchor_index, etree.fromstring(to_inject))
        invoice_data["ubl_cii_xml_attachment_values"]["raw"] = etree.tostring(
            cleanup_xml_node(tree), xml_declaration=True, encoding="UTF-8"
        )
