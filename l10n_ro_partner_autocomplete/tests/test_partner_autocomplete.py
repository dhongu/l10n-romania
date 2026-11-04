from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.l10n_ro_anaf_partner_lookup.tests.test_anaf_partner_lookup import CUI, REQUEST_PATH, anaf_result
from odoo.addons.l10n_ro_anaf_partner_lookup.tests.test_vies_lookup import VIES_PATH, VIES_VAT, vies_answer

IAP_PATH = (
    "odoo.addons.partner_autocomplete.models.iap_autocomplete_api.IapAutocompleteApi._request_partner_autocomplete"
)


@tagged("post_install", "-at_install")
class TestPartnerAutocomplete(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ro = cls.env.ref("base.ro")
        cls.be = cls.env.ref("base.be")
        cls.Partner = cls.env["res.partner"]

    def setUp(self):
        super().setUp()
        # No test goes to VIES: unless a test says otherwise, VIES does not answer
        self.vies = self.startPatcher(patch(VIES_PATH, return_value=None))

    def _iap(self):
        """IAP must not be asked about a Romanian CUI"""
        return patch(IAP_PATH, side_effect=AssertionError("IAP was called"))

    def test_vat_from_anaf_without_iap(self):
        with patch(REQUEST_PATH, return_value=anaf_result()), self._iap():
            suggestions = self.Partner.autocomplete_by_vat("RO" + CUI, self.be.id)
        self.assertEqual(len(suggestions), 1)
        suggestion = suggestions[0]
        self.assertEqual(suggestion["name"], "FOREST AND BIOMASS ROMÂNIA S.A.")
        self.assertEqual(suggestion["vat"], "RO" + CUI)
        self.assertEqual(suggestion["country_id"]["id"], self.ro.id)
        self.assertEqual(suggestion["state_id"]["id"], self.env.ref("base.RO_TM").id)
        self.assertEqual(suggestion["city"], "Timișoara")

    def test_cui_without_ro_searched_as_name(self):
        with patch(REQUEST_PATH, return_value=anaf_result()), self._iap():
            suggestions = self.Partner.autocomplete_by_name(CUI, self.ro.id)
        self.assertEqual(suggestions[0]["vat"], "RO" + CUI)

    def test_cui_without_ro_outside_romania_goes_to_iap(self):
        with patch(REQUEST_PATH) as request, patch(IAP_PATH, return_value=({"data": []}, False)):
            self.Partner.autocomplete_by_name(CUI, self.be.id)
        request.assert_not_called()

    def test_name_goes_to_iap(self):
        with patch(REQUEST_PATH) as request, patch(IAP_PATH, return_value=({"data": []}, False)) as iap:
            self.Partner.autocomplete_by_name("Forest and Biomass", self.ro.id)
        request.assert_not_called()
        iap.assert_called_once()

    def test_company_not_at_anaf(self):
        with patch(REQUEST_PATH, return_value={}), self._iap():
            self.assertEqual(self.Partner.autocomplete_by_vat("RO" + CUI, self.ro.id), [])

    def test_anaf_down_falls_back_to_iap(self):
        with patch(REQUEST_PATH, return_value=None), patch(IAP_PATH, return_value=({"data": []}, False)) as iap:
            self.Partner.autocomplete_by_vat("RO" + CUI, self.ro.id)
        iap.assert_called_once()

    def test_enrich_anaf_suggestion_without_iap(self):
        with patch(REQUEST_PATH, return_value=anaf_result()), self._iap():
            suggestion = self.Partner.autocomplete_by_vat("RO" + CUI, self.ro.id)[0]
            data = self.Partner.with_context(enriched_company_data=suggestion).enrich_by_duns(False)
        self.assertEqual(data["street"], "Str. Ciprian Porumbescu Nr. 12")
        self.assertFalse(data.get("error"))

    def test_message_after_save(self):
        partner = self.Partner.create({"name": "TEST ANAF"})
        partner.enrich_company_message_post({"entity_type": "l10n_ro_anaf"})
        self.assertIn("ANAF", partner.message_ids[0].body)

    # -- update an existing partner from ANAF ---------------------------

    def _partner(self, **vals):
        values = {
            "name": "Forest Vechi",
            "is_company": True,
            "vat": "RO" + CUI,
            "country_id": self.ro.id,
            "street": "Str. Veche 1",
            "city": "Arad",
            "phone": "0700000000",
        }
        values.update(vals)
        return self.Partner.with_context(l10n_ro_anaf_no_autofill=True).create(values)

    def test_refresh_updates_and_logs_the_changes(self):
        partner = self._partner()
        with patch(REQUEST_PATH, return_value=anaf_result()):
            partner.action_l10n_ro_anaf_refresh()
        self.assertEqual(partner.name, "FOREST AND BIOMASS ROMÂNIA S.A.")
        self.assertEqual(partner.street, "Str. Ciprian Porumbescu Nr. 12")
        self.assertEqual(partner.city, "Timișoara")
        self.assertEqual(partner.state_id, self.env.ref("base.RO_TM"))
        # A phone already on the partner stays
        self.assertEqual(partner.phone, "0700000000")
        body = partner.message_ids[0].body
        self.assertIn("Str. Veche 1", body)
        self.assertIn("Str. Ciprian Porumbescu Nr. 12", body)

    def test_refresh_fills_an_empty_phone(self):
        partner = self._partner(phone=False)
        with patch(REQUEST_PATH, return_value=anaf_result()):
            partner.action_l10n_ro_anaf_refresh()
        self.assertEqual(partner.phone, "0356179038")

    def _anaf_result_without_street(self):
        result = anaf_result(codPostal="")
        result["adresa_domiciliu_fiscal"].update(
            ddenumire_Strada="", dnumar_Strada="", ddetalii_Adresa="", dcod_Postal=""
        )
        return result

    def test_refresh_keeps_an_address_anaf_does_not_hold(self):
        # The same locality, written without diacritics and without the county
        partner = self._partner(city="Timisoara", street2="Bl. A1, Sc. 2", zip="300001")
        with patch(REQUEST_PATH, return_value=self._anaf_result_without_street()):
            partner.action_l10n_ro_anaf_refresh()
        self.assertEqual(partner.street, "Str. Veche 1")
        self.assertEqual(partner.street2, "Bl. A1, Sc. 2")
        self.assertEqual(partner.zip, "300001")
        # What ANAF does hold is still updated
        self.assertEqual(partner.city, "Timișoara")
        self.assertEqual(partner.state_id.code, "TM")
        self.assertNotIn("Str. Veche 1", partner.message_ids[0].body)

    def test_refresh_clears_the_details_of_another_street(self):
        # ANAF has a new street without details: the old block and postal code went with the old one
        partner = self._partner(city="Timișoara", street2="Bl. A1, Sc. 2", zip="300001")
        result = anaf_result(codPostal="")
        result["adresa_domiciliu_fiscal"].update(ddetalii_Adresa="", dcod_Postal="")
        with patch(REQUEST_PATH, return_value=result):
            partner.action_l10n_ro_anaf_refresh()
        self.assertEqual(partner.street, "Str. Ciprian Porumbescu Nr. 12")
        self.assertFalse(partner.street2)
        self.assertNotEqual(partner.zip, "300001")

    def test_refresh_clears_the_street_of_another_locality(self):
        # The old street does not exist in the city ANAF gives: kept, it would make a false address
        partner = self._partner(street2="Bl. A1, Sc. 2", zip="310130")
        with patch(REQUEST_PATH, return_value=self._anaf_result_without_street()):
            partner.action_l10n_ro_anaf_refresh()
        self.assertFalse(partner.street)
        self.assertFalse(partner.street2)
        self.assertFalse(partner.zip)
        self.assertEqual(partner.city, "Timișoara")

    def test_refresh_without_change(self):
        partner = self._partner()
        with patch(REQUEST_PATH, return_value=anaf_result()):
            partner.action_l10n_ro_anaf_refresh()
            partner.action_l10n_ro_anaf_refresh()
        self.assertIn("no change", partner.message_ids[0].body)

    def test_refresh_warns_about_struck_off(self):
        partner = self._partner()
        with patch(REQUEST_PATH, return_value=anaf_result(stare_inregistrare="RADIERE din data 03.04.2026")):
            partner.action_l10n_ro_anaf_refresh()
        self.assertIn("struck off", partner.message_ids[0].body)

    def test_refresh_errors(self):
        partner = self._partner()
        with patch(REQUEST_PATH, return_value={}), self.assertRaisesRegex(UserError, "no company registered"):
            partner.action_l10n_ro_anaf_refresh()
        with patch(REQUEST_PATH, return_value=None), self.assertRaisesRegex(UserError, "did not answer"):
            partner.action_l10n_ro_anaf_refresh()
        # base_vat refuses a wrong control digit on write; a partner imported before can still have one
        self.env.cr.execute("UPDATE res_partner SET vat = 'RO30834858' WHERE id = %s", [partner.id])
        partner.invalidate_recordset(["vat"])
        with self.assertRaisesRegex(UserError, "not a valid CUI"):
            partner.action_l10n_ro_anaf_refresh()

    # -- a partner created with its CUI as the name ---------------------

    def test_create_with_cui_as_name(self):
        for name in (CUI, "RO" + CUI, " ro 30834857 "):
            with patch(REQUEST_PATH, return_value=anaf_result()):
                partner = self.Partner.create({"name": name})
            self.assertEqual(partner.name, "FOREST AND BIOMASS ROMÂNIA S.A.")
            self.assertEqual(partner.vat, "RO" + CUI)
            self.assertTrue(partner.is_company)
            partner.vat = False

    def test_name_create_from_a_many2one(self):
        with patch(REQUEST_PATH, return_value=anaf_result()):
            partner_id, _name = self.Partner.name_create(CUI)
        self.assertEqual(self.Partner.browse(partner_id).city, "Timișoara")

    def test_create_explicit_values_win(self):
        with patch(REQUEST_PATH, return_value=anaf_result()):
            partner = self.Partner.create({"name": CUI, "phone": "0700000000"})
        self.assertEqual(partner.phone, "0700000000")

    def test_create_left_alone(self):
        with patch(REQUEST_PATH) as request:
            self.Partner.create({"name": "Forest and Biomass"})
            self.Partner.create({"name": "30834858"})
            self.Partner.create({"name": CUI, "country_id": self.be.id})
            self.Partner.with_context(l10n_ro_anaf_no_autofill=True).create({"name": CUI})
        request.assert_not_called()

    def test_create_when_anaf_is_down(self):
        with patch(REQUEST_PATH, return_value=None):
            partner = self.Partner.create({"name": CUI})
        self.assertEqual(partner.name, CUI)

    def test_create_with_another_tax_id(self):
        if self.env["ir.module.module"]._get("l10n_ro_partner_create_by_vat_button").state == "installed":
            self.skipTest("l10n_ro_partner_create_by_vat_button replaces the Tax ID with the name")
        with patch(REQUEST_PATH) as request:
            self.Partner.create({"name": CUI, "vat": "RO1234567897"})
        request.assert_not_called()

    def test_create_with_the_same_cui_as_tax_id(self):
        # The Tax ID derived from the name, as l10n_ro_partner_create_by_vat_button sets it
        with patch(REQUEST_PATH, return_value=anaf_result()):
            partner = self.Partner.create({"name": CUI, "vat": "RO" + CUI})
        self.assertEqual(partner.name, "FOREST AND BIOMASS ROMÂNIA S.A.")

    # -- city_id, where base_address_extended adds it ---------------------

    def _test_city(self):
        if "city_id" not in self.Partner._fields:
            self.skipTest("res.partner has no city_id (base_address_extended)")
        return self.env["res.city"].create(
            {
                "name": "Testoara",
                "zipcode": "300001",
                "state_id": self.env.ref("base.RO_TM").id,
                "country_id": self.ro.id,
            }
        )

    def test_suggestion_carries_the_city(self):
        city = self._test_city()
        answer = anaf_result()
        answer["adresa_domiciliu_fiscal"]["ddenumire_Localitate"] = "Mun. Testoara"
        with patch(REQUEST_PATH, return_value=answer), self._iap():
            suggestion = self.Partner.autocomplete_by_vat("RO" + CUI, self.ro.id)[0]
        self.assertEqual(suggestion["city_id"], {"id": city.id, "display_name": city.display_name})

    def test_choosing_the_city_keeps_the_postal_code(self):
        city = self._test_city()
        spec = {"zip": {}, "city": {}, "city_id": {}, "state_id": {}, "country_id": {}}
        values = {"country_id": self.ro.id, "zip": "300045", "city_id": city.id}
        result = self.Partner.onchange(values, ["city_id"], spec)
        self.assertNotIn("zip", result["value"])
        # Without a postal code, the city's is taken as usual
        result = self.Partner.onchange(dict(values, zip=False), ["city_id"], spec)
        self.assertEqual(result["value"].get("zip"), "300001")

    def test_city_and_postal_code_together_keep_the_city(self):
        self._test_city()
        state_b = self.env.ref("base.RO_B")
        City = self.env["res.city"]
        sectors = {
            n: City.search([("state_id", "=", state_b.id), ("name", "in", [f"Sector{n}", f"Sector {n}"])], limit=1)
            or City.create({"name": f"Sector{n}", "state_id": state_b.id, "country_id": self.ro.id})
            for n in (2, 6)
        }
        spec = {"zip": {}, "city": {}, "city_id": {}, "state_id": {}, "country_id": {}}
        # The address is in Sector 2, the postal code ANAF gives is one of Sector 6
        values = {"country_id": self.ro.id, "state_id": state_b.id, "zip": "060787", "city_id": sectors[2].id}
        result = self.Partner.onchange(values, ["zip", "city_id", "state_id"], spec)
        self.assertNotIn("city_id", result["value"])
        self.assertNotIn("zip", result["value"])

    # -- the Romanian VAT fields ------------------------------------------

    def test_create_sets_the_vat_payer(self):
        with patch(REQUEST_PATH, return_value=anaf_result()):
            partner = self.Partner.create({"name": CUI})
        self.assertTrue(partner.l10n_ro_vat_subjected)
        self.assertEqual(partner.l10n_ro_vat_number, CUI)

    def test_refresh_clears_the_vat_payer(self):
        partner = self._partner(l10n_ro_vat_subjected=True)
        answer = anaf_result()
        answer["inregistrare_scop_Tva"]["scpTVA"] = False
        with patch(REQUEST_PATH, return_value=answer):
            partner.action_l10n_ro_anaf_refresh()
        self.assertFalse(partner.l10n_ro_vat_subjected)
        self.assertEqual(partner.l10n_ro_vat_number, CUI)
        # A check box is listed as Yes / No, not as True / False
        self.assertIn("Yes → No", partner.message_ids[0].body)

    def test_vat_number_without_prefix(self):
        partner = self._partner(vat="RO " + CUI)
        self.assertEqual(partner.l10n_ro_vat_number, CUI)
        partner.vat = False
        self.assertFalse(partner.l10n_ro_vat_number)

    # -- VIES -------------------------------------------------------------

    def test_eu_vat_from_vies_without_iap(self):
        self.vies.return_value = vies_answer()
        with self._iap():
            suggestions = self.Partner.autocomplete_by_vat(VIES_VAT, self.ro.id)
        self.assertEqual(len(suggestions), 1)
        suggestion = suggestions[0]
        self.assertEqual(suggestion["entity_type"], "l10n_ro_vies")
        self.assertEqual(suggestion["name"], "MOTOROLA SOLUTIONS ITALIA SRL")
        self.assertEqual(suggestion["country_id"]["id"], self.env.ref("base.it").id)
        self.assertEqual(suggestion["city"], "Milano Mi")
        with self._iap():
            data = self.Partner.with_context(enriched_company_data=suggestion).enrich_by_duns(False)
        self.assertEqual(data["zip"], "20122")

    def test_eu_vat_without_details_goes_to_iap(self):
        self.vies.return_value = vies_answer(name="---", address="---")
        with patch(IAP_PATH, return_value=({"data": []}, False)) as iap:
            self.Partner.autocomplete_by_vat("DE811569869", self.ro.id)
        iap.assert_called_once()

    def test_eu_vat_vies_down_goes_to_iap(self):
        with patch(IAP_PATH, return_value=({"data": []}, False)) as iap:
            self.Partner.autocomplete_by_vat(VIES_VAT, self.ro.id)
        iap.assert_called_once()

    def test_name_like_a_vat_number_not_asked_at_vies(self):
        with patch(IAP_PATH, return_value=({"data": []}, False)):
            self.Partner.autocomplete_by_name("Delta 2000", self.ro.id)
        self.vies.assert_not_called()

    def test_romanian_cui_not_asked_at_vies_for_suggestion(self):
        with patch(REQUEST_PATH, return_value=anaf_result()), self._iap():
            self.Partner.autocomplete_by_vat("RO" + CUI, self.ro.id)
        self.vies.assert_not_called()

    def test_message_after_save_from_anaf_has_vies_status(self):
        partner = self._partner(l10n_ro_vat_subjected=True)
        self.vies.return_value = vies_answer(name="FOREST AND BIOMASS", address="---")
        partner.enrich_company_message_post({"entity_type": "l10n_ro_anaf"})
        body = partner.message_ids[0].body
        self.assertIn("ANAF", body)
        self.assertIn("valid for intra-community operations", body)

    def test_non_payer_not_asked_at_vies(self):
        partner = self._partner(vat=CUI, l10n_ro_vat_subjected=False)
        partner.enrich_company_message_post({"entity_type": "l10n_ro_anaf"})
        self.vies.assert_not_called()

    def test_refresh_from_anaf_says_not_in_vies(self):
        partner = self._partner()
        self.vies.return_value = vies_answer("INVALID", "---", "---")
        with patch(REQUEST_PATH, return_value=anaf_result()):
            partner.action_l10n_ro_anaf_refresh()
        self.assertIn("not registered for intra-community operations", partner.message_ids[0].body)

    def _eu_partner(self, **vals):
        values = {
            "name": "Motorola Vechi",
            "is_company": True,
            "vat": VIES_VAT,
            "country_id": self.env.ref("base.it").id,
        }
        values.update(vals)
        return self.Partner.create(values)

    def test_message_after_save_from_vies(self):
        partner = self._eu_partner()
        partner.enrich_company_message_post({"entity_type": "l10n_ro_vies"})
        self.assertIn("VIES", partner.message_ids[0].body)
        if "vies_valid" in partner._fields:
            self.assertTrue(partner.vies_valid)
        self.vies.assert_not_called()

    def test_refresh_from_vies(self):
        partner = self._eu_partner(street="Via Vecchia 1")
        self.vies.return_value = vies_answer()
        partner.action_l10n_ro_vies_refresh()
        self.assertEqual(partner.name, "MOTOROLA SOLUTIONS ITALIA SRL")
        self.assertEqual(partner.street, "Largo Francesco Richini 6")
        self.assertEqual(partner.zip, "20122")
        body = partner.message_ids[0].body
        self.assertIn("Via Vecchia 1", body)
        self.assertIn("valid for intra-community operations", body)
        if "vies_valid" in partner._fields:
            self.assertTrue(partner.vies_valid)

    def test_refresh_from_vies_keeps_what_vies_does_not_know(self):
        partner = self._eu_partner(
            name="Siemens", vat="DE811569869", country_id=self.env.ref("base.de").id, street="X 1"
        )
        self.vies.return_value = vies_answer(name="---", address="---")
        partner.action_l10n_ro_vies_refresh()
        self.assertEqual(partner.name, "Siemens")
        self.assertEqual(partner.street, "X 1")
        self.assertIn("no change", partner.message_ids[0].body)

    def test_refresh_from_vies_not_found(self):
        partner = self._eu_partner()
        if "vies_valid" in partner._fields:
            partner.vies_valid = True
        self.vies.return_value = vies_answer("INVALID", "---", "---")
        partner.action_l10n_ro_vies_refresh()
        self.assertIn("not registered for intra-community operations", partner.message_ids[0].body)
        if "vies_valid" in partner._fields:
            self.assertFalse(partner.vies_valid)

    def test_refresh_from_vies_errors(self):
        partner = self._eu_partner()
        with self.assertRaisesRegex(UserError, "VIES did not answer"):
            partner.action_l10n_ro_vies_refresh()

    def test_vat_payer_once_on_the_form(self):
        arch = self.Partner.get_views([(False, "form")])["views"]["form"]["arch"]
        arch = arch.decode() if isinstance(arch, bytes) else arch
        self.assertEqual(arch.count('name="l10n_ro_vat_subjected"'), 1)
        self.assertNotIn("l10n_ro_vat_subjected_info", arch)

    def test_refresh_from_vies_clears_old_street_details_and_state(self):
        it = self.env.ref("base.it")
        state = self.env["res.country.state"].search([("country_id", "=", it.id)], limit=1)
        partner = self._eu_partner(street="Via Vecchia 1", street2="Scala B", city="Roma", state_id=state.id)
        self.vies.return_value = vies_answer()
        partner.action_l10n_ro_vies_refresh()
        self.assertEqual(partner.street, "Largo Francesco Richini 6")
        self.assertFalse(partner.street2)
        self.assertEqual(partner.city, "Milano Mi")
        self.assertFalse(partner.state_id)
