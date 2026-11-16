from unittest.mock import patch

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

VIES_PATH = (
    "odoo.addons.l10n_ro_anaf_partner_lookup.models.l10n_ro_anaf_partner_lookup.L10nRoAnafPartnerLookup._vies_request"
)
VIES_VAT = "IT00743110157"


def vies_answer(
    status="VALID", name="MOTOROLA SOLUTIONS ITALIA SRL", address="LARGO FRANCESCO RICHINI 6 \n20122 MILANO MI\n"
):
    """An answer of the VIES REST service, in its own shape"""
    return {
        "isValid": status == "VALID",
        "userError": status,
        "name": name,
        "address": address,
        "vatNumber": VIES_VAT[2:],
    }


@tagged("post_install", "-at_install")
class TestViesLookup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Lookup = cls.env["l10n.ro.anaf.partner.lookup"]

    def _vies(self, answer, vat=VIES_VAT):
        with patch(VIES_PATH, return_value=answer) as request:
            result = self.Lookup.vies_lookup(vat)
        return result, request

    def test_split_eu_vat(self):
        self.assertEqual(self.Lookup.split_eu_vat("it 007-43110157"), ("IT", "00743110157"))
        self.assertEqual(self.Lookup.split_eu_vat("EL094014201"), ("EL", "094014201"))
        self.assertEqual(self.Lookup.split_eu_vat("US123456789"), ("", ""))
        self.assertEqual(self.Lookup.split_eu_vat("00743110157"), ("", ""))

    def test_found_with_address(self):
        result, request = self._vies(vies_answer())
        request.assert_called_once_with("IT", "00743110157", None)
        self.assertEqual(result["state"], "found")
        self.assertTrue(result["has_details"])
        partner = result["partner"]
        self.assertEqual(partner["name"], "MOTOROLA SOLUTIONS ITALIA SRL")
        self.assertEqual(partner["vat"], VIES_VAT)
        self.assertEqual(partner["country_id"], self.env.ref("base.it").id)
        self.assertEqual(partner["street"], "Largo Francesco Richini 6")
        self.assertEqual(partner["zip"], "20122")
        self.assertEqual(partner["city"], "Milano Mi")

    def test_address_on_one_line(self):
        partner = self._vies(vies_answer(address="KONYVES KALMAN KÖRÚT 36 1097 BUDAPEST"), "HU10773381")[0]["partner"]
        self.assertEqual(partner["country_id"], self.env.ref("base.hu").id)
        self.assertEqual(partner["street"], "Konyves Kalman Körút 36")
        self.assertEqual(partner["zip"], "1097")
        self.assertEqual(partner["city"], "Budapest")

    def test_greece_prefix_is_el(self):
        result = self._vies(vies_answer(address="ΑΙΟΛΟΥ 86        10559 - ΑΘΗΝΑ"), "EL094014201")[0]
        self.assertEqual(result["partner"]["vat"], "EL094014201")
        self.assertEqual(result["partner"]["country_id"], self.env.ref("base.gr").id)
        self.assertEqual(result["partner"]["zip"], "10559")
        self.assertEqual(result["partner"]["city"], "Αθηνα")

    def test_address_without_postal_code_stays_in_street(self):
        partner = self._vies(vies_answer(address="UNIT 5, DUBLIN INDUSTRIAL ESTATE"))[0]["partner"]
        self.assertEqual(partner["street"], "Unit 5, Dublin Industrial Estate")
        self.assertNotIn("zip", partner)

    def test_member_state_without_details(self):
        result = self._vies(vies_answer(name="---", address="---"), "DE811569869")[0]
        self.assertEqual(result["state"], "found")
        self.assertFalse(result["has_details"])
        self.assertEqual(result["partner"]["vat"], "DE811569869")
        self.assertNotIn("name", result["partner"])
        self.assertNotIn("street", result["partner"])

    def test_not_found(self):
        self.assertEqual(self._vies(vies_answer("INVALID", "---", "---"))[0]["state"], "not_found")

    def test_not_valid_although_processed(self):
        # `userError` is the state of the request, `isValid` the answer: VALID with isValid false
        # is a number that is not registered
        answer = dict(vies_answer("VALID", "---", "---"), isValid=False)
        self.assertEqual(self._vies(answer)[0]["state"], "not_found")

    def test_member_state_busy_is_unavailable(self):
        self.assertEqual(self._vies(vies_answer("MS_MAX_CONCURRENT_REQ", "---", "---"))[0]["state"], "unavailable")

    def test_vies_down(self):
        self.assertEqual(self._vies(None)[0]["state"], "unavailable")

    def test_wrong_check_digit_not_asked(self):
        result, request = self._vies(vies_answer(), "IT00743110158")
        self.assertEqual(result["state"], "invalid")
        request.assert_not_called()
        result, request = self._vies(vies_answer(), "US123456789")
        self.assertEqual(result["state"], "invalid")
        request.assert_not_called()
