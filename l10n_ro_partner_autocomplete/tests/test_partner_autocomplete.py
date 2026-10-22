from unittest.mock import patch

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.l10n_ro_anaf_lookup.tests.test_anaf_lookup import CUI, REQUEST_PATH, anaf_result

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
