# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from lxml import etree

from odoo import fields
from odoo.tests import tagged

from odoo.addons.l10n_ro_edi.tests.common import TestROEdiCommon

NS = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


@tagged("post_install_l10n", "post_install", "-at_install")
class TestBillingReference(TestROEdiCommon):
    """Stornoul trimis in SPV trebuie sa poarte numarul si data facturii corectate
    (``cac:BillingReference``, BT-25 / BT-26). In 19.0 standardul nu scrie nodul pentru
    CIUS-RO (EFACTURA-001)."""

    def _billing_references(self, move):
        xml, _errors = self.env["account.edi.xml.ubl_ro"]._export_invoice(move)
        tree = etree.fromstring(xml)
        return [
            (
                ref.findtext("cbc:ID", namespaces=NS),
                ref.findtext("cbc:IssueDate", namespaces=NS),
            )
            for ref in tree.findall("cac:BillingReference/cac:InvoiceDocumentReference", NS)
        ]

    def test_credit_note_references_reversed_invoice(self):
        invoice = self.create_invoice(invoice_date=fields.Date.from_string("2026-09-15"))
        credit_note = invoice._reverse_moves([{"invoice_date": fields.Date.from_string("2026-10-01")}])
        credit_note.action_post()

        self.assertEqual(self._billing_references(credit_note), [(invoice.name, "2026-09-15")])

    def test_credit_note_without_origin_has_no_reference(self):
        credit_note = self.create_invoice(move_type="out_refund")
        self.assertFalse(credit_note.reversed_entry_id)

        self.assertEqual(self._billing_references(credit_note), [])

    def test_invoice_has_no_reference(self):
        invoice = self.create_invoice()

        self.assertEqual(self._billing_references(invoice), [])
