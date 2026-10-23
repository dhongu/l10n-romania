from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.l10n_ro_edi.models.account_move import AccountMove as NativeAccountMove


@tagged("post_install", "-at_install")
class TestSpvResetNotIndexed(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner SPV Reset",
                "country_id": cls.env.ref("base.ro").id,
                "state_id": cls.env.ref("base.RO_B").id,
                "city": "Bucuresti",
                "street": "Str. Test 1",
            }
        )
        cls.product = cls.env["product.product"].create({"name": "Test Product SPV Reset"})

    def _create_posted_invoice(self):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [(0, 0, {"product_id": self.product.id, "quantity": 1, "price_unit": 100})],
            }
        )
        invoice.action_post()
        return invoice

    def _create_not_indexed_invoice(self):
        invoice = self._create_posted_invoice()
        self.env["l10n_ro_edi.document"].sudo().create({"invoice_id": invoice.id, "state": "invoice_sent"})
        invoice.l10n_ro_edi_state = "invoice_not_indexed"
        return invoice

    def test_reset_not_indexed_marks_refused(self):
        """Negăsită în SPV la sincronizare: trimiterea devine refuzată și se poate retrimite."""
        invoice = self._create_not_indexed_invoice()
        with patch.object(NativeAccountMove, "_l10n_ro_edi_fetch_invoices", return_value=None) as sync:
            invoice.action_l10n_ro_edi_reset_not_indexed()
            sync.assert_called_once()
        self.assertEqual(invoice.l10n_ro_edi_state, "invoice_refused")
        self.assertEqual(invoice.l10n_ro_edi_document_ids.mapped("state"), ["invoice_refused"])
        self.assertIn("resetată manual", invoice.message_ids[0].body)

    def test_reset_not_indexed_found_at_sync(self):
        """Găsită în SPV la sincronizare: nu se resetează nimic, rămâne validată."""
        invoice = self._create_not_indexed_invoice()

        def _sync_validates(model):
            invoice.l10n_ro_edi_document_ids.sudo().unlink()
            self.env["l10n_ro_edi.document"].sudo().create({"invoice_id": invoice.id, "state": "invoice_validated"})

        with patch.object(NativeAccountMove, "_l10n_ro_edi_fetch_invoices", _sync_validates):
            invoice.action_l10n_ro_edi_reset_not_indexed()
        self.assertEqual(invoice.l10n_ro_edi_state, "invoice_validated")
        self.assertEqual(invoice.l10n_ro_edi_document_ids.mapped("state"), ["invoice_validated"])

    def test_reset_requires_not_indexed(self):
        invoice = self._create_posted_invoice()
        with self.assertRaises(UserError):
            invoice.action_l10n_ro_edi_reset_not_indexed()
