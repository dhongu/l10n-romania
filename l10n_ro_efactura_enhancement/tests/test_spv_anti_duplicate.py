# ©  2026 Terrabit
# See README.rst file on addons root folder for license details

from unittest.mock import patch

import requests

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

SEND_METHOD = "odoo.addons.l10n_ro_edi.models.ciusro_document" ".L10nRoEdiDocument._request_ciusro_send_invoice"
LOGGER = "odoo.addons.l10n_ro_efactura_enhancement.models.account_move"


@tagged("post_install", "-at_install")
class TestSpvAntiDuplicate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        # pre_send check requires an access token to proceed to the upload
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

    def _create_invoice(self):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [(0, 0, {"product_id": self.product.id, "quantity": 1, "price_unit": 100})],
            }
        )
        invoice.action_post()
        return invoice

    @mute_logger(LOGGER)
    def test_timeout_flags_uncertain_and_blocks_resend(self):
        """Un timeout la trimitere marchează factura ca incertă, fără document
        'invoice_sent', și o exclude din cronul de auto-send."""
        invoice = self._create_invoice()
        with patch(SEND_METHOD, side_effect=requests.ReadTimeout("timeout")):
            invoice._l10n_ro_edi_send_invoice("<Invoice/>")

        self.assertTrue(invoice.l10n_ro_edi_send_uncertain, "Factura trebuie marcată incertă")
        self.assertFalse(
            invoice.l10n_ro_edi_document_ids.filtered(lambda d: d.state == "invoice_sent"),
            "Nu trebuie să existe document 'invoice_sent' după timeout",
        )
        # cronul de auto-send selectează state=False + uncertain=False -> exclusă
        candidates = self.env["account.move"].search(
            [
                ("l10n_ro_edi_state", "=", False),
                ("l10n_ro_edi_send_uncertain", "=", False),
                ("id", "=", invoice.id),
            ]
        )
        self.assertNotIn(invoice, candidates, "Factura incertă nu trebuie auto-retrimisă")

    @mute_logger(LOGGER)
    def test_idempotency_guard_skips_when_index_present(self):
        """Dacă factura are deja index de încărcare, nu se mai trimite."""
        invoice = self._create_invoice()
        invoice.l10n_ro_edi_index = "6520851057"
        with patch(SEND_METHOD) as mock_send:
            invoice._l10n_ro_edi_send_invoice("<Invoice/>")
        mock_send.assert_not_called()

    @mute_logger(LOGGER)
    def test_idempotency_guard_skips_when_sent_document_present(self):
        """Dacă factura are deja un document validat, nu se mai trimite."""
        invoice = self._create_invoice()
        self.env["l10n_ro_edi.document"].create(
            {
                "invoice_id": invoice.id,
                "state": "invoice_validated",
                "key_loading": "6520851057",
                "datetime": fields.Datetime.now(),
            }
        )
        with patch(SEND_METHOD) as mock_send:
            invoice._l10n_ro_edi_send_invoice("<Invoice/>")
        mock_send.assert_not_called()

    def test_clear_uncertain(self):
        """Butonul de resetare debifează marcajul incert."""
        invoice = self._create_invoice()
        invoice.l10n_ro_edi_send_uncertain = True
        invoice.action_l10n_ro_edi_clear_send_uncertain()
        self.assertFalse(invoice.l10n_ro_edi_send_uncertain)
