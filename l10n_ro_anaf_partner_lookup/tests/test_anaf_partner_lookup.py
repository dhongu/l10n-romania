import unittest
from unittest.mock import patch

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

REQUEST_PATH = (
    "odoo.addons.l10n_ro_anaf_partner_lookup.models.l10n_ro_anaf_partner_lookup.L10nRoAnafPartnerLookup._request"
)
CUI = "30834857"


def anaf_result(**general):
    """An answer of the ANAF v9 service, in its own shape"""
    result = {
        "date_generale": {
            "cui": int(CUI),
            "denumire": "FOREST AND BIOMASS ROMÂNIA S.A.",
            "nrRegCom": "J35/2622/2012",
            "telefon": "0356179038",
            "codPostal": "300045",
            "stare_inregistrare": "INREGISTRAT din data 02.10.2012",
        },
        "inregistrare_scop_Tva": {"scpTVA": True},
        "inregistrare_RTVAI": {"statusTvaIncasare": False},
        "stare_inactiv": {"statusInactivi": False, "dataRadiere": ""},
        "adresa_domiciliu_fiscal": {
            "ddenumire_Strada": "Str. Ciprian Porumbescu",
            "dnumar_Strada": "12",
            "ddenumire_Localitate": "Mun. Timişoara",
            "dcod_JudetAuto": "TM",
            "ddetalii_Adresa": "Zona Nr.3, Etaj 1",
            "dcod_Postal": "300045",
        },
        "adresa_sediu_social": {},
    }
    result["date_generale"].update(general)
    return result


@tagged("post_install", "-at_install")
class TestAnafPartnerLookup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Lookup = cls.env["l10n.ro.anaf.partner.lookup"]

    def _lookup(self, answer, vat=CUI):
        with patch(REQUEST_PATH, return_value=answer) as request:
            result = self.Lookup.lookup(vat)
        return result, request

    def test_normalize_cui(self):
        for typed in (CUI, "RO" + CUI, " ro 30 834 857 ", "RO-30834857"):
            self.assertEqual(self.Lookup.normalize_cui(typed), CUI)

    def test_control_digit(self):
        self.assertTrue(self.Lookup.is_valid_cui(CUI))
        self.assertFalse(self.Lookup.is_valid_cui("30834858"))
        self.assertFalse(self.Lookup.is_valid_cui("1"))
        self.assertFalse(self.Lookup.is_valid_cui("ABC"))
        # A personal numeric code (CNP) is not a CUI
        self.assertFalse(self.Lookup.is_valid_cui("1800101420010"))

    def test_invalid_cui_does_not_ask_anaf(self):
        result, request = self._lookup(anaf_result(), vat="30834858")
        self.assertEqual(result["state"], "invalid")
        request.assert_not_called()

    def test_company_found(self):
        result, request = self._lookup(anaf_result(), vat="RO " + CUI)
        request.assert_called_once_with(CUI, None)
        self.assertEqual(result["state"], "found")
        self.assertTrue(result["vat_payer"])
        self.assertFalse(result["inactive"])
        self.assertFalse(result["struck_off"])
        partner = result["partner"]
        self.assertEqual(partner["name"], "FOREST AND BIOMASS ROMÂNIA S.A.")
        self.assertEqual(partner["vat"], "RO" + CUI)
        self.assertEqual(partner["street"], "Str. Ciprian Porumbescu Nr. 12")
        self.assertEqual(partner["street2"], "Zona Nr.3, Etaj 1")
        # The prefix of the locality is dropped and the diacritics are the right ones
        self.assertEqual(partner["city"], "Timișoara")
        self.assertEqual(partner["state_id"], self.env.ref("base.RO_TM").id)
        self.assertEqual(partner["country_id"], self.env.ref("base.ro").id)
        self.assertEqual(partner["zip"], "300045")
        # The trade register number is not the Company ID, which is the CUI
        self.assertNotIn("additional_identifiers", partner)
        if "nrc" in self.env["res.partner"]._fields:
            self.assertEqual(partner["nrc"], "J35/2622/2012")
        # The values create a partner as they are: a company, with the CUI as its Company ID
        created = self.env["res.partner"].create(partner)
        self.assertTrue(created.is_company)
        self.assertEqual(created._get_additional_identifier("RO_EN"), CUI)

    def test_not_vat_payer_has_no_ro_prefix(self):
        answer = anaf_result()
        answer["inregistrare_scop_Tva"]["scpTVA"] = False
        result, _request = self._lookup(answer)
        self.assertFalse(result["vat_payer"])
        self.assertEqual(result["partner"]["vat"], CUI)
        # A company without the RO prefix all the same
        created = self.env["res.partner"].create(result["partner"])
        self.assertTrue(created.is_company)
        self.assertEqual(created._get_additional_identifier("RO_EN"), CUI)

    def test_bucharest_city_is_the_sector(self):
        answer = anaf_result()
        answer["adresa_domiciliu_fiscal"].update(
            ddenumire_Localitate="Sector 3 Mun. Bucureşti", dcod_JudetAuto="B", dcod_Postal="30167"
        )
        result, _request = self._lookup(answer)
        self.assertEqual(result["partner"]["city"], "Sector 3")
        # ANAF drops the leading 0 of the Bucharest postal codes
        self.assertEqual(result["partner"]["zip"], "030167")
        self.assertEqual(result["partner"]["state_id"], self.env.ref("base.RO_B").id)

    def test_locality_without_administrative_units(self):
        for anaf_locality, city in (
            ("Mun. Timişoara", "Timișoara"),
            ("Orş. Lipova", "Lipova"),
            ("Oraş Buziaş", "Buziaș"),
            # A village is the locality, not the commune or the town it belongs to
            ("Sat Filipeşti Com. Filipeşti", "Filipești"),
            ("Sat Româneşti Com. Tomeşti", "Românești"),
            ("Sat Bacova Orş. Buziaş", "Bacova"),
            ("Com. Recaş", "Recaș"),
            # A name only starting like a unit stays whole
            ("Sat Comăneşti Com. Comăneşti", "Comănești"),
            ("Sat Muntenii de Sus Com. Muntenii de Sus", "Muntenii de Sus"),
            ("Sat Valea Sat Mare Com. Bistra", "Valea Sat Mare"),
        ):
            answer = anaf_result()
            answer["adresa_domiciliu_fiscal"]["ddenumire_Localitate"] = anaf_locality
            result, _request = self._lookup(answer)
            self.assertEqual(result["partner"]["city"], city, anaf_locality)

    def test_bucharest_sector_from_postal_code(self):
        answer = anaf_result()
        answer["adresa_domiciliu_fiscal"].update(
            ddenumire_Localitate="Mun. Bucureşti", dcod_JudetAuto="B", dcod_Postal="60787"
        )
        result, _request = self._lookup(answer)
        self.assertEqual(result["partner"]["zip"], "060787")
        self.assertEqual(result["partner"]["city"], "Sector 6")

    def test_bucharest_without_sector_is_left_for_the_check(self):
        answer = anaf_result()
        answer["adresa_domiciliu_fiscal"].update(
            ddenumire_Localitate="Mun. Bucureşti", dcod_JudetAuto="B", dcod_Postal=""
        )
        result, _request = self._lookup(answer)
        self.assertEqual(result["partner"]["city"], "Mun. București")

    def test_address_in_capitals_and_without_street(self):
        answer = anaf_result()
        answer["adresa_domiciliu_fiscal"].update(
            ddenumire_Strada="", dnumar_Strada="", ddetalii_Adresa="SAT NOU 5", ddenumire_Localitate="COM. RECAS"
        )
        result, _request = self._lookup(answer)
        # The details take the place of the missing street
        self.assertEqual(result["partner"]["street"], "Sat Nou 5")
        self.assertEqual(result["partner"]["street2"], "")
        self.assertEqual(result["partner"]["city"], "Recas")

    def test_registered_office_first(self):
        answer = anaf_result()
        answer["adresa_domiciliu_fiscal"] = {}
        answer["adresa_sediu_social"] = {
            "sdenumire_Strada": "Str. Memorandumului",
            "snumar_Strada": "1",
            "sdenumire_Localitate": "Mun. Cluj-Napoca",
            "scod_JudetAuto": "CJ",
        }
        result, _request = self._lookup(answer)
        self.assertEqual(result["partner"]["street"], "Str. Memorandumului Nr. 1")
        self.assertEqual(result["partner"]["city"], "Cluj-Napoca")
        self.assertEqual(result["partner"]["state_id"], self.env.ref("base.RO_CJ").id)

    def test_address_from_one_block(self):
        # DANTE INTERNATIONAL: the registered office in Sector 6 with a postal code, the fiscal
        # domicile in Sector 2 without one. The invoice shows the registered office, whole
        answer = anaf_result(codPostal="")
        answer["adresa_domiciliu_fiscal"].update(
            ddenumire_Strada="Str. Gara Herăstrău",
            dnumar_Strada="6",
            ddenumire_Localitate="Sector 2 Mun. Bucureşti",
            dcod_JudetAuto="B",
            ddetalii_Adresa="",
            dcod_Postal="",
        )
        answer["adresa_sediu_social"] = {
            "sdenumire_Strada": "Şos. Virtuţii",
            "snumar_Strada": "148",
            "sdenumire_Localitate": "Sector 6 Mun. Bucureşti",
            "scod_JudetAuto": "B",
            "scod_Postal": "60787",
        }
        partner = self._lookup(answer)[0]["partner"]
        self.assertEqual(partner["street"], "Șos. Virtuții Nr. 148")
        self.assertEqual(partner["street2"], "")
        self.assertEqual(partner["city"], "Sector 6")
        self.assertEqual(partner["zip"], "060787")

    def test_no_postal_code_from_the_other_block(self):
        answer = anaf_result(codPostal="")
        answer["adresa_sediu_social"] = {
            "sdenumire_Strada": "Str. Strada Testului Inexistentă",
            "snumar_Strada": "6",
            "sdenumire_Localitate": "Sector 2 Mun. Bucureşti",
            "scod_JudetAuto": "B",
            "scod_Postal": "",
        }
        answer["adresa_domiciliu_fiscal"].update(
            ddenumire_Localitate="Sector 6 Mun. Bucureşti", dcod_JudetAuto="B", dcod_Postal="60787"
        )
        partner = self._lookup(answer)[0]["partner"]
        self.assertEqual(partner["city"], "Sector 2")
        self.assertEqual(partner["zip"], "")

    def test_struck_off_and_inactive(self):
        answer = anaf_result(stare_inregistrare="RADIERE din data 03.04.2026")
        answer["stare_inactiv"].update(statusInactivi=True, dataInactivare="2026-05-04")
        result, _request = self._lookup(answer)
        self.assertTrue(result["struck_off"])
        self.assertTrue(result["inactive"])
        self.assertEqual(result["inactive_date"], "2026-05-04")

    def test_vat_on_payment(self):
        result = self._lookup(anaf_result())[0]
        self.assertFalse(result["vat_on_payment"])
        answer = anaf_result()
        answer["inregistrare_RTVAI"].update(statusTvaIncasare=True, dataInceputTvaInc="2026-01-01")
        result = self._lookup(answer)[0]
        self.assertTrue(result["vat_on_payment"])
        # The partner flag only where l10n_ro_anaf_partner defines it
        if "l10n_ro_vat_on_payment" in self.env["res.partner"]._fields:
            self.assertTrue(result["partner"]["l10n_ro_vat_on_payment"])
        else:
            self.assertNotIn("l10n_ro_vat_on_payment", result["partner"])

    def test_no_rtvai_block_leaves_vat_on_payment(self):
        answer = anaf_result()
        del answer["inregistrare_RTVAI"]
        result = self._lookup(answer)[0]
        self.assertFalse(result["vat_on_payment"])
        self.assertNotIn("l10n_ro_vat_on_payment", result["partner"])

    def test_trade_register_and_timeout(self):
        with patch(REQUEST_PATH, return_value=anaf_result()) as request:
            result = self.Lookup.lookup(CUI, timeout=5)
        request.assert_called_once_with(CUI, 5)
        self.assertEqual(result["trade_register"], "J35/2622/2012")

    def test_not_found_and_unavailable(self):
        self.assertEqual(self._lookup({})[0]["state"], "not_found")
        self.assertEqual(self._lookup(None)[0]["state"], "unavailable")


@tagged("post_install", "-at_install")
class TestAnafPartnerLookupCity(TransactionCase):
    """city_id, where base_address_extended adds it (with the cities of l10n_ro_city)"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if "city_id" not in cls.env["res.partner"]._fields:
            raise unittest.SkipTest("res.partner has no city_id (base_address_extended)")
        cls.Lookup = cls.env["l10n.ro.anaf.partner.lookup"]
        cls.City = cls.env["res.city"]
        cls.ro = cls.env.ref("base.ro")
        cls.state_bc = cls.env.ref("base.RO_BC")

    def _city(self, name, zipcode, municipality="", state=None):
        vals = {"name": name, "zipcode": zipcode, "state_id": (state or self.state_bc).id, "country_id": self.ro.id}
        if "l10n_ro_municipality" in self.City._fields:
            vals["l10n_ro_municipality"] = municipality
        return self.City.create(vals)

    def _lookup(self, locality, zip_code, state_code="BC"):
        answer = anaf_result()
        answer["adresa_domiciliu_fiscal"].update(
            ddenumire_Localitate=locality, dcod_Postal=zip_code, dcod_JudetAuto=state_code
        )
        with patch(REQUEST_PATH, return_value=answer):
            return self.Lookup.lookup(CUI)["partner"]

    def test_city_by_name(self):
        city = self._city("Satul Testului", "607901", "Testeni")
        self.assertEqual(self._lookup("Sat Satul Testului Com. Testeni", "607901")["city_id"], city.id)

    def test_same_name_told_apart(self):
        self._city("Valea Testului", "607902", "Prima Comună")
        second = self._city("Valea Testului", "607903", "Testeni")
        # By the commune where the cities know it, else by the postal code
        self.assertEqual(self._lookup("Sat Valea Testului Com. Testeni", "607903")["city_id"], second.id)

    def test_same_name_not_told_apart(self):
        self._city("Lunca Testului", "607904", "Testeni")
        self._city("Lunca Testului", "607904", "Testeni")
        self.assertNotIn("city_id", self._lookup("Sat Lunca Testului Com. Testeni", "607904"))

    def test_city_by_postal_code(self):
        city = self._city("Testopolis", "607905")
        self.assertEqual(self._lookup("Sat Necunoscut Com. Nicăieri", "607905")["city_id"], city.id)

    def test_bucharest_sector(self):
        state_b = self.env.ref("base.RO_B")
        sector = self.City.search([("state_id", "=", state_b.id), ("name", "in", ["Sector3", "Sector 3"])], limit=1)
        sector = sector or self._city("Sector3", "", state=state_b)
        self.assertEqual(self._lookup("Sector 3 Mun. Bucureşti", "030167", "B")["city_id"], sector.id)

    def test_no_city_left_empty(self):
        self.assertNotIn("city_id", self._lookup("Sat Nicaieri Com. Nicaieri", "607999"))


@tagged("post_install", "-at_install")
class TestAnafPartnerLookupZip(TransactionCase):
    """The postal code of the street, where l10n_ro_zip has them, when ANAF gives none"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if "res.zip" not in cls.env:
            raise unittest.SkipTest("No res.zip (l10n_ro_zip)")
        cls.Lookup = cls.env["l10n.ro.anaf.partner.lookup"]
        cls.state_bc = cls.env.ref("base.RO_BC")
        Zip = cls.env["res.zip"]
        for name, street_type, street_name in [
            ("607911", "Strada", "Testului"),
            ("607912", "Bulevard", "Lung de Test nr. 1-19"),
            ("607913", "Bulevard", "Lung de Test nr. 2-22"),
            ("607914", "Bulevard", "Lung de Test nr. 21-T"),
            ("607915", "", ""),
        ]:
            Zip.create(
                {
                    "name": name,
                    "city": "Testopolis",
                    "state_id": cls.state_bc.id,
                    "country_id": cls.env.ref("base.ro").id,
                    "street_type": street_type,
                    "street_name": street_name,
                }
            )

    def _zip(self, street, number=""):
        answer = anaf_result()
        answer["adresa_domiciliu_fiscal"].update(
            ddenumire_Strada=street,
            dnumar_Strada=number,
            ddenumire_Localitate="Testopolis",
            dcod_JudetAuto="BC",
            dcod_Postal="",
        )
        with patch(REQUEST_PATH, return_value=answer):
            return self.Lookup.lookup(CUI)["partner"]["zip"]

    def test_zip_by_street(self):
        self.assertEqual(self._zip("Str. Testului", "3"), "607911")

    def test_zip_by_number_range(self):
        self.assertEqual(self._zip("Bd. Lung de Test", "7"), "607912")
        self.assertEqual(self._zip("Bulevardul Lung de Test", "8"), "607913")
        self.assertEqual(self._zip("Bd. Lung de Test", "45"), "607914")
        self.assertEqual(self._zip("Bd. Lung de Test", "40"), "")

    def test_zip_of_the_locality(self):
        self.assertEqual(self._zip(""), "607915")

    def test_unknown_street_has_no_zip(self):
        self.assertEqual(self._zip("Str. Nicăieri", "1"), "")
