from unittest.mock import patch

from lxml import etree

from odoo.tests import tagged
from odoo.tools import file_open

from odoo.addons.account_edi_ubl_cii.models.account_edi_common import AccountEdiCommon
from odoo.addons.l10n_ro_edi.tests.common import TestROEdiCommon


@tagged("post_install_l10n", "post_install", "-at_install")
class TestCiusRoVatCompare(TestROEdiCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.builder = cls.env["account.edi.xml.ubl_ro"]
        cls.ro = cls.env.ref("base.ro")

    def _supplier(self, vat="RO12345674", **kwargs):
        values = {
            "name": "Romanian VAT comparison supplier SRL",
            "is_company": True,
            "country_id": self.ro.id,
            "state_id": self.env.ref("base.RO_B").id,
            "street": "Test Street 1",
            "city": "SECTOR1",
            "vat": vat,
            "l10n_ro_vat_subjected": vat.startswith("RO"),
        }
        values.update(kwargs)
        partner = self.env["res.partner"].with_context(no_vat_validation=True).create(values)
        self.assertEqual(partner.vat, vat)
        return partner

    def _legacy_import(self, vat, name="Romanian VAT comparison supplier SRL", **kwargs):
        return self.builder._import_partner(
            self.env.company,
            name,
            False,
            False,
            vat,
            postal_address={"country_code": "RO"},
            **kwargs,
        )

    def test_ro_prefix_equivalence(self):
        for stored, incoming in [
            ("RO12345674", "12345674"),
            ("12345674", "RO12345674"),
            ("ro12345674", "12345674"),
            (" RO 12345674 ", "12345674"),
            ("12345674", "ro 12345674"),
        ]:
            with self.subTest(stored=stored, incoming=incoming):
                self.assertTrue(self.builder._vat_is_equal(stored, incoming, self.ro))

    def test_different_or_invalid_identifiers_are_not_equivalent(self):
        for stored, incoming in [
            ("RO12345674", "1234567897"),
            ("RO12345675", "12345675"),
            ("RO00000000", "00000000"),
            ("RO012345674", "12345674"),
            ("RO123.45674", "12345674"),
            ("RO8001011234567", "8001011234567"),
            ("DE12345674", "12345674"),
            ("RO12345674", ""),
            ("", "12345674"),
        ]:
            with self.subTest(stored=stored, incoming=incoming):
                self.assertFalse(self.builder._vat_is_equal(stored, incoming, self.ro))

    def test_foreign_or_unknown_country_keeps_native_comparison(self):
        for country in (self.env.ref("base.de"), False):
            with self.subTest(country=country):
                self.assertFalse(self.builder._vat_is_equal("RO12345674", "12345674", country))
                self.assertTrue(self.builder._vat_is_equal("DE 123456789", "de123456789", country))

    def test_generic_ubl_comparison_is_unchanged(self):
        self.assertFalse(self.env["account.edi.xml.ubl_bis3"]._vat_is_equal("RO12345674", "12345674", self.ro))

    def test_legacy_import_reuses_prefixed_partner(self):
        partner = self._supplier()
        before = self.env["res.partner"].search_count([])
        found, logs = self._legacy_import("12345674")
        self.assertEqual(found, partner)
        self.assertEqual(partner.vat, "RO12345674")
        self.assertFalse(logs)
        self.assertEqual(self.env["res.partner"].search_count([]), before)

    def test_native_comparison_reproduces_duplicate(self):
        partner = self._supplier()
        before = self.env["res.partner"].search_count([])
        with patch.object(type(self.builder), "_vat_is_equal", AccountEdiCommon._vat_is_equal):
            found, logs = self._legacy_import("12345674")
        self.assertNotEqual(found, partner)
        self.assertTrue(logs)
        self.assertEqual(self.env["res.partner"].search_count([]), before + 1)

    def test_legacy_import_reuses_bare_partner(self):
        partner = self._supplier(vat="12345674")
        before = self.env["res.partner"].search_count([])
        found, logs = self._legacy_import("RO12345674")
        self.assertEqual(found, partner)
        self.assertEqual(partner.vat, "12345674")
        self.assertFalse(logs)
        self.assertEqual(self.env["res.partner"].search_count([]), before)

    def test_legacy_import_vat_match_does_not_need_same_name(self):
        partner = self._supplier(name="Previous legal name SRL")
        found, logs = self._legacy_import("12345674", name="Updated legal name SRL")
        self.assertEqual(found, partner)
        self.assertFalse(logs)
        self.assertEqual(partner.name, "Previous legal name SRL")

    def test_existing_duplicate_candidates_do_not_create_another_partner(self):
        partners = self._supplier() | self._supplier(vat="12345674")
        before = self.env["res.partner"].search_count([])
        found, logs = self._legacy_import("12345674")
        self.assertIn(found, partners)
        self.assertFalse(logs)
        self.assertEqual(self.env["res.partner"].search_count([]), before)

    def test_other_company_partner_is_not_reused(self):
        other_company = self.env["res.company"].create({"name": "Other VAT comparison company"})
        other = self._supplier(company_id=other_company.id)
        local = self._supplier(vat="12345674", company_id=self.env.company.id)
        found, logs = self._legacy_import("12345674")
        self.assertEqual(found, local)
        self.assertNotEqual(found, other)
        self.assertFalse(logs)

    def test_archived_partner_is_not_reactivated(self):
        archived = self._supplier(active=False)
        found, _logs = self._legacy_import("12345674")
        self.assertNotEqual(found, archived)
        self.assertFalse(archived.active)

    def test_collected_values_import_reuses_partner(self):
        partner = self._supplier()
        before = self.env["res.partner"].search_count([])
        collected = {
            "customer_values": {
                "customer": partner,
                "name": partner.name,
                "vat": "12345674",
                "country_code": "RO",
            },
            "logs": [],
            "to_write": {},
        }
        self.builder._import_create_missing_customer(collected)
        self.assertEqual(collected["customer_values"]["customer"], partner)
        self.assertFalse(collected["logs"])
        self.assertEqual(self.env["res.partner"].search_count([]), before)
        self.assertEqual(partner.vat, "RO12345674")

    def _import_xml(self, supplier, incoming_vat):
        with file_open("l10n_ro_edi/tests/test_files/from_odoo/ciusro_in_invoice.xml", "rb") as source:
            tree = etree.fromstring(source.read())
        ns = {
            "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        }
        party = tree.find("cac:AccountingSupplierParty/cac:Party", ns)
        for element in party.xpath(".//cbc:CompanyID | .//cbc:EndpointID", namespaces=ns):
            element.text = incoming_vat
        for element in party.xpath(".//cbc:Name | .//cbc:RegistrationName", namespaces=ns):
            element.text = supplier.name
        attachment = self.env["ir.attachment"].create(
            {"name": "ro-vat-comparison.xml", "mimetype": "application/xml", "raw": etree.tostring(tree)}
        )
        return self.company_data["default_journal_purchase"]._create_document_from_attachment(attachment.id)

    def test_xml_import_reuses_partner_in_both_directions(self):
        for stored, incoming in [("RO12345674", "12345674"), ("12345674", "RO12345674")]:
            with self.subTest(stored=stored, incoming=incoming), self.env.cr.savepoint():
                partner = self._supplier(vat=stored)
                before = self.env["res.partner"].search_count([])
                invoice = self._import_xml(partner, incoming)
                self.assertEqual(invoice.partner_id, partner)
                self.assertEqual(invoice.state, "draft")
                self.assertEqual(partner.vat, stored)
                self.assertEqual(self.env["res.partner"].search_count([]), before)
                partner.active = False

    def test_import_preserves_existing_paid_invoice_and_reconciliation(self):
        supplier = self._supplier()
        historical = self.create_invoice(partner_id=supplier.id)
        refund = historical._reverse_moves([{"date": historical.date}], cancel=True)
        self.assertTrue(
            historical.line_ids.filtered(lambda line: line.account_id.account_type == "asset_receivable").reconciled
        )
        moves = historical | refund
        lines = moves.line_ids
        move_fields = [
            "name",
            "state",
            "partner_id",
            "date",
            "amount_total",
            "amount_residual",
            "payment_state",
            "line_ids",
        ]
        line_fields = [
            "partner_id",
            "account_id",
            "debit",
            "credit",
            "amount_currency",
            "amount_residual",
            "reconciled",
            "full_reconcile_id",
            "matched_debit_ids",
            "matched_credit_ids",
        ]
        partials = lines.matched_debit_ids | lines.matched_credit_ids
        before = (
            moves.read(move_fields),
            lines.read(line_fields),
            partials.read(["debit_move_id", "credit_move_id", "amount"]),
        )
        imported = self._import_xml(supplier, "12345674")
        self.assertEqual(imported.partner_id, supplier)
        self.assertEqual(imported.state, "draft")
        self.assertEqual(
            (
                moves.read(move_fields),
                lines.read(line_fields),
                partials.read(["debit_move_id", "credit_move_id", "amount"]),
            ),
            before,
        )
