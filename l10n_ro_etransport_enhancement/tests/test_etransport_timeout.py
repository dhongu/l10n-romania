# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
from unittest.mock import MagicMock, patch

import requests

from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from odoo.addons.l10n_ro_edi_stock.models.etransport_api import ETransportAPI
from odoo.addons.l10n_ro_edi_stock.models.stock_picking import Picking as CorePicking

from ..models.etransport_api import DEFAULT_ETRANSPORT_TIMEOUT


@tagged("post_install", "-at_install")
class TestETransportTimeout(TransactionCase):
    """Timeout configurabil și tratarea căderilor de rețea către ANAF."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.company.id)], limit=1)
        cls.partner = cls.env["res.partner"].create({"name": "Partner Timeout"})

    def _create_picking(self):
        picking_type = self.env["stock.picking.type"].search(
            [("code", "=", "outgoing"), ("warehouse_id", "=", self.warehouse.id)],
            limit=1,
        )
        return self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "partner_id": self.partner.id,
                "location_id": picking_type.default_location_src_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id,
            }
        )

    def _mocked_response(self):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"ExecutionStatus": 0, "index_incarcare": "1", "UIT": "X"}
        return response

    def test_default_timeout_on_company(self):
        """Compania primește implicit timeout-ul modulului, nu cele 10s din standard."""
        self.assertEqual(self.company.l10n_ro_etransport_timeout, DEFAULT_ETRANSPORT_TIMEOUT)

    def test_company_timeout_is_used(self):
        """Timeout-ul configurat pe companie ajunge în cererea HTTP."""
        self.company.l10n_ro_etransport_timeout = 45

        with patch.object(requests.Session, "request", return_value=self._mocked_response()) as mocked_request:
            ETransportAPI().get_status(company_id=self.company, document_load_id="1")

        self.assertEqual(mocked_request.call_args.kwargs["timeout"], 45)

    def test_fallback_timeout_when_not_configured(self):
        """Fără valoare pe companie se folosește timeout-ul implicit, nu 10s."""
        self.company.l10n_ro_etransport_timeout = 0

        with patch.object(requests.Session, "request", return_value=self._mocked_response()) as mocked_request:
            ETransportAPI().get_status(company_id=self.company, document_load_id="1")

        self.assertEqual(mocked_request.call_args.kwargs["timeout"], DEFAULT_ETRANSPORT_TIMEOUT)

    # avertismentul e chiar comportamentul testat; fără mute, `checklog-odoo` din CI
    # tratează orice WARNING din log ca eșec
    @mute_logger("odoo.addons.l10n_ro_etransport_enhancement.models.stock_picking")
    def test_send_timeout_creates_failed_document(self):
        """Un timeout la trimitere produce document 'stock_sending_failed', nu traceback RPC."""
        picking = self._create_picking()
        error = requests.exceptions.ReadTimeout("Read timed out. (read timeout=10)")

        with patch.object(CorePicking, "_l10n_ro_edi_stock_send_etransport_document", side_effect=error):
            picking._l10n_ro_edi_stock_send_etransport_document(send_type="send")

        document = picking._l10n_ro_edi_stock_get_last_document("stock_sending_failed")
        self.assertTrue(document, "Trebuie creat un document eșuat, ca livrarea să nu rămână fără urmă")
        self.assertIn("SPV", document.message, "Mesajul trebuie să avertizeze despre verificarea în SPV")

    @mute_logger("odoo.addons.l10n_ro_etransport_enhancement.models.stock_picking")
    def test_status_fetch_timeout_does_not_stop_the_batch(self):
        """O cădere de rețea la un picking nu oprește interogarea celorlalte."""
        pickings = self._create_picking() | self._create_picking()
        calls = []

        def _fetch(self):
            calls.append(self.id)
            if len(calls) == 1:
                raise requests.exceptions.ReadTimeout("Read timed out.")

        with patch.object(CorePicking, "_l10n_ro_edi_stock_fetch_document_status", _fetch):
            pickings._l10n_ro_edi_stock_fetch_document_status()

        self.assertEqual(len(calls), 2, "Al doilea picking trebuie interogat chiar dacă primul a picat")
