import requests
from lxml import etree

from odoo import _, api, models
from odoo.exceptions import UserError

from odoo.addons.l10n_ro_efactura.models.ciusro_document import NS_UPLOAD, make_efactura_request


class L10nRoEdiDocument(models.Model):
    _inherit = "l10n_ro_edi.document"

    @api.model
    def _request_ciusro_send_invoice(self, company, xml_data, move_type="out_invoice"):
        """
        This method makes an 'upload' request to send xml_data to Romanian SPV.Based on the result, it will then process
        the answer and return a dictionary, which may consist of either an 'error' or a 'key_loading' string.

        :param company: ``res.company`` object
        :param xml_data: String of XML data to be sent
        :param move_type: ``move_type`` field from ``account.move`` object, used for the request parameter
        :return: Result dictionary -> {'error': <str>} | {'key_loading': <str>}
        """
        if not self.invoice_id:
            invoice_id = self.env.context.get("active_id", False)
            if invoice_id:
                invoice = self.env["account.move"].browse(invoice_id)
            else:
                raise UserError(_("Invoice not found!"))
        else:
            invoice = self.invoice_id
        if invoice.commercial_partner_id.is_company:
            endpoint = "upload"
        else:
            endpoint = "uploadb2c"

        result = make_efactura_request(
            session=requests,
            company=company,
            endpoint=endpoint,
            method="POST",
            params={"standard": "UBL" if move_type == "out_invoice" else "CN", "cif": company.vat.replace("RO", "")},
            data=xml_data,
        )
        if "error" in result:
            return result

        root = etree.fromstring(result["content"])
        res_status = root.get("ExecutionStatus")
        if res_status == "1":
            error_elements = root.findall(".//ns:Errors", namespaces=NS_UPLOAD)
            error_messages = [error_element.get("errorMessage") for error_element in error_elements]
            return {"error": "\n".join(error_messages)}
        else:
            return {"key_loading": root.get("index_incarcare")}
