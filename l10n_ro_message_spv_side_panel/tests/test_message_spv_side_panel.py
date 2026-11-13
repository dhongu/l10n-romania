# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import io
import zipfile

from odoo.tests import TransactionCase, tagged

from odoo.addons.l10n_ro_message_spv_side_panel import uninstall_hook

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
      <cac:SellersItemIdentification><cbc:ID>PCR-2560</cbc:ID></cac:SellersItemIdentification>
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
      <cac:StandardItemIdentification><cbc:ID schemeID="0160">5941234567890</cbc:ID></cac:StandardItemIdentification>
      <cac:ClassifiedTaxCategory><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory>
    </cac:Item>
    <cac:Price><cbc:PriceAmount currencyID="RON">210.00</cbc:PriceAmount></cac:Price>
  </cac:InvoiceLine>
</Invoice>
"""


@tagged("post_install", "-at_install")
class TestMessageSpvSidePanel(TransactionCase):
    def _message(self, xml_bytes=None, message_type="in_invoice"):
        """A message whose ZIP holds the given XML (none: a message without file)."""
        message = self.env["l10n.ro.message.spv"].create(
            {"name": "1234", "cif": "RO99999999", "message_type": message_type}
        )
        if xml_bytes is not None:
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w") as archive:
                archive.writestr("1234.xml", xml_bytes)
            message.attachment_id = self.env["ir.attachment"].create({"name": "1234.zip", "raw": buffer.getvalue()})
        # the web client reads with `bin_size`: the computed fields must still see the XML
        message = message.with_context(bin_size=True)
        message.invalidate_recordset()
        return message

    def test_incoming_invoice(self):
        message = self._message(INVOICE_XML)
        self.assertEqual(message.spv_party_vat, "RO14567890", "the supplier, for a received invoice")
        data = message._spv_read_invoice()
        self.assertEqual(data["number"], "TID 4521")
        self.assertEqual(data["supplier"]["name"], "Termo Instal Distributie SRL")
        self.assertEqual(data["supplier"]["address"], "Str. Fabricii 1, Cluj-Napoca, RO")
        self.assertEqual(len(data["lines"]), 2)
        self.assertEqual(data["lines"][0]["name"], "Pompa circulatie 25/60")
        self.assertEqual(data["lines"][0]["tax_percent"], "21")
        self.assertEqual(data["lines"][0]["code"], "PCR-2560", "the code of the seller")
        self.assertEqual(
            data["lines"][1]["code"], "5941234567890", "the standard identifier, when there is no code of the seller"
        )
        self.assertIn("Pompa circulatie 25/60", str(message.spv_lines_html))
        self.assertIn("Termo Instal Distributie SRL", str(message.spv_document_html))
        self.assertIn("2,299.00", data["total"])

    def test_dates_follow_the_language_of_the_user(self):
        data = self._message(INVOICE_XML)._spv_read_invoice()
        self.assertNotEqual(data["issue_date"], "2026-11-03")
        self.assertIn("2026", data["issue_date"])

    def test_outgoing_invoice_shows_the_customer(self):
        message = self._message(INVOICE_XML, message_type="out_invoice")
        self.assertEqual(message.spv_party_vat, "RO99999999")

    def test_credit_note_lines(self):
        xml = (
            INVOICE_XML.replace(b"<Invoice ", b"<CreditNote ")
            .replace(b"</Invoice>", b"</CreditNote>")
            .replace(b"cac:InvoiceLine", b"cac:CreditNoteLine")
            .replace(b"cbc:InvoicedQuantity", b"cbc:CreditedQuantity")
        )
        data = self._message(xml)._spv_read_invoice()
        self.assertTrue(data["is_credit_note"])
        self.assertEqual(len(data["lines"]), 2)
        self.assertEqual(data["lines"][1]["quantity"], "1")

    def test_message_without_xml(self):
        message = self._message()
        self.assertFalse(message.spv_party_vat)
        self.assertFalse(message.spv_document_html)
        self.assertEqual(message._spv_read_invoice(), {})

    def test_not_a_number_does_not_block_the_message(self):
        """A value like `1.234,50` or `n/a` is shown as written, the message still opens."""
        xml = INVOICE_XML.replace(b">845.00<", b">1.234,50<").replace(
            b">2299.00</cbc:PayableAmount", b">n/a</cbc:PayableAmount"
        )
        message = self._message(xml)
        data = message._spv_read_invoice()
        self.assertEqual(data["lines"][0]["price"], "1.234,50")
        self.assertEqual(message.spv_party_vat, "RO14567890")
        self.assertIn("1.234,50", str(message.spv_lines_html))

    def test_external_entities_are_not_resolved(self):
        """The XML comes from a third party: a DOCTYPE with an external entity must not
        bring the content of a local file into the document."""
        xml = INVOICE_XML.replace(
            b"<Invoice ",
            b'<!DOCTYPE Invoice [<!ENTITY leak SYSTEM "file:///etc/hosts">]><Invoice ',
            1,
        ).replace(b"<cbc:InvoiceTypeCode>380", b"<cbc:Note>&leak;</cbc:Note><cbc:InvoiceTypeCode>380")
        message = self._message(xml)
        data = message._spv_read_invoice()
        # `localhost` is in /etc/hosts and nowhere in the invoice
        self.assertNotIn("localhost", str(data.get("note", "")))
        self.assertNotIn("localhost", str(message.spv_document_html))

    def test_empty_or_invalid_xml_does_not_block_the_message(self):
        """A ZIP whose XML is empty, or is not XML, opens as a message without a document."""
        for content in (b"", b"This is not an XML document."):
            with self.subTest(content=content):
                message = self._message(content)
                self.assertEqual(message._spv_read_invoice(), {})
                self.assertFalse(message.spv_party_vat)
                self.assertFalse(message.spv_document_html)
                message.unlink()

    def test_non_finite_numbers_do_not_block_the_message(self):
        """`inf` or `nan` in the XML are shown as written, the message still opens."""
        xml = INVOICE_XML.replace(b">845.00<", b">inf<").replace(
            b">2299.00</cbc:TaxInclusiveAmount", b">nan</cbc:TaxInclusiveAmount"
        )
        message = self._message(xml)
        data = message._spv_read_invoice()
        self.assertEqual(data["lines"][0]["price"], "inf")
        self.assertEqual(message.spv_party_vat, "RO14567890")
        self.assertTrue(message.spv_document_html)

    def test_menus_open_the_split_view(self):
        action = self.env.ref("l10n_ro_message_spv_side_panel.action_l10n_ro_message_spv_split")
        for xmlid in ("menu_l10n_ro_spv", "menu_l10n_ro_message_spv"):
            self.assertEqual(self.env.ref(f"l10n_ro_message_spv.{xmlid}").action, action)

    def test_uninstall_hook_puts_the_menus_back(self):
        original = self.env.ref("l10n_ro_message_spv.action_l10n_ro_message_spv")
        uninstall_hook(self.env)
        for xmlid in ("menu_l10n_ro_spv", "menu_l10n_ro_message_spv"):
            self.assertEqual(self.env.ref(f"l10n_ro_message_spv.{xmlid}").action, original)

    def test_full_form_shows_the_document_without_tabs(self):
        arch = self.env["l10n.ro.message.spv"].get_view(view_type="form")["arch"]
        self.assertIn("spv_document_html", arch)
        self.assertNotIn("<notebook", arch.split("spv_document_html")[1])
        self.assertIn("spv_party_vat", arch)
