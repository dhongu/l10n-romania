# ©  2026 Terrabit
# See README.rst file on addons root folder for license details

from datetime import timedelta
from unittest.mock import patch

import requests

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

SEND_METHOD = "odoo.addons.l10n_ro_edi.models.ciusro_document.L10nRoEdiDocument._request_ciusro_send_invoice"
FETCH_METHOD = "odoo.addons.l10n_ro_edi.models.ciusro_document.L10nRoEdiDocument._request_ciusro_fetch_status"
LOGGERS = (
    "odoo.addons.l10n_ro_efactura_enhancement.models.account_move",
    "odoo.addons.account.models.account_move_send",
)


@tagged("post_install", "-at_install")
class TestSpvSendUncertain(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.company.write(
            {
                "l10n_ro_edi_access_token": "TESTTOKEN",
                "country_id": cls.env.ref("base.ro").id,
                "account_fiscal_country_id": cls.env.ref("base.ro").id,
                "vat": "RO1234567897",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner RO",
                "country_id": cls.env.ref("base.ro").id,
                "state_id": cls.env.ref("base.RO_B").id,
                "city": "Bucuresti",
                "street": "Str. Test 1",
                "invoice_edi_format": "ciusro",
            }
        )
        cls.product = cls.env["product.product"].create({"name": "Test Product", "taxes_id": [(5,)]})
        # Isolate the auto-send cron from invoices already in the test database.
        cls.env["account.move"].search(
            [("move_type", "in", ("out_invoice", "out_refund")), ("state", "=", "posted")]
        ).l10n_ro_edi_send_uncertain = True

    def _create_invoice(self, days_ago=1):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": fields.Date.today() - timedelta(days=days_ago),
                "invoice_line_ids": [(0, 0, {"product_id": self.product.id, "quantity": 1, "price_unit": 100})],
            }
        )
        invoice.action_post()
        return invoice

    def _patch_export(self):
        # The CIUS-RO XML content is irrelevant here: only the SPV upload matters.
        return patch.object(
            type(self.env["account.edi.xml.ubl_ro"]), "_export_invoice", return_value=(b"<Invoice/>", set())
        )

    @mute_logger(*LOGGERS)
    def test_cron_timeout_does_not_stop_batch(self):
        """Timeout la prima trimitere a unei facturi: cron-ul de auto-send nu
        se oprește cu IndexError, iar restul lotului se trimite în SPV."""
        timed_out = self._create_invoice(days_ago=1)
        other = self._create_invoice(days_ago=2)
        calls = []

        def _send(*args, **kwargs):
            calls.append(1)
            if len(calls) == 1:  # cron-ul trimite în ordinea datei descrescătoare
                raise requests.ReadTimeout("timeout")
            return {"key_loading": "7000000001"}

        with (
            patch(SEND_METHOD, side_effect=_send),
            patch(FETCH_METHOD, return_value={}),
            self._patch_export(),
            patch.object(self.env.registry, "in_test_mode", return_value=True),
        ):
            self.env["account.move"]._cron_l10n_ro_edi_auto_send()

        self.assertEqual(len(calls), 2, "Ambele facturi trebuie încercate")
        self.assertTrue(timed_out.l10n_ro_edi_send_uncertain)
        self.assertFalse(timed_out.l10n_ro_edi_state)
        failed = timed_out.l10n_ro_edi_document_ids
        self.assertEqual(failed.mapped("state"), ["invoice_sending_failed"])
        self.assertIn("timeout", failed.message)
        self.assertEqual(other.l10n_ro_edi_state, "invoice_sent")
        self.assertEqual(other.l10n_ro_edi_index, "7000000001")

        # La rularea următoare factura incertă nu se mai retrimite.
        with (
            patch(SEND_METHOD) as mock_send,
            patch(FETCH_METHOD, return_value={}),  # ANAF nu a răspuns încă
            self._patch_export(),
            patch.object(self.env.registry, "in_test_mode", return_value=True),
        ):
            self.env["account.move"]._cron_l10n_ro_edi_auto_send()
        mock_send.assert_not_called()

    def test_send_wizard_skips_uncertain_invoice(self):
        """Butonul Trimite (account.move.send) nu mai încarcă în SPV o factură
        incertă și afișează un avertisment pentru operator."""
        invoice = self._create_invoice()
        move_send = self.env["account.move.send"]
        self.assertTrue(move_send._is_ro_edi_applicable(invoice))

        invoice.l10n_ro_edi_send_uncertain = True
        self.assertFalse(move_send._is_ro_edi_applicable(invoice))
        move_data = {invoice: move_send._get_default_sending_settings(invoice, sending_methods={"manual"})}
        alerts = move_send._get_alerts(invoice, move_data)
        self.assertIn("l10n_ro_efactura_warning_uncertain_moves", alerts)
        self.assertIn(invoice.name, alerts["l10n_ro_efactura_warning_uncertain_moves"]["message"])

        wizard = self.env["account.move.send.wizard"].with_context(active_model="account.move", active_ids=invoice.ids)
        wizard = wizard.create({})
        checkbox = wizard.extra_edi_checkboxes.get("ro_spv")
        self.assertTrue(checkbox and checkbox["readonly"] and not checkbox["checked"])

        with patch(SEND_METHOD) as mock_send, self._patch_export():
            move_send._generate_and_send_invoices(invoice, sending_methods={"manual"})
        mock_send.assert_not_called()

    def test_send_to_spv_only_blocks_uncertain_invoice(self):
        """„Trimite in SPV” refuză o selecție care conține facturi incerte."""
        invoice = self._create_invoice()
        invoice.l10n_ro_edi_send_uncertain = True
        with (
            patch.object(type(self.env["account.move.send"]), "_generate_and_send_invoices") as mock_send,
            self.assertRaisesRegex(UserError, invoice.name),
        ):
            invoice.action_send_to_spv_only()
        mock_send.assert_not_called()
