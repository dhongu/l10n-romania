# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from lxml import etree

from odoo import api, fields, models
from odoo.tools.misc import formatLang

TEMPLATE_DOCUMENT = "l10n_ro_message_spv_side_panel.spv_invoice_document"
TEMPLATE_LINES = "l10n_ro_message_spv_side_panel.spv_invoice_lines"


def _text(node, path):
    """Stripped text of the first element at `path`, or an empty string."""
    if node is None:
        return ""
    value = node.findtext(path)
    return value.strip() if value else ""


class L10nRoMessageSpv(models.Model):
    _inherit = "l10n.ro.message.spv"

    # Read from the invoice XML when the record is opened, not stored: they are shown
    # for one record at a time, in the side panel.
    spv_party_vat = fields.Char(
        string="VAT (XML)",
        compute="_compute_spv_invoice",
        help="The VAT number of the other party, as written in the invoice XML.",
    )
    spv_document_html = fields.Html(
        string="Document",
        compute="_compute_spv_invoice",
        sanitize=False,
    )
    spv_lines_html = fields.Html(
        string="XML Lines",
        compute="_compute_spv_invoice",
        sanitize=False,
    )

    @api.depends("attachment_id", "message_type")
    def _compute_spv_invoice(self):
        qweb = self.env["ir.qweb"]
        for message in self:
            # The web client reads with `bin_size`: the content of the ZIP would be
            # replaced by its size.
            data = message.with_context(bin_size=False)._spv_read_invoice()
            message.spv_party_vat = data.get("party", {}).get("vat", "")
            if data:
                message.spv_document_html = qweb._render(TEMPLATE_DOCUMENT, data)
                message.spv_lines_html = qweb._render(TEMPLATE_LINES, data)
            else:
                message.spv_document_html = False
                message.spv_lines_html = False

    def _spv_read_invoice(self):
        """Read the invoice XML of the message into what the panel shows.

        Returns an empty dict when the message has no invoice XML (not downloaded yet,
        or the ZIP holds none). Amounts are formatted strings, in the language of the
        user."""
        self.ensure_one()
        _file_name, xml_bytes = self._get_xml_bytes()
        if not xml_bytes:
            return {}
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(xml_bytes, parser=parser)
        if root is None:
            return {}

        is_credit_note = etree.QName(root).localname == "CreditNote"
        supplier = self._spv_read_party(root.find("./{*}AccountingSupplierParty/{*}Party"))
        customer = self._spv_read_party(root.find("./{*}AccountingCustomerParty/{*}Party"))
        incoming = self.message_type in ("in_invoice", "in_receipt")
        party = supplier if incoming else customer

        def money(value):
            return formatLang(self.env, float(value), digits=2) if value else ""

        lines = []
        line_nodes = root.findall("./{*}InvoiceLine") + root.findall("./{*}CreditNoteLine")
        for index, line in enumerate(line_nodes, start=1):
            qty_node = line.find("./{*}InvoicedQuantity")
            if qty_node is None:
                qty_node = line.find("./{*}CreditedQuantity")
            quantity = qty_node.text.strip() if qty_node is not None and qty_node.text else ""
            lines.append(
                {
                    "number": index,
                    "name": _text(line, "./{*}Item/{*}Name") or _text(line, "./{*}Item/{*}Description"),
                    "unit": qty_node.get("unitCode", "") if qty_node is not None else "",
                    "quantity": quantity,
                    "price": money(_text(line, "./{*}Price/{*}PriceAmount")),
                    "tax_percent": _text(line, "./{*}Item/{*}ClassifiedTaxCategory/{*}Percent"),
                    "amount": money(_text(line, "./{*}LineExtensionAmount")),
                }
            )

        def total(path):
            text = _text(root, f".//{{*}}LegalMonetaryTotal/{{*}}{path}")
            return float(text) if text else 0.0

        untaxed = total("TaxExclusiveAmount")
        with_tax = total("TaxInclusiveAmount")
        return {
            "is_credit_note": is_credit_note,
            "number": _text(root, "./{*}ID"),
            "issue_date": _text(root, "./{*}IssueDate"),
            "due_date": _text(root, "./{*}DueDate") or _text(root, "./{*}PaymentMeans/{*}PaymentDueDate"),
            "currency": _text(root, "./{*}DocumentCurrencyCode"),
            "supplier": supplier,
            "customer": customer,
            "party": party,
            "lines": lines,
            "untaxed": money(untaxed),
            "tax": money(with_tax - untaxed) if with_tax else "",
            "total": money(total("PayableAmount") or with_tax),
            "note": _text(root, "./{*}Note"),
        }

    @api.model
    def _spv_read_party(self, party):
        """Name, VAT and address of a party node of the UBL invoice."""
        if party is None:
            return {}
        address = party.find("./{*}PostalAddress")
        address_parts = [
            _text(address, "./{*}StreetName"),
            _text(address, "./{*}CityName"),
            _text(address, "./{*}Country/{*}IdentificationCode"),
        ]
        return {
            "name": _text(party, "./{*}PartyLegalEntity/{*}RegistrationName") or _text(party, "./{*}PartyName/{*}Name"),
            "vat": _text(party, "./{*}PartyTaxScheme/{*}CompanyID")
            or _text(party, "./{*}PartyLegalEntity/{*}CompanyID"),
            "address": ", ".join(part for part in address_parts if part),
        }
