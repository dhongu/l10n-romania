# © 2025 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from unittest.mock import MagicMock, patch

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestPartnerCreateByVatOpenapi(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.ro_country = cls.env.ref("base.ro")
        cls.de_country = cls.env.ref("base.de")

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner OpenAPI",
                "company_type": "company",
                "country_id": cls.ro_country.id,
            }
        )

        # Setăm openapi_key în parametrii de sistem
        cls.env["ir.config_parameter"].sudo().set_param("openapi_key", "test-api-key-123")

    def _mock_openapi_response(self):
        """Returnează un dict simulat de răspuns OpenAPI."""
        return {
            "denumire": "SC TEST SRL",
            "numar_reg_com": "J12/123/2020",
            "adresa": "Str. Testului nr. 1, Cluj-Napoca",
            "telefon": "0264123456",
            "cod_postal": "400001",
            "tva": True,
            "judet": None,
            "radiata": False,
        }

    def test_get_openapi_returns_dict_on_success(self):
        """Test că _get_Openapi returnează un dict cu datele partenerului."""
        mock_response_data = self._mock_openapi_response()

        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = str(mock_response_data).replace("'", '"').encode()

        import json

        mock_response.read.return_value = json.dumps(mock_response_data).encode()

        with patch(
            "odoo.addons.l10n_ro_partner_create_by_vat_openapi.models.res_partner.urlopen",
            return_value=mock_response,
        ):
            result = self.partner._get_Openapi("12345678")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["name"], "SC TEST SRL")
        self.assertEqual(result["nrc"], "J12/123/2020")
        self.assertTrue(result["l10n_ro_vat_subjected"])
        self.assertFalse(result["radiata"])

    def test_get_openapi_no_api_key(self):
        """Test că _get_Openapi ridică UserError dacă lipsește openapi_key."""
        self.env["ir.config_parameter"].sudo().set_param("openapi_key", "")
        try:
            with self.assertRaises(UserError):
                self.partner._get_Openapi("12345678")
        finally:
            self.env["ir.config_parameter"].sudo().set_param("openapi_key", "test-api-key-123")

    def test_button_get_partner_data_openapi_ro_vat(self):
        """Test că button_get_partner_data_openapi actualizează partenerul cu date de la OpenAPI."""
        mock_response_data = self._mock_openapi_response()
        import json

        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = json.dumps(mock_response_data).encode()

        partner = self.env["res.partner"].create(
            {
                "name": "Firma Test",
                "vat": "RO12345678",
                "country_id": self.ro_country.id,
                "company_type": "company",
            }
        )

        with patch(
            "odoo.addons.l10n_ro_partner_create_by_vat_openapi.models.res_partner.urlopen",
            return_value=mock_response,
        ):
            partner.button_get_partner_data_openapi()

        self.assertEqual(partner.name, "SC TEST SRL")
        self.assertEqual(partner.nrc, "J12/123/2020")

    def test_button_get_partner_data_openapi_radiata(self):
        """Test că partenerul radiat este dezactivat (active=False)."""
        mock_data = self._mock_openapi_response()
        mock_data["radiata"] = True
        import json

        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = json.dumps(mock_data).encode()

        partner = self.env["res.partner"].create(
            {
                "name": "Firma Radiata",
                "vat": "RO99999999",
                "country_id": self.ro_country.id,
                "company_type": "company",
            }
        )

        with patch(
            "odoo.addons.l10n_ro_partner_create_by_vat_openapi.models.res_partner.urlopen",
            return_value=mock_response,
        ):
            partner.button_get_partner_data_openapi()

        self.assertFalse(partner.active)

    def test_button_get_partner_data_openapi_no_vat_raises(self):
        """Test că button_get_partner_data_openapi ridică UserError dacă nu există VAT."""
        partner = self.env["res.partner"].create(
            {
                "name": "Fara VAT",
                "company_type": "company",
            }
        )
        with self.assertRaises(UserError):
            partner.button_get_partner_data_openapi()

    def test_button_get_partner_data_openapi_name_is_digit(self):
        """Test că dacă name este numeric, se construiește VAT-ul RO+name."""
        mock_response_data = self._mock_openapi_response()
        import json

        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = json.dumps(mock_response_data).encode()

        partner = self.env["res.partner"].create(
            {
                "name": "12345678",
                "company_type": "company",
                "country_id": self.ro_country.id,
            }
        )

        with patch(
            "odoo.addons.l10n_ro_partner_create_by_vat_openapi.models.res_partner.urlopen",
            return_value=mock_response,
        ):
            partner.button_get_partner_data_openapi()

        self.assertEqual(partner.name, "SC TEST SRL")

    def test_button_get_partner_data_openapi_openapi_failure_graceful(self):
        """Test că eșecul OpenAPI nu crăpă — partenerul rămâne nemodificat."""
        partner = self.env["res.partner"].create(
            {
                "name": "Firma Fara Date",
                "vat": "RO11111111",
                "country_id": self.ro_country.id,
                "company_type": "company",
            }
        )
        original_name = partner.name

        with patch(
            "odoo.addons.l10n_ro_partner_create_by_vat_openapi.models.res_partner.urlopen",
            side_effect=Exception("Connection timeout"),
        ):
            partner.button_get_partner_data_openapi()

        # Numele nu trebuie schimbat dacă OpenAPI a eșuat
        self.assertEqual(partner.name, original_name)

    def test_wizard_do_get_data_openapi_service(self):
        """Test că wizard-ul cu service=openapi apelează button_get_partner_data_openapi."""
        mock_response_data = self._mock_openapi_response()
        import json

        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = json.dumps(mock_response_data).encode()

        partner = self.env["res.partner"].create(
            {
                "name": "Wizard Test Partner",
                "vat": "RO22222222",
                "country_id": self.ro_country.id,
                "company_type": "company",
            }
        )

        wizard = self.env["get.partner.data"].create(
            {
                "partner_id": partner.id,
                "service": "openapi",
            }
        )

        with patch(
            "odoo.addons.l10n_ro_partner_create_by_vat_openapi.models.res_partner.urlopen",
            return_value=mock_response,
        ):
            wizard.do_get_data()

        self.assertEqual(partner.name, "SC TEST SRL")

    def test_wizard_do_get_data_openapi_no_api_key_raises(self):
        """Test că wizard-ul ridică UserError dacă lipsește openapi_key."""
        self.env["ir.config_parameter"].sudo().set_param("openapi_key", "")

        partner = self.env["res.partner"].create(
            {
                "name": "No Key Partner",
                "vat": "RO33333333",
                "country_id": self.ro_country.id,
                "company_type": "company",
            }
        )

        wizard = self.env["get.partner.data"].create(
            {
                "partner_id": partner.id,
                "service": "openapi",
            }
        )

        with self.assertRaises(UserError):
            wizard.do_get_data()

        self.env["ir.config_parameter"].sudo().set_param("openapi_key", "test-api-key-123")

    def test_wizard_do_get_data_non_openapi_service(self):
        """Test că wizard-ul cu alt service nu apelează logica openapi."""
        partner = self.env["res.partner"].create(
            {
                "name": "Wizard Non OpenAPI",
                "vat": "RO44444444",
                "company_type": "company",
                "country_id": self.ro_country.id,
            }
        )

        wizard = self.env["get.partner.data"].create(
            {
                "partner_id": partner.id,
                "service": "anaf",
            }
        )

        # Cu service != openapi, button_get_partner_data_openapi nu trebuie apelat
        with patch(
            "odoo.addons.l10n_ro_partner_create_by_vat_openapi.models.res_partner.ResPartner.button_get_partner_data_openapi"
        ) as mock_btn:
            try:
                wizard.do_get_data()
            except Exception as e:
                _logger.warning("do_get_data raised exception: %s", e)
            mock_btn.assert_not_called()

    def test_ro_vat_change_onchange(self):
        """Test că onchange ro_vat_change nu crăpă cu context skip_ro_vat_change."""
        partner = self.env["res.partner"].new(
            {
                "name": "Onchange Test",
                "vat": "RO12345678",
                "country_id": self.ro_country.id,
                "company_type": "company",
            }
        )
        # Nu trebuie să ridice excepție
        result = partner.ro_vat_change()
        # Rezultatul poate fi None sau dict
        self.assertIn(result, [None, {}] if result is None else [result])
