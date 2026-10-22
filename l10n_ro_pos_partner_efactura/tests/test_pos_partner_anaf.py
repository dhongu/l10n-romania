from unittest.mock import patch

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from odoo.addons.l10n_ro_anaf_lookup.tests.test_anaf_lookup import CUI, REQUEST_PATH, anaf_result
from odoo.addons.point_of_sale.tests.common import CommonPosTest


@tagged("post_install", "-at_install")
class TestPosPartnerAnaf(CommonPosTest):
    @classmethod
    @CommonPosTest.setup_country("ro")
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.l10n_ro_accounting = True
        cls.config = cls.pos_config_usd
        cls.Partner = cls.env["res.partner"]
        cls.country_ro = cls.env.ref("base.ro")
        cls.state_cj = cls.env.ref("base.RO_CJ")
        # A partner already in the database under this CUI would be returned instead of the test one
        cls.Partner.search([("vat", "in", [CUI, "RO" + CUI])]).write({"vat": False})

    def _create_from_vat(self, vat_number=CUI, answer=None):
        with patch(REQUEST_PATH, return_value=anaf_result() if answer is None else answer):
            return self.Partner.l10n_ro_pos_partner_from_cui(self.config.id, vat_number)

    def _complete_vals(self, **vals):
        data = {
            "name": "TEST POS Partner",
            "is_company": True,
            "vat": "RO" + CUI,
            "street": "Str. Memorandumului 1",
            "city": "Cluj-Napoca",
            "state_id": self.state_cj.id,
            "country_id": self.country_ro.id,
        }
        data.update(vals)
        return data

    def test_partner_fetched_from_anaf_must_be_confirmed(self):
        result = self._create_from_vat()
        partner = self.Partner.browse(result["res.partner"][0]["id"])
        self.assertTrue(partner.l10n_ro_pos_anaf_to_confirm)
        self.assertTrue(result["res.partner"][0]["l10n_ro_pos_anaf_to_confirm"])

    def test_complete_partner_on_file_is_not_confirmed_again(self):
        partner = self.Partner.create(self._complete_vals())
        with patch(REQUEST_PATH, side_effect=AssertionError("ANAF was called")):
            result = self.Partner.l10n_ro_pos_partner_from_cui(self.config.id, CUI)
        self.assertEqual(result["res.partner"][0]["id"], partner.id)
        self.assertFalse(partner.l10n_ro_pos_anaf_to_confirm)
        self.assertFalse(result["res.partner"][0]["l10n_ro_pos_anaf_to_confirm"])

    def test_incomplete_partner_on_file_must_be_confirmed(self):
        partner = self.Partner.create(self._complete_vals(street=False))
        with patch(REQUEST_PATH, side_effect=AssertionError("ANAF was called")):
            result = self.Partner.l10n_ro_pos_partner_from_cui(self.config.id, CUI)
        self.assertTrue(partner.l10n_ro_pos_anaf_to_confirm)
        self.assertTrue(result["res.partner"][0]["l10n_ro_pos_anaf_to_confirm"])

    def test_confirm_clears_the_flag(self):
        partner = self.Partner.create(self._complete_vals(l10n_ro_pos_anaf_to_confirm=True))
        partner.l10n_ro_pos_anaf_confirm()
        self.assertFalse(partner.l10n_ro_pos_anaf_to_confirm)

    def test_confirm_refuses_incomplete_data(self):
        partner = self.Partner.create(self._complete_vals(city=False, l10n_ro_pos_anaf_to_confirm=True))
        with self.assertRaisesRegex(ValidationError, "City"):
            partner.l10n_ro_pos_anaf_confirm()
        self.assertTrue(partner.l10n_ro_pos_anaf_to_confirm)

    def test_warnings_list_missing_data_and_street_without_number(self):
        partner = self.Partner.create(self._complete_vals(street="Str. Memorandumului", city=False))
        self.assertIn("City", partner.l10n_ro_pos_anaf_warnings)
        self.assertIn("no number", partner.l10n_ro_pos_anaf_warnings)
        partner.write({"street": "Str. Memorandumului 1", "city": "Cluj-Napoca"})
        self.assertFalse(partner.l10n_ro_pos_anaf_warnings)

    def test_city_not_in_county(self):
        if "res.city" not in self.env:
            self.skipTest("res.city is not installed")
        City = self.env["res.city"]
        City.create({"name": "Cluj-Napoca", "state_id": self.state_cj.id, "country_id": self.country_ro.id})
        partner = self.Partner.create(self._complete_vals(city="Voluntari"))
        self.assertIn("Voluntari", partner.l10n_ro_pos_anaf_warnings)
        # Diacritics and case written differently are the same city
        partner.city = "CLUJ NAPOCA"
        self.assertFalse(partner.l10n_ro_pos_anaf_warnings)

    def test_fetched_partner_data(self):
        result = self._create_from_vat("RO 30834857")
        partner = self.Partner.browse(result["res.partner"][0]["id"])
        self.assertEqual(partner.name, "FOREST AND BIOMASS ROMÂNIA S.A.")
        self.assertEqual(partner.vat, "RO" + CUI)
        self.assertEqual(partner.street, "Str. Ciprian Porumbescu Nr. 12")
        self.assertEqual(partner.state_id, self.env.ref("base.RO_TM"))
        self.assertTrue(partner.is_company)

    def test_invalid_cui(self):
        with self.assertRaisesRegex(UserError, "not a valid CUI"):
            self._create_from_vat("30834858")

    def test_company_not_at_anaf(self):
        with self.assertRaisesRegex(UserError, "no company registered"):
            self._create_from_vat(answer={})

    def test_anaf_down(self):
        with patch(REQUEST_PATH, return_value=None), self.assertRaisesRegex(UserError, "did not answer"):
            self.Partner.l10n_ro_pos_partner_from_cui(self.config.id, CUI)

    def test_struck_off_company_refused(self):
        with self.assertRaisesRegex(UserError, "struck off"):
            self._create_from_vat(answer=anaf_result(stare_inregistrare="RADIERE din data 03.04.2026"))
        self.assertFalse(self.Partner.search([("vat", "=", "RO" + CUI)]))

    def test_flag_is_loaded_in_pos(self):
        self.assertIn("l10n_ro_pos_anaf_to_confirm", self.Partner._load_pos_data_fields(self.config))
