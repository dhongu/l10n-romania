# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.l10n_ro_efactura_enhancement.models.account_edi_xml_cius_ro import (
    DELIVERY_LIMITS,
    DOCUMENT_LIMITS,
    LINE_LIMITS,
    NOTE_MAX_LEN,
    PARTY_LIMITS,
    PAYMENT_ID_MAX_LEN,
    PAYMENT_MEANS_LIMITS,
    MaxLen,
)

# Familiile de reguli BR-RO-L* din schematronul CIUS-RO v1.0.9.
KNOWN_LIMITS = {20, 50, 100, 140, 150, 200, 300, 1000}


@tagged("post_install", "-at_install")
class TestCiusRoLengthLimits(TransactionCase):
    """Tichetele #9369 și #9441: ANAF respinge factura integral dacă un singur câmp
    depășește limita lui de lungime (regulile BR-RO-L020 .. BR-RO-L1000).

    Cazuri reale care au produs respingeri în producție:
    - `payment_reference` cu 43 de comenzi concatenate, ~450 caractere (BT-83, 140)
    - `street2` folosit de clienții din magazin drept câmp de observații (BT-51/76, 100)
    - denumire de institut de 118 caractere ajunsă în contact (BT-56, 100)
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.builder = cls.env["account.edi.xml.ubl_ro"]

    # -- harta de limite ---------------------------------------------------

    def test_payment_id_limit_matches_anaf_rule(self):
        """Limita e cea din BR-RO-L140, nu cea presupusă de 200 de caractere.

        Tichet #9441: valoarea 200 fusese preluată din corespondența tichetului
        #9369, nu din răspunsul ANAF, așa că facturile lungi rămâneau respinse și
        după trunchiere.
        """
        self.assertEqual(PAYMENT_ID_MAX_LEN, 140)

    def test_every_limit_belongs_to_a_known_rule_family(self):
        """Nicio limită inventată: fiecare cifră e o familie BR-RO-L* reală."""
        for name, limits in (
            ("DOCUMENT_LIMITS", DOCUMENT_LIMITS),
            ("PARTY_LIMITS", PARTY_LIMITS),
            ("DELIVERY_LIMITS", DELIVERY_LIMITS),
            ("PAYMENT_MEANS_LIMITS", PAYMENT_MEANS_LIMITS),
            ("LINE_LIMITS", LINE_LIMITS),
        ):
            for path, spec in limits.items():
                with self.subTest(map=name, path=path):
                    limit = spec.limit if isinstance(spec, MaxLen) else spec
                    self.assertIn(limit, KNOWN_LIMITS)

    # -- BT-83, referința de plată ----------------------------------------

    def test_real_refused_reference_passes_limit(self):
        """Referința reală de pe PTCDRO20689 (43 de comenzi) intră sub limită."""
        orders = [f"S{189800 + index}" for index in range(43)]
        reference = " - ".join(["PTCDRO20689"] + orders)
        self.assertGreater(len(reference), PAYMENT_ID_MAX_LEN)
        node = {"cac:PaymentMeans": {"cbc:PaymentID": {"_text": reference}}}
        self.builder._l10n_ro_apply_length_limits(node)
        value = node["cac:PaymentMeans"]["cbc:PaymentID"]["_text"]
        self.assertLessEqual(len(value), PAYMENT_ID_MAX_LEN)
        self.assertTrue(value.startswith("PTCDRO20689 - S189800"))
        # nu s-a tăiat în mijlocul unui cod de comandă
        self.assertTrue(all(part in orders or part == "PTCDRO20689" for part in value.split(" - ")))

    def test_short_payment_id_untouched(self):
        node = {"cac:PaymentMeans": [{"cbc:PaymentID": {"_text": "6246422002 - PTCRO304410"}}]}
        self.builder._l10n_ro_apply_length_limits(node)
        self.assertEqual(node["cac:PaymentMeans"][0]["cbc:PaymentID"]["_text"], "6246422002 - PTCRO304410")

    def test_no_separator_falls_back_to_hard_cut(self):
        node = {"cac:PaymentMeans": {"cbc:PaymentID": {"_text": "X" * 260}}}
        self.builder._l10n_ro_apply_length_limits(node)
        self.assertEqual(node["cac:PaymentMeans"]["cbc:PaymentID"]["_text"], "X" * PAYMENT_ID_MAX_LEN)

    # -- BT-51 / BT-76 / BT-56, adrese și contacte ------------------------

    def test_observations_in_street2_are_truncated(self):
        """street2 folosit ca observații nu mai blochează transmiterea (PTCSRO198653)."""
        street2 = (
            "Sa fiu sunat inainte va rog și vreau să verific comanda. "
            "Daca se poate sa mi trimiteți comanda lunimultumeac"
        )
        self.assertGreater(len(street2), 100)
        node = {
            "cac:AccountingCustomerParty": {
                "cac:Party": {
                    "cac:PostalAddress": {
                        "cbc:StreetName": {"_text": "str. George Enescu 21/7"},
                        "cbc:AdditionalStreetName": {"_text": street2},
                    }
                }
            }
        }
        self.builder._l10n_ro_apply_length_limits(node)
        address = node["cac:AccountingCustomerParty"]["cac:Party"]["cac:PostalAddress"]
        self.assertLessEqual(len(address["cbc:AdditionalStreetName"]["_text"]), 100)
        # strada (BT-50, limita 150) rămâne neatinsă
        self.assertEqual(address["cbc:StreetName"]["_text"], "str. George Enescu 21/7")

    def test_long_institution_name_truncated_in_contact(self):
        """Denumirea lungă de instituție nu mai blochează transmiterea (PTCSRO198808)."""
        name = (
            "INSTITUTUL NAŢIONAL DE CERCETARE-DEZVOLTARE ÎN CONSTRUCŢII, URBANISM "
            'ŞI DEZVOLTARE TERITORIALĂ DURABILĂ "URBAN-INCERC"'
        )
        self.assertGreater(len(name), 100)
        node = {
            "cac:AccountingCustomerParty": {
                "cac:Party": {
                    "cac:Contact": {"cbc:Name": {"_text": name}},
                    "cac:PartyLegalEntity": {"cbc:RegistrationName": {"_text": name}},
                }
            }
        }
        self.builder._l10n_ro_apply_length_limits(node)
        party = node["cac:AccountingCustomerParty"]["cac:Party"]
        self.assertLessEqual(len(party["cac:Contact"]["cbc:Name"]["_text"]), 100)
        # denumirea legală (BT-44) permite 200, deci rămâne întreagă
        self.assertEqual(party["cac:PartyLegalEntity"]["cbc:RegistrationName"]["_text"], name)

    def test_delivery_address_is_covered(self):
        """BT-76 e pe altă cale decât BT-51 și trebuie prins separat."""
        node = {
            "cac:Delivery": {
                "cac:DeliveryLocation": {"cac:Address": {"cbc:AdditionalStreetName": {"_text": "x" * 150}}}
            }
        }
        self.builder._l10n_ro_apply_length_limits(node)
        value = node["cac:Delivery"]["cac:DeliveryLocation"]["cac:Address"]["cbc:AdditionalStreetName"]["_text"]
        self.assertEqual(len(value), 100)

    # -- măsurarea normalizată --------------------------------------------

    def test_length_measured_on_normalized_text(self):
        """Schematronul măsoară string-length(normalize-space(...)).

        Un text cu spații multiple poate depăși limita brut și să fie totuși valid;
        nu-l tăiem, ca să nu pierdem informație fără motiv.
        """
        value = "A" + " " * 80 + "B"
        self.assertGreater(len(value), 50)
        node = {"cac:AccountingCustomerParty": {"cac:Party": {"cac:PostalAddress": {"cbc:CityName": {"_text": value}}}}}
        self.builder._l10n_ro_apply_length_limits(node)
        self.assertEqual(
            node["cac:AccountingCustomerParty"]["cac:Party"]["cac:PostalAddress"]["cbc:CityName"]["_text"], value
        )

    # -- BT-22 / BT-127, notele se sparg, nu se taie ----------------------

    def test_long_note_is_split_not_truncated(self):
        """UBL permite repetarea lui cbc:Note, deci păstrăm tot textul."""
        text = "x" * 700
        node = {"cbc:Note": {"_text": text}}
        self.builder._l10n_ro_apply_length_limits(node)
        chunks = node["cbc:Note"]
        self.assertIsInstance(chunks, list)
        self.assertEqual(len(chunks), 3)
        for chunk in chunks:
            self.assertLessEqual(len(chunk["_text"]), NOTE_MAX_LEN)
        self.assertEqual("".join(chunk["_text"] for chunk in chunks), text)

    def test_short_note_left_alone(self):
        node = {"cbc:Note": {"_text": "Nota scurta"}}
        self.builder._l10n_ro_apply_length_limits(node)
        self.assertEqual(node["cbc:Note"], {"_text": "Nota scurta"})

    def test_line_note_is_split(self):
        node = {"cac:InvoiceLine": [{"cbc:Note": {"_text": "y" * 400}}]}
        self.builder._l10n_ro_apply_length_limits(node)
        self.assertEqual(len(node["cac:InvoiceLine"][0]["cbc:Note"]), 2)

    # -- robustețe ---------------------------------------------------------

    def test_missing_and_odd_nodes_are_tolerated(self):
        """Documentele incomplete sau cu forme neașteptate nu crapă."""
        self.builder._l10n_ro_apply_length_limits({})
        self.builder._l10n_ro_apply_length_limits({"cac:PaymentMeans": None})
        self.builder._l10n_ro_apply_length_limits({"cac:AccountingCustomerParty": None})
        self.builder._l10n_ro_apply_length_limits({"cac:PaymentMeans": [{"cbc:PaymentMeansCode": {"_text": 30}}]})
        self.builder._l10n_ro_apply_length_limits({"cbc:Note": None})
        self.builder._l10n_ro_apply_length_limits({"cac:InvoiceLine": [{"cac:Item": {"cbc:Name": {"_text": None}}}]})

    def test_attribute_leaf_is_truncated(self):
        """Frunza poate fi un atribut XML, nu un nod text (BT-82)."""
        node = {"cac:PaymentMeans": {"cbc:PaymentMeansCode": {"_text": 30, "name": "z" * 150}}}
        self.builder._l10n_ro_apply_length_limits(node)
        self.assertEqual(len(node["cac:PaymentMeans"]["cbc:PaymentMeansCode"]["name"]), 100)

    def test_bis3_non_ro_has_no_limits(self):
        """Limitele sunt CIUS-RO: generatorul Peppol generic nu le moștenește."""
        self.assertFalse(hasattr(self.env["account.edi.xml.ubl_bis3"], "_l10n_ro_apply_length_limits"))
