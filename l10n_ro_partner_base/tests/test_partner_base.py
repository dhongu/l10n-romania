# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from unittest.mock import patch

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

CUI = "18547290"

ANAF_RESULT = {
    "date_generale": {
        "cui": 30834857,
        "denumire": "FOREST AND BIOMASS ROMÂNIA S.A.",
        "telefon": "0356179038",
        "codPostal": "307225",
        "nrRegCom": "J2012002622359",
        "cod_CAEN": "119",
    },
    "inregistrare_scop_Tva": {"scpTVA": True},
    "stare_inactiv": {"statusInactivi": False},
    "adresa_domiciliu_fiscal": {
        "ddenumire_Strada": "STR. TEST",
        "dnumar_Strada": "5",
        "ddenumire_Localitate": "Mun. Timişoara",
        "ddenumire_Judet": "TIMIŞ",
        "dcod_JudetAuto": "TM",
        "ddetalii_Adresa": "FERMA 5-6",
        "dcod_Postal": "307225",
    },
}


@tagged("post_install", "-at_install")
class TestRoVat(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ro = cls.env.ref("base.ro")

    def _partner(self, vat, subjected):
        return self.env["res.partner"].create(
            {
                "name": f"Test RO {vat}",
                "is_company": True,
                "country_id": self.ro.id,
                "vat": vat,
                "l10n_ro_vat_subjected": subjected,
            }
        )

    def test_subjected_gets_prefix(self):
        partner = self._partner(CUI, True)
        self.assertEqual(partner.vat, "RO" + CUI)
        self.assertEqual(partner.l10n_ro_vat_number, CUI)

    def test_not_subjected_loses_prefix(self):
        partner = self._partner("RO" + CUI, False)
        self.assertEqual(partner.vat, CUI)
        self.assertEqual(partner.l10n_ro_vat_number, CUI)

    def test_switch_subjected(self):
        partner = self._partner(CUI, False)
        partner.l10n_ro_vat_subjected = True
        partner.vat = partner._get_ro_vat()
        self.assertEqual(partner.vat, "RO" + CUI)

    def test_non_ro_partner_untouched(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Test FR",
                "country_id": self.env.ref("base.fr").id,
                "vat": "FR23334175221",
            }
        )
        self.assertEqual(partner.vat, "FR23334175221")

    def test_company_caen(self):
        company = self.env.company
        company.l10n_ro_caen_code = "6201"
        company.invalidate_recordset()
        self.assertEqual(company.l10n_ro_caen_code, "6201")


@tagged("post_install", "-at_install")
class TestRoAnaf(TransactionCase):
    def _mock(self, result=None, error=""):
        return patch.object(
            type(self.env["res.partner"]),
            "_l10n_ro_anaf_request",
            return_value=(error, result if result is not None else ANAF_RESULT),
        )

    def test_mapping(self):
        values = self.env["res.partner"]._l10n_ro_anaf_to_values(ANAF_RESULT)
        self.assertEqual(values["name"], "FOREST AND BIOMASS ROMÂNIA S.A.")
        self.assertTrue(values["l10n_ro_vat_subjected"])
        self.assertEqual(values["vat"], "RO30834857")
        self.assertEqual(values["nrc"], "J2012002622359")
        self.assertEqual(values["street"], "Str. Test Nr. 5")
        self.assertEqual(values["street2"], "Ferma 5-6")
        self.assertEqual(values["zip"], "307225")
        self.assertEqual(values["phone"], "0356179038")
        self.assertEqual(values["state_id"], self.env.ref("base.RO_TM").id)
        self.assertEqual(values["company_type"], "company")

    def test_not_vat_payer_has_no_prefix(self):
        result = dict(ANAF_RESULT, inregistrare_scop_Tva={"scpTVA": False})
        values = self.env["res.partner"]._l10n_ro_anaf_to_values(result)
        self.assertEqual(values["vat"], "30834857")
        self.assertFalse(values["l10n_ro_vat_subjected"])

    def test_empty_answer(self):
        self.assertEqual(self.env["res.partner"]._l10n_ro_anaf_to_values({}), {})

    def test_get_data_button(self):
        partner = self.env["res.partner"].create(
            {"name": "x", "is_company": True, "country_id": self.env.ref("base.ro").id}
        )
        partner.vat = "30834857"
        with self._mock():
            res = partner.l10n_ro_get_anaf_data()
        self.assertFalse(res)
        self.assertEqual(partner.name, "FOREST AND BIOMASS ROMÂNIA S.A.")
        self.assertEqual(partner.vat, "RO30834857")
        self.assertEqual(partner.city, "Timișoara")

    def test_get_data_error_is_a_warning(self):
        partner = self.env["res.partner"].create({"name": "x", "country_id": self.env.ref("base.ro").id})
        partner.vat = "30834857"
        with self._mock(result={}, error="down"):
            res = partner.l10n_ro_get_anaf_data()
        self.assertEqual(res["warning"]["message"], "down")
        self.assertEqual(partner.name, "x")

    def test_create_from_cui_name(self):
        with self._mock():
            partner = self.env["res.partner"].create({"name": "30834857"})
        self.assertEqual(partner.name, "FOREST AND BIOMASS ROMÂNIA S.A.")
        self.assertEqual(partner.vat, "RO30834857")

    def test_name_that_is_not_a_cui_is_left_alone(self):
        with self._mock() as request:
            partner = self.env["res.partner"].create({"name": "Some Company"})
        request.assert_not_called()
        self.assertEqual(partner.name, "Some Company")

    def test_wizard(self):
        partner = self.env["res.partner"].create(
            {
                "name": "x",
                "is_company": True,
                "country_id": self.env.ref("base.ro").id,
                "vat": "30834857",
            }
        )
        wizard = (
            self.env["l10n.ro.get.partner.data"]
            .with_context(active_model="res.partner", active_ids=partner.ids)
            .create({})
        )
        self.assertEqual(wizard.partner_id, partner)
        with self._mock():
            wizard.do_get_data()
        self.assertEqual(wizard.state, "set")
        self.assertEqual(partner.name, "FOREST AND BIOMASS ROMÂNIA S.A.")
