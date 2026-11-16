# ©  2026 Terrabit
# See README.rst file on addons root folder for license details

from datetime import timedelta
from unittest.mock import patch

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from odoo.addons.l10n_ro_efactura_enhancement.models.account_move import MAX_SPV_SEND_RETRIES

SEND_PATH = "odoo.addons.l10n_ro_edi.models.account_move._request_ciusro_send_invoice"
FETCH_PATH = "odoo.addons.l10n_ro_edi.models.account_move._request_ciusro_fetch_status"
LOGGER = "odoo.addons.l10n_ro_efactura_enhancement.models.account_move"

ANAF_OK = {"key_loading": "IDX"}
ANAF_DOWN = {"error": "Serviciul SPV nu este disponibil"}


@tagged("post_install", "-at_install")
class TestCronAutoSendRetries(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.company.l10n_ro_edi_access_token = "TESTTOKEN"
        cls.company.l10n_ro_spv_cron_report_email = False
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Client Persoana Fizica",
                "country_id": cls.env.ref("base.ro").id,
                "state_id": cls.env.ref("base.RO_B").id,
                "city": "Bucuresti",
                "street": "Str. Test 1",
            }
        )
        cls.product = cls.env["product.product"].create({"name": "Test Product"})
        cls.cron = cls.env.ref("l10n_ro_efactura_enhancement.ir_cron_l10n_ro_edi_auto_send")
        # Isolate from invoices of the test database still waiting for the SPV:
        # mark them as exhausted, so the cron only sees the invoices of the test.
        cls.env["account.move"].search(
            [("move_type", "in", ("out_invoice", "out_refund")), ("l10n_ro_edi_state", "=", False)]
        ).l10n_ro_spv_send_failures = MAX_SPV_SEND_RETRIES

    def _create_invoice(self, days_ago=3):
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

    def _run_cron(self, anaf_answer, limit=20):
        """Run the auto-send cron with the SPV upload answered by ``anaf_answer``.

        The XML generation of account.move.send is replaced by a fixed XML; the
        upload itself goes through l10n_ro_edi, only the HTTP call is mocked.
        """
        sent = self.env["account.move"]

        def fake_generate_and_send(_self, moves, **kwargs):
            nonlocal sent
            sent |= moves
            for move in moves:
                move._l10n_ro_edi_send_invoice(b"<Invoice/>")

        with (
            patch(SEND_PATH, return_value=anaf_answer) as mock_send,
            patch(FETCH_PATH, return_value={}),
            patch.object(
                type(self.env["account.move.send"]), "_generate_and_send_invoices", autospec=True
            ) as mock_generate,
            patch.object(type(self.cron), "_trigger", autospec=True) as mock_trigger,
        ):
            mock_generate.side_effect = fake_generate_and_send
            self.env["account.move"]._cron_l10n_ro_edi_auto_send(limit=limit)
        auto_send_triggers = [c for c in mock_trigger.call_args_list if c.args[0] == self.cron]
        return sent, mock_send, auto_send_triggers

    @mute_logger(LOGGER)
    def test_failed_send_is_counted_until_the_limit(self):
        """ANAF refuză încărcarea: eșecul se numără și, după limită, factura nu se mai trimite."""
        invoice = self._create_invoice()
        for attempt in range(1, MAX_SPV_SEND_RETRIES + 1):
            sent, _mock_send, _triggers = self._run_cron(ANAF_DOWN)
            self.assertEqual(sent, invoice)
            self.assertFalse(invoice.l10n_ro_edi_state)
            self.assertEqual(invoice.l10n_ro_spv_send_failures, attempt)

        sent, mock_send, _triggers = self._run_cron(ANAF_DOWN)
        self.assertFalse(sent, "the retry limit must stop the automatic send")
        self.assertFalse(mock_send.called)
        self.assertEqual(invoice.l10n_ro_spv_send_failures, MAX_SPV_SEND_RETRIES)

    @mute_logger(LOGGER)
    def test_successful_send_is_not_counted(self):
        """Încărcare reușită (și după un eșec): factura e „Trimis”, contorul nu crește."""
        invoice = self._create_invoice()
        self._run_cron(ANAF_DOWN)
        self.assertEqual(invoice.l10n_ro_spv_send_failures, 1)

        self._run_cron(ANAF_OK)
        self.assertEqual(invoice.l10n_ro_edi_state, "invoice_sent")
        self.assertEqual(invoice.l10n_ro_spv_send_failures, 1)

    @mute_logger(LOGGER)
    def test_report_lists_retrying_and_exhausted(self):
        """Raportul primește facturile reluate și pe cele cu reîncercările epuizate."""
        retrying = self._create_invoice()
        retrying.l10n_ro_spv_send_failures = 1
        exhausted = self._create_invoice()
        exhausted.l10n_ro_spv_send_failures = MAX_SPV_SEND_RETRIES
        with patch.object(type(self.env["account.move"]), "_l10n_ro_spv_send_cron_report", autospec=True) as report:
            self._run_cron(ANAF_DOWN)
        stats = report.call_args.args[2]
        self.assertEqual(stats["retrying"], retrying)
        self.assertEqual(stats["exhausted"] & (retrying | exhausted), exhausted)
        self.assertEqual(stats["failed_now"], retrying)

    @mute_logger(LOGGER)
    def test_all_failed_no_retrigger(self):
        """Lot plin, dar toate trimiterile eșuează: cron-ul nu se reia la +5 minute."""
        for _i in range(3):
            self._create_invoice()
        sent, _mock_send, triggers = self._run_cron(ANAF_DOWN, limit=2)
        self.assertEqual(len(sent), 2)
        self.assertFalse(triggers)

    @mute_logger(LOGGER)
    def test_progress_retriggers(self):
        """Lot plin și cel puțin o factură încărcată: cron-ul se reia la +5 minute."""
        for _i in range(3):
            self._create_invoice()
        sent, _mock_send, triggers = self._run_cron(ANAF_OK, limit=2)
        self.assertEqual(len(sent), 2)
        self.assertEqual(len(triggers), 1)

    @mute_logger(LOGGER)
    def test_partial_batch_no_retrigger(self):
        """Toți candidații au încăput în lot: nu e nimic de reluat."""
        self._create_invoice()
        self._create_invoice()
        _sent, _mock_send, triggers = self._run_cron(ANAF_OK, limit=5)
        self.assertFalse(triggers)

    @mute_logger(LOGGER)
    def test_failing_invoices_do_not_block_new_ones(self):
        """Facturile care au mai eșuat trec la coada lotului, după cele netrimise încă."""
        failing = self._create_invoice(days_ago=2)
        failing.l10n_ro_spv_send_failures = 1
        fresh = self._create_invoice(days_ago=4)
        sent, _mock_send, _triggers = self._run_cron(ANAF_OK, limit=1)
        self.assertEqual(sent, fresh)

    def test_reset_to_draft_resets_counter(self):
        """Factura readusă în ciornă și corectată primește din nou toate reîncercările."""
        invoice = self._create_invoice()
        invoice.l10n_ro_spv_send_failures = MAX_SPV_SEND_RETRIES
        invoice.button_draft()
        self.assertEqual(invoice.l10n_ro_spv_send_failures, 0)
