# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import io
import zipfile
from unittest.mock import patch

from odoo.tests import TransactionCase, tagged

INVOICE_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
  <cbc:ID>TID 4521</cbc:ID>
  <cbc:IssueDate>2026-11-03</cbc:IssueDate>
  <cbc:DueDate>2026-12-03</cbc:DueDate>
  <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
  <cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
  <cac:AccountingSupplierParty>
    <cac:Party>
      <cac:PostalAddress>
        <cbc:StreetName>Str. Fabricii 1</cbc:StreetName>
        <cbc:CityName>Cluj-Napoca</cbc:CityName>
        <cac:Country><cbc:IdentificationCode>RO</cbc:IdentificationCode></cac:Country>
      </cac:PostalAddress>
      <cac:PartyTaxScheme><cbc:CompanyID>RO14567890</cbc:CompanyID></cac:PartyTaxScheme>
      <cac:PartyLegalEntity>
        <cbc:RegistrationName>Termo Instal Distributie SRL</cbc:RegistrationName>
      </cac:PartyLegalEntity>
    </cac:Party>
  </cac:AccountingSupplierParty>
  <cac:AccountingCustomerParty>
    <cac:Party>
      <cac:PartyTaxScheme><cbc:CompanyID>RO99999999</cbc:CompanyID></cac:PartyTaxScheme>
      <cac:PartyLegalEntity>
        <cbc:RegistrationName>Cumparator Test SRL</cbc:RegistrationName>
      </cac:PartyLegalEntity>
    </cac:Party>
  </cac:AccountingCustomerParty>
  <cac:LegalMonetaryTotal>
    <cbc:LineExtensionAmount currencyID="RON">1900.00</cbc:LineExtensionAmount>
    <cbc:TaxExclusiveAmount currencyID="RON">1900.00</cbc:TaxExclusiveAmount>
    <cbc:TaxInclusiveAmount currencyID="RON">2299.00</cbc:TaxInclusiveAmount>
    <cbc:PayableAmount currencyID="RON">2299.00</cbc:PayableAmount>
  </cac:LegalMonetaryTotal>
  <cac:InvoiceLine>
    <cbc:ID>1</cbc:ID>
    <cbc:InvoicedQuantity unitCode="H87">2</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount currencyID="RON">1690.00</cbc:LineExtensionAmount>
    <cac:Item>
      <cbc:Name>Pompa circulatie 25/60</cbc:Name>
      <cac:ClassifiedTaxCategory><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory>
    </cac:Item>
    <cac:Price><cbc:PriceAmount currencyID="RON">845.00</cbc:PriceAmount></cac:Price>
  </cac:InvoiceLine>
  <cac:InvoiceLine>
    <cbc:ID>2</cbc:ID>
    <cbc:InvoicedQuantity unitCode="H87">1</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount currencyID="RON">210.00</cbc:LineExtensionAmount>
    <cac:Item>
      <cbc:Name>Vas expansiune 24 L</cbc:Name>
      <cac:ClassifiedTaxCategory><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory>
    </cac:Item>
    <cac:Price><cbc:PriceAmount currencyID="RON">210.00</cbc:PriceAmount></cac:Price>
  </cac:InvoiceLine>
</Invoice>
"""


@tagged("post_install", "-at_install")
class TestMessageSpvSidePanel(TransactionCase):
    def _message(self, message_type="in_invoice"):
        return self.env["l10n.ro.message.spv"].create(
            {"name": "1234", "cif": "RO99999999", "message_type": message_type}
        )

    def _read(self, message, xml_bytes):
        model = type(message)
        with patch.object(model, "_get_xml_bytes", return_value=("i.xml", xml_bytes)):
            message.invalidate_recordset()
            return {
                "vat": message.spv_party_vat,
                "document": message.spv_document_html,
                "lines": message.spv_lines_html,
                "data": message._spv_read_invoice(),
            }

    def test_incoming_invoice(self):
        result = self._read(self._message("in_invoice"), INVOICE_XML)
        self.assertEqual(result["vat"], "RO14567890", "the supplier, for a received invoice")
        data = result["data"]
        self.assertEqual(data["number"], "TID 4521")
        self.assertEqual(data["supplier"]["name"], "Termo Instal Distributie SRL")
        self.assertEqual(data["supplier"]["address"], "Str. Fabricii 1, Cluj-Napoca, RO")
        self.assertEqual(len(data["lines"]), 2)
        self.assertEqual(data["lines"][0]["name"], "Pompa circulatie 25/60")
        self.assertEqual(data["lines"][0]["tax_percent"], "21")
        self.assertIn("Pompa circulatie 25/60", str(result["lines"]))
        self.assertIn("Termo Instal Distributie SRL", str(result["document"]))
        self.assertIn("2,299.00", data["total"])

    def test_outgoing_invoice_shows_the_customer(self):
        result = self._read(self._message("out_invoice"), INVOICE_XML)
        self.assertEqual(result["vat"], "RO99999999")

    def test_credit_note_lines(self):
        xml = (
            INVOICE_XML.replace(b"<Invoice ", b"<CreditNote ")
            .replace(b"</Invoice>", b"</CreditNote>")
            .replace(b"cac:InvoiceLine", b"cac:CreditNoteLine")
            .replace(b"cbc:InvoicedQuantity", b"cbc:CreditedQuantity")
        )
        data = self._read(self._message(), xml)["data"]
        self.assertTrue(data["is_credit_note"])
        self.assertEqual(len(data["lines"]), 2)
        self.assertEqual(data["lines"][1]["quantity"], "1")

    def test_message_without_xml(self):
        message = self._message()
        message.invalidate_recordset()
        self.assertFalse(message.spv_party_vat)
        self.assertFalse(message.spv_document_html)
        self.assertEqual(message._spv_read_invoice(), {})

    def test_read_from_zip_as_the_web_client_does(self):
        """The web client reads with `bin_size`: the computed fields must still see the XML."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("1234.xml", INVOICE_XML)
        attachment = self.env["ir.attachment"].create({"name": "1234.zip", "raw": buffer.getvalue()})
        message = self._message()
        message.attachment_id = attachment
        message = message.with_context(bin_size=True)
        message.invalidate_recordset()
        self.assertEqual(message.spv_party_vat, "RO14567890")
        self.assertIn("Pompa circulatie 25/60", str(message.spv_lines_html))
