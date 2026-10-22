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
        request.assert_called_once_with(CUI)
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
        self.assertNotIn("company_registry", partner)
        if "nrc" in self.env["res.partner"]._fields:
            self.assertEqual(partner["nrc"], "J35/2622/2012")
        # The values create a partner as they are
        created = self.env["res.partner"].create(partner)
        if self.env["ir.module.module"]._get("l10n_ro").state == "installed":
            self.assertEqual(created.company_registry, CUI)

    def test_not_vat_payer_has_no_ro_prefix(self):
        answer = anaf_result()
        answer["inregistrare_scop_Tva"]["scpTVA"] = False
        result, _request = self._lookup(answer)
        self.assertFalse(result["vat_payer"])
        self.assertEqual(result["partner"]["vat"], CUI)

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

    def test_registered_office_when_no_fiscal_domicile(self):
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

    def test_struck_off_and_inactive(self):
        answer = anaf_result(stare_inregistrare="RADIERE din data 03.04.2026")
        answer["stare_inactiv"]["statusInactivi"] = True
        result, _request = self._lookup(answer)
        self.assertTrue(result["struck_off"])
        self.assertTrue(result["inactive"])

    def test_not_found_and_unavailable(self):
        self.assertEqual(self._lookup({})[0]["state"], "not_found")
        self.assertEqual(self._lookup(None)[0]["state"], "unavailable")
