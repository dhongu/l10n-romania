# ©  2026 Terrabit
# See README.rst file on addons root folder for license details

from datetime import timedelta
from unittest.mock import patch

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

FETCH_PATH = "odoo.addons.l10n_ro_edi.models.account_move._request_ciusro_fetch_status"
DOWNLOAD_PATH = "odoo.addons.l10n_ro_edi.models.account_move._request_ciusro_download_answer"
LOGGER = "odoo.addons.l10n_ro_efactura_enhancement.models.account_move"

# ANAF finished the validation and accepted the invoice
FETCH_VALIDATED = {"key_download": "KEY", "state_status": "ok"}
DOWNLOAD_VALIDATED = {
    "signature": {"key_signature": "SIG", "key_certificate": "CERT", "attachment_raw": b"<Signature/>"},
}


@tagged("post_install", "-at_install")
class TestCronFetchStatusRetrigger(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.company.l10n_ro_edi_access_token = "TESTTOKEN"
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner RO",
                "country_id": cls.env.ref("base.ro").id,
                "state_id": cls.env.ref("base.RO_B").id,
                "city": "Bucuresti",
                "street": "Str. Test 1",
            }
        )
        cls.product = cls.env["product.product"].create({"name": "Test Product"})
        cls.cron = cls.env.ref("l10n_ro_efactura_enhancement.ir_cron_l10n_ro_edi_fetch_status")
        # Isolate from invoices already waiting in the SPV in the test database.
        cls.env["account.move"].search([("l10n_ro_edi_state", "=", "invoice_sent")]).l10n_ro_edi_document_ids.unlink()

    def _create_sent_invoice(self, index):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": fields.Date.today() - timedelta(days=3),
                "invoice_line_ids": [(0, 0, {"product_id": self.product.id, "quantity": 1, "price_unit": 100})],
            }
        )
        invoice.action_post()
        invoice.l10n_ro_edi_index = index
        self.env["l10n_ro_edi.document"].create(
            {
                "invoice_id": invoice.id,
                "state": "invoice_sent",
                "datetime": fields.Datetime.now(),
            }
        )
        self.assertEqual(invoice.l10n_ro_edi_state, "invoice_sent")
        return invoice

    def _run_fetch(self, fetch_result, limit):
        with (
            patch(FETCH_PATH, return_value=fetch_result) as mock_fetch,
            patch(DOWNLOAD_PATH, return_value=DOWNLOAD_VALIDATED),
            patch.object(type(self.cron), "_trigger", autospec=True) as mock_trigger,
        ):
            self.env["account.move"]._cron_l10n_ro_edi_fetch_status(limit=limit)
        return mock_fetch, mock_trigger

    def _fetch_cron_triggers(self, mock_trigger):
        # auto_send reschedules its own cron through the same patched method
        return [c for c in mock_trigger.call_args_list if c.args[0] == self.cron]

    @mute_logger(LOGGER)
    def test_no_answer_from_anaf_no_retrigger(self):
        """ANAF nu răspunde ({}): nicio factură nu se schimbă, deci nu se reia la +2 minute."""
        invoices = self._create_sent_invoice("1001") | self._create_sent_invoice("1002")
        mock_fetch, mock_trigger = self._run_fetch({}, limit=2)
        self.assertEqual(mock_fetch.call_count, 2)
        self.assertFalse(self._fetch_cron_triggers(mock_trigger))
        invoices.invalidate_recordset(["l10n_ro_edi_state"])
        self.assertEqual(set(invoices.mapped("l10n_ro_edi_state")), {"invoice_sent"})

    @mute_logger(LOGGER)
    def test_full_batch_with_progress_retriggers(self):
        """Lot plin și facturi care își schimbă starea: se reia la +2 minute."""
        invoices = self._create_sent_invoice("2001") | self._create_sent_invoice("2002")
        _mock_fetch, mock_trigger = self._run_fetch(FETCH_VALIDATED, limit=2)
        self.assertEqual(len(self._fetch_cron_triggers(mock_trigger)), 1)
        invoices.invalidate_recordset(["l10n_ro_edi_state"])
        self.assertEqual(set(invoices.mapped("l10n_ro_edi_state")), {"invoice_validated"})

    @mute_logger(LOGGER)
    def test_partial_batch_with_progress_no_retrigger(self):
        """Lot incomplet: toate facturile au fost verificate în acest ciclu, nu se reia."""
        self._create_sent_invoice("3001")
        self._create_sent_invoice("3002")
        _mock_fetch, mock_trigger = self._run_fetch(FETCH_VALIDATED, limit=5)
        self.assertFalse(self._fetch_cron_triggers(mock_trigger))

    @mute_logger(LOGGER)
    def test_auto_send_does_not_retrigger_fetch_without_progress(self):
        """Apelul intern din auto_send respectă aceeași regulă de retrigger."""
        self._create_sent_invoice("4001")
        self._create_sent_invoice("4002")
        with (
            patch(FETCH_PATH, return_value={}),
            patch.object(type(self.cron), "_trigger", autospec=True) as mock_trigger,
            patch.object(type(self.env["account.move.send"]), "_generate_and_send_invoices"),
        ):
            self.env["account.move"]._cron_l10n_ro_edi_auto_send(limit=2)
        self.assertFalse(self._fetch_cron_triggers(mock_trigger))
