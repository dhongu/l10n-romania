import {describe, expect, test} from "@odoo/hoot";

import {parseInvoiceXml} from "@l10n_ro_message_spv_side_panel_online/document/spv_invoice_parser.esm";

const INVOICE = `<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
  <cbc:ID>TID 4521</cbc:ID>
  <cbc:IssueDate>2026-11-03</cbc:IssueDate>
  <cbc:DueDate>2026-12-03</cbc:DueDate>
  <cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
  <cac:AccountingSupplierParty><cac:Party>
    <cac:PostalAddress><cbc:StreetName>Str. Fabricii 1</cbc:StreetName><cbc:CityName>Cluj-Napoca</cbc:CityName>
      <cac:Country><cbc:IdentificationCode>RO</cbc:IdentificationCode></cac:Country></cac:PostalAddress>
    <cac:PartyTaxScheme><cbc:CompanyID>RO14567890</cbc:CompanyID></cac:PartyTaxScheme>
    <cac:PartyLegalEntity><cbc:RegistrationName>Termo Instal SRL</cbc:RegistrationName></cac:PartyLegalEntity>
  </cac:Party></cac:AccountingSupplierParty>
  <cac:AccountingCustomerParty><cac:Party>
    <cac:PartyTaxScheme><cbc:CompanyID>RO99999999</cbc:CompanyID></cac:PartyTaxScheme>
    <cac:PartyLegalEntity><cbc:RegistrationName>Cumparator Test SRL</cbc:RegistrationName></cac:PartyLegalEntity>
  </cac:Party></cac:AccountingCustomerParty>
  <cac:LegalMonetaryTotal>
    <cbc:TaxExclusiveAmount>1900.00</cbc:TaxExclusiveAmount>
    <cbc:TaxInclusiveAmount>2299.00</cbc:TaxInclusiveAmount>
    <cbc:PayableAmount>2299.00</cbc:PayableAmount>
  </cac:LegalMonetaryTotal>
  <cac:InvoiceLine>
    <cbc:InvoicedQuantity unitCode="H87">2</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount>1690.00</cbc:LineExtensionAmount>
    <cac:Item><cbc:Name>Pompa 25/60</cbc:Name>
      <cac:SellersItemIdentification><cbc:ID>PCR-2560</cbc:ID></cac:SellersItemIdentification>
      <cac:ClassifiedTaxCategory><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
    <cac:Price><cbc:PriceAmount>845.00</cbc:PriceAmount></cac:Price>
  </cac:InvoiceLine>
  <cac:InvoiceLine>
    <cbc:InvoicedQuantity unitCode="H87">1</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount>210.00</cbc:LineExtensionAmount>
    <cac:Item><cbc:Name>Vas 24 L</cbc:Name>
      <cac:StandardItemIdentification><cbc:ID>5941234567890</cbc:ID></cac:StandardItemIdentification>
      <cac:ClassifiedTaxCategory><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
    <cac:Price><cbc:PriceAmount>210.00</cbc:PriceAmount></cac:Price>
  </cac:InvoiceLine>
</Invoice>`;

describe.current.tags("headless");

test("reads the parties, the header, the lines and the totals", () => {
    const data = parseInvoiceXml(INVOICE, {incoming: true});
    expect(data.number).toBe("TID 4521");
    expect(data.supplier.name).toBe("Termo Instal SRL");
    expect(data.supplier.vat).toBe("RO14567890");
    expect(data.supplier.address).toBe("Str. Fabricii 1, Cluj-Napoca, RO");
    expect(data.party.vat).toBe("RO14567890");
    expect(data.lines).toHaveLength(2);
    expect(data.lines[0].code).toBe("PCR-2560");
    expect(data.lines[0].taxPercent).toBe("21");
    expect(data.lines[0].price).toBe(845);
    expect(data.lines[1].code).toBe("5941234567890");
    expect(data.untaxed).toBe(1900);
    expect(data.total).toBe(2299);
    expect(data.tax).toBe(399);
});

test("the other party is the customer on an invoice sent", () => {
    const data = parseInvoiceXml(INVOICE, {incoming: false});
    expect(data.party.vat).toBe("RO99999999");
});

test("what is not an invoice gives null", () => {
    expect(parseInvoiceXml("")).toBe(null);
    expect(parseInvoiceXml("<not xml")).toBe(null);
    expect(parseInvoiceXml("<Signature/>")).toBe(null);
});
