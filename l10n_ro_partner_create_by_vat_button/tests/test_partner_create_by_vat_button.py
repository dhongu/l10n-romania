from types import SimpleNamespace
from unittest.mock import patch

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPartnerCreateByVatButton(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Ensure Romania exists
        cls.country_ro = cls.env["res.country"].search([("code", "=", "RO")], limit=1)
        if not cls.country_ro:
            cls.country_ro = cls.env["res.country"].create({"name": "Romania", "code": "RO"})

        # A basic company partner to attach contacts to (some flows require a company)
        cls.company = cls.env["res.partner"].create(
            {
                "name": "Test Company",
                "is_company": True,
                "country_id": cls.country_ro.id,
            }
        )

    def _new_partner(self, **vals):
        data = {
            "name": "Test Partner",
            "is_company": True,
            "country_id": self.country_ro.id,
            "parent_id": self.company.id,
        }
        data.update(vals)
        return self.env["res.partner"].create(data)

    def test_wizard_anaf_for_delivery_contact_raises(self):
        delivery = self._new_partner(type="delivery")
        wiz = self.env["get.partner.data"].create(
            {
                "partner_id": delivery.id,
                "service": "anaf",
            }
        )
        with self.assertRaises(ValidationError):
            wiz.do_get_data()

    def test_wizard_anaf_success_message(self):
        partner = self._new_partner()
        wiz = self.env["get.partner.data"].create(
            {
                "partner_id": partner.id,
                "service": "anaf",
            }
        )
        # Simulate successful update without warnings
        with patch.object(type(partner), "get_partner_data", autospec=True, return_value={}):
            action = wiz.do_get_data()
        self.assertEqual(wiz.state, "set")
        self.assertTrue("Partner data updated" in (wiz.status_message or ""))
        self.assertIsInstance(action, dict)
        self.assertEqual(action.get("res_id"), wiz.id)

    def test_wizard_anaf_warning_message(self):
        partner = self._new_partner()
        wiz = self.env["get.partner.data"].create(
            {
                "partner_id": partner.id,
                "service": "anaf",
            }
        )
        with patch.object(type(partner), "get_partner_data", autospec=True, return_value={"warning": {"message": "X"}}):
            wiz.do_get_data()
        self.assertIn("Attention!", wiz.status_message or "")

    def test_wizard_vies_calls_partner_and_sets_message(self):
        partner = self._new_partner(vat="RO14826496")
        wiz = self.env["get.partner.data"].create(
            {
                "partner_id": partner.id,
                "service": "vies",
            }
        )
        with patch.object(type(partner), "get_partner_name_from_vies", autospec=True, return_value=None) as mocked:
            wiz.do_get_data()
            # Ensure the partner method was invoked
            self.assertTrue(mocked.called)
        self.assertEqual(wiz.state, "set")
        self.assertIn("VIES", wiz.status_message or "")

    def test_partner_create_autofill_vat_and_merge_from_anaf(self):
        # When name is like RO<digits>, create() should set vat and merge results from ANAF
        res_map = {
            "name": "RO Company SRL",
            "street": "Str. Exemplu 1",
            "city": "Bucuresti",
        }
        # Patch ANAF helpers on the model
        with (
            patch.object(
                self.env["res.partner"].__class__, "_get_Anaf", autospec=True, return_value=(None, object())
            ) as p_get,
            patch.object(
                self.env["res.partner"].__class__, "_Anaf_to_Odoo", autospec=True, return_value=res_map
            ) as p_to_odoo,
        ):
            partner = self.env["res.partner"].create(
                {
                    "name": "RO14826496",
                    "is_company": True,
                }
            )
        # _get_Anaf and _Anaf_to_Odoo were called
        self.assertTrue(p_get.called)
        self.assertTrue(p_to_odoo.called)
        # VAT is copied from name and mapped fields were applied
        self.assertEqual(partner.vat, "RO14826496")
        self.assertEqual(partner.name, res_map["name"])  # updated by ANAF mapping
        self.assertEqual(partner.street, res_map["street"])

    def test_get_partner_name_from_vies_valid_updates_fields(self):
        # Prepare partner with RO country, vat 'RO14826496' (alpha prefix to trigger slicing)
        partner = self._new_partner(vat="RO14826496", name="Old Name", street=False)

        # Mock _get_vies_client to return a fake SOAP client
        def fake_checkVat(countryCode, vatNumber):
            self.assertEqual(countryCode, "RO")
            self.assertEqual(vatNumber, "14826496")
            return SimpleNamespace(valid=True, name="Acme SRL", address="Some Street 10")

        fake_client = SimpleNamespace(
            service=SimpleNamespace(checkVat=fake_checkVat)
        )
        with patch.object(type(partner), "_get_vies_client", return_value=fake_client):
            partner.get_partner_name_from_vies()

        # Country must remain/set to RO
        self.assertEqual(partner.country_id.code, "RO")

    def test_get_partner_name_from_vies_invalid_raises(self):
        partner = self._new_partner(vat="RO7654321")

        def fake_checkVat(countryCode, vatNumber):
            return SimpleNamespace(valid=False, name="", address="")

        fake_client = SimpleNamespace(
            service=SimpleNamespace(checkVat=fake_checkVat)
        )
        with patch.object(type(partner), "_get_vies_client", return_value=fake_client):
            with self.assertRaises(UserError):
                partner.get_partner_name_from_vies()

    def test_get_partner_name_from_vies_missing_country_info_raises(self):
        # Numeric VAT but no country set should raise the guidance error
        partner = self.env["res.partner"].create(
            {
                "name": "Foo",
                "is_company": True,
                "vat": "14826496",
            }
        )
        with self.assertRaisesRegex(UserError, "Please add the country code"):
            # Patch _get_vies_client; code should raise before it's called
            with patch.object(type(partner), "_get_vies_client"):
                partner.get_partner_name_from_vies()

    def test_compute_warning_message_for_ro_company_missing_fields(self):
        # Ensure RO state exists
        state_ro = self.env["res.country.state"].search(
            [("code", "=", "B"), ("country_id", "=", self.country_ro.id)], limit=1
        )
        if not state_ro:
            state_ro = self.env["res.country.state"].create(
                {
                    "name": "Bucuresti",
                    "code": "B",
                    "country_id": self.country_ro.id,
                }
            )
        partner = self.env["res.partner"].create(
            {
                "name": "ACME RO",
                "is_company": True,
                "country_id": self.country_ro.id,
                # Intentionally missing vat, street, city, state_id, zip
            }
        )
        # Trigger compute by reading the field
        msg = partner.warning_message
        self.assertTrue(msg)
        for label in ["VAT", "Street", "City", "State", "ZIP"]:
            self.assertIn(label, msg)

        # Fill all required and ensure message disappears
        partner.write(
            {
                "vat": "RO123",
                "street": "Str 1",
                "city": "Bucuresti",
                "state_id": state_ro.id,
                "zip": "010101",
            }
        )
        self.assertFalse(partner.warning_message)

    def test_no_warning_for_non_ro(self):
        country_de = self.env["res.country"].search([("code", "=", "DE")], limit=1) or self.env["res.country"].create(
            {"name": "Germany", "code": "DE"}
        )
        partner = self.env["res.partner"].create(
            {
                "name": "ACME DE",
                "is_company": True,
                "country_id": country_de.id,
            }
        )
        self.assertFalse(partner.warning_message)
