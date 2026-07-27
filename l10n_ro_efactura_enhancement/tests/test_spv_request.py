# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from unittest.mock import patch

import requests

from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from odoo.addons.l10n_ro_edi.models.utils import (
    _request_ciusro_download_answer,
    _request_ciusro_fetch_status,
)

from ..models.spv_request import check_spv_answer


class FakeResponse:
    """Minimal stand-in for a ``requests`` response object."""

    def __init__(self, content, status_code=200):
        self.content = content
        self.status_code = status_code


@tagged("post_install", "-at_install")
class TestSpvAnswerCheck(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.l10n_ro_edi_access_token = "test-token"

    def _fetch_status(self, content):
        """Rulează stareMesaj cu un răspuns SPV controlat."""
        with patch.object(requests.Session, "request", return_value=FakeResponse(content)):
            return _request_ciusro_fetch_status(
                company=self.company,
                key_loading="123456",
                session=requests.Session(),
            )

    def test_check_answer_accepts_expected_payload(self):
        """Payload-ul așteptat pentru fiecare endpoint trece neatins."""
        for endpoint, content in (
            ("stareMesaj", b'<?xml version="1.0"?><header stare="ok"/>'),
            ("upload", b"<header index_incarcare='1'/>"),
            ("descarcare", b"PK\x03\x04rest-of-zip"),
            ("transformare", b"%PDF-1.7"),
            ("listaMesajeFactura", b'{"mesaje": []}'),
        ):
            with self.subTest(endpoint=endpoint):
                self.assertIsNone(check_spv_answer(self.company, endpoint, content))

    def test_check_answer_ignores_unknown_endpoint(self):
        """Un endpoint necunoscut nu este validat, ca să nu blocăm fluxuri noi."""
        self.assertIsNone(check_spv_answer(self.company, "endpointNou", b"orice"))

    def test_check_answer_reports_json_error(self):
        """Eroarea JSON de la ANAF este extrasă ca mesaj lizibil."""
        error = check_spv_answer(
            self.company,
            "stareMesaj",
            b'{"eroare": "Nu exista niciun mesaj cu id_incarcare=123456"}',
        )
        self.assertIn("Nu exista niciun mesaj", error)

    def test_check_answer_reports_html_page(self):
        """Pagina HTML de gateway este raportată fără markup."""
        error = check_spv_answer(
            self.company,
            "descarcare",
            b"<html><body><h1>503 Service Unavailable</h1></body></html>",
        )
        self.assertIn("503 Service Unavailable", error)
        self.assertNotIn("<h1>", error)

    def test_check_answer_reports_empty_body(self):
        """Corpul gol este raportat explicit."""
        self.assertIn("empty body", check_spv_answer(self.company, "stareMesaj", b"  "))

    @mute_logger("odoo.addons.l10n_ro_efactura_enhancement.models.spv_request")
    def test_fetch_status_returns_error_instead_of_crashing(self):
        """stareMesaj cu răspuns non-XML întoarce eroare, nu XMLSyntaxError."""
        result = self._fetch_status(b'{"eroare": "Limita de apeluri a fost atinsa"}')
        self.assertIn("error", result)
        self.assertIn("Limita de apeluri", result["error"])

    def test_fetch_status_still_parses_valid_xml(self):
        """Răspunsul XML valid este procesat ca înainte de patch."""
        result = self._fetch_status(
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<header xmlns="mfp:anaf:dgti:efactura:stareMesajFactura:v1"'
            b' stare="ok" id_descarcare="987"/>'
        )
        self.assertEqual(result, {"key_download": "987", "state_status": "ok"})

    @mute_logger("odoo.addons.l10n_ro_efactura_enhancement.models.spv_request")
    def test_download_answer_returns_error_instead_of_crashing(self):
        """descarcare cu răspuns non-ZIP întoarce eroare, nu BadZipFile."""
        with patch.object(
            requests.Session,
            "request",
            return_value=FakeResponse(b'{"eroare": "Limita de descarcari atinsa"}'),
        ):
            result = _request_ciusro_download_answer(
                company=self.company,
                key_download="987",
                session=requests.Session(),
            )
        self.assertIn("error", result)
        self.assertIn("Limita de descarcari", result["error"])
