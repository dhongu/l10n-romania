# See README.rst file on addons root folder for license details
from datetime import timedelta
from unittest.mock import patch

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.l10n_ro_efactura_enhancement.models.account_move import (
    MAX_SPV_SEND_RETRIES,
    SPV_SEND_RETRY_DELAY,
)

SEND = "odoo.addons.account.models.account_move_send.AccountMoveSend._generate_and_send_invoices"
FETCH = "odoo.addons.l10n_ro_efactura_enhancement.models.account_move.AccountMove._cron_l10n_ro_edi_fetch_status"


@tagged("post_install", "-at_install")
class TestCronRetryLimit(TransactionCase):
    """The auto-send cron must stop retrying an invoice that keeps failing.

    On 19.0 a failed upload creates no l10n_ro_edi.document, so the old limit,
    which counted ``invoice_sending_failed`` documents, never triggered: a
    broken invoice was retried every night and on every 5-minute retrigger.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.l10n_ro_edi_access_token = "token"
        partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner Cron",
                "country_id": cls.env.ref("base.ro").id,
                "state_id": cls.env.ref("base.RO_B").id,
                "city": "SECTOR1",
                "street": "Str. Test 1",
            }
        )
        cls.invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "invoice_date": fields.Date.today() - timedelta(days=1),
                "invoice_line_ids": [(0, 0, {"name": "Test", "quantity": 1, "price_unit": 100})],
            }
        )
        cls.invoice.action_post()

    def _run_cron(self):
        # The send "fails": nothing is uploaded, the state stays False.
        with patch(SEND) as send, patch(FETCH):
            self.env["account.move"]._cron_l10n_ro_edi_auto_send()
        return send

    def _age_last_attempt(self):
        self.invoice.l10n_ro_spv_last_send_attempt = fields.Datetime.now() - SPV_SEND_RETRY_DELAY - timedelta(minutes=1)

    def test_failed_attempts_are_counted_until_the_limit(self):
        for attempt in range(1, MAX_SPV_SEND_RETRIES + 1):
            send = self._run_cron()
            self.assertIn(self.invoice, send.call_args.args[0])
            self.assertEqual(self.invoice.l10n_ro_spv_send_attempts, attempt)
            self._age_last_attempt()

        send = self._run_cron()
        self.assertFalse(send.called, "An invoice with exhausted retries must not be sent again")
        self.assertEqual(self.invoice.l10n_ro_spv_send_attempts, MAX_SPV_SEND_RETRIES)

    def test_retrigger_does_not_retry_a_fresh_failure(self):
        self._run_cron()
        send = self._run_cron()
        self.assertFalse(send.called, "The 5-minute retrigger must not retry the invoice that just failed")
        self.assertEqual(self.invoice.l10n_ro_spv_send_attempts, 1)

    def test_limit_is_announced_once_in_chatter(self):
        for _attempt in range(MAX_SPV_SEND_RETRIES):
            self._run_cron()
            self._age_last_attempt()
        self._run_cron()
        messages = self.invoice.message_ids.filtered(lambda m: "nu o mai reîncearcă" in (m.body or ""))
        self.assertEqual(len(messages), 1)

    def test_reset_to_draft_gives_the_attempts_back(self):
        self.invoice.write(
            {
                "l10n_ro_spv_send_attempts": MAX_SPV_SEND_RETRIES,
                "l10n_ro_spv_last_send_attempt": fields.Datetime.now(),
            }
        )
        self.invoice.button_draft()
        self.assertEqual(self.invoice.l10n_ro_spv_send_attempts, 0)
        self.assertFalse(self.invoice.l10n_ro_spv_last_send_attempt)
