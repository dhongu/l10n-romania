# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import Form, TransactionCase, tagged

from .common import IMPORTER_VAT, load_lines

EXTRACT_LINES = "odoo.addons.l10n_ro_customs_dvi_import.tools.sni_dvi.extract_lines"
PDF = base64.b64encode(b"%PDF-1.4 SNI declaration")


@tagged("post_install", "-at_install")
class TestDviImport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.vat = IMPORTER_VAT
        cls.vendor = cls.env["res.partner"].create({"name": "Exporter", "country_id": cls.env.ref("base.md").id})
        cls.taxes = {}
        for rate in (11, 21):
            cls.taxes[rate] = cls.env["account.tax"].search(
                [
                    ("type_tax_use", "=", "purchase"),
                    ("amount_type", "=", "percent"),
                    ("amount", "=", rate),
                    ("company_id", "=", cls.company.id),
                ],
                limit=1,
            ) or cls.env["account.tax"].create(
                {
                    "name": f"VAT {rate}% import",
                    "type_tax_use": "purchase",
                    "amount": rate,
                    "company_id": cls.company.id,
                }
            )

    def _create_bill(self, ref):
        return self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.vendor.id,
                "ref": ref,
                "invoice_date": "2026-09-10",
                "invoice_line_ids": [(0, 0, {"name": "Goods", "quantity": 1, "price_unit": 1000, "tax_ids": False})],
            }
        )

    def _wizard_form(self, bill, fixture):
        wizard_form = Form(self.env["account.invoice.dvi"].with_context(active_id=bill.id))
        with patch(EXTRACT_LINES, return_value=load_lines(fixture)):
            wizard_form.dvi_file = PDF
        return wizard_form

    def _apply(self, wizard_form, fixture):
        wizard = wizard_form.save()
        with patch(EXTRACT_LINES, return_value=load_lines(fixture)):
            action = wizard.do_create_dvi()
        return self.env["stock.landed.cost"].browse(action["res_id"])

    def test_fill_in_regime_4000(self):
        bill = self._create_bill("EXP/2026/00001")
        wizard_form = self._wizard_form(bill, "dvi_4000_two_items")
        self.assertEqual(wizard_form.dvi_number, "26ROXX0000000001R1")
        self.assertEqual(str(wizard_form.date), "2026-09-11")
        self.assertEqual(wizard_form.customs_regime, "4000")
        self.assertEqual(wizard_form.custom_duty, 0.0)
        self.assertAlmostEqual(wizard_form.tax_base, 55825.29)
        self.assertEqual(wizard_form.tax_value, 6141.0, "B00 is transcribed, not recomputed from the base")
        self.assertEqual(wizard_form.tax_id.amount, 11)
        self.assertNotIn("is not among the invoices", wizard_form.dvi_import_info)

        landed_cost = self._apply(wizard_form, "dvi_4000_two_items")
        self.assertEqual(landed_cost.dvi_number, "26ROXX0000000001R1")
        self.assertEqual(landed_cost.tax_value, 6141.0)
        self.assertEqual(bill.dvi_id, landed_cost)
        attachment = self.env["ir.attachment"].search(
            [("res_model", "=", "stock.landed.cost"), ("res_id", "=", landed_cost.id)]
        )
        self.assertEqual(len(attachment), 1, "The declaration is attached to the DVI")

        with self.assertRaisesRegex(UserError, "already recorded"):
            self._wizard_form(self._create_bill("EXP/2026/00001"), "dvi_4000_two_items")

    def test_fill_in_regime_4200(self):
        """Regime 4200: B00 is the guarantee held by customs, never import VAT."""
        bill = self._create_bill("11EX")
        wizard_form = self._wizard_form(bill, "dvi_4200_two_items")
        self.assertEqual(wizard_form.customs_regime, "4200")
        self.assertEqual(wizard_form.tax_value, 0.0)
        self.assertEqual(wizard_form.vat_guarantee_amount, 7473.0)
        self.assertFalse(wizard_form.tax_id.amount, "The import is exempt")
        self.assertNotIn("No purchase tax", wizard_form.dvi_import_info, "The B00 rate is irrelevant under 4200")
        landed_cost = self._apply(wizard_form, "dvi_4200_two_items")
        self.assertEqual(landed_cost.vat_guarantee_amount, 7473.0)
        self.assertEqual(landed_cost.vat_guarantee_state, "blocked")

    def test_fill_in_customs_duty(self):
        bill = self._create_bill("CI-20260101-ABC-001")
        wizard_form = self._wizard_form(bill, "dvi_4000_customs_duty")
        self.assertEqual(wizard_form.custom_duty, 144.0)
        self.assertEqual(wizard_form.tax_base, 8617.13, "The VAT base includes the customs duty")
        self.assertEqual(wizard_form.tax_value, 1810.0)
        self.assertEqual(wizard_form.tax_id.amount, 21)

    def test_bill_not_on_declaration(self):
        bill = self._create_bill("OTHER-INVOICE")
        wizard_form = self._wizard_form(bill, "dvi_4000_one_item")
        self.assertIn("is not among the invoices", wizard_form.dvi_import_info)

    def test_other_importer(self):
        self.company.vat = "RO76543210"
        with self.assertRaisesRegex(UserError, "is not the current company"):
            self._wizard_form(self._create_bill("EXP/2026/00002"), "dvi_4000_one_item")
