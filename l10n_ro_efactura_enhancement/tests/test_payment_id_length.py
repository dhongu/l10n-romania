# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.l10n_ro_efactura_enhancement.models.account_edi_xml_cius_ro import PAYMENT_ID_MAX_LEN


@tagged("post_install", "-at_install")
class TestPaymentIdLength(TransactionCase):
    """Tichetele #9369 și #9441: ANAF respinge e-Factura (BR-RO-L140) dacă
    ``cbc:PaymentID`` sau ``cbc:InstructionID`` depășesc 140 de caractere -- limita
    CIUS-RO pentru Avizul de plată (BT-83). Pe facturile care consolidează multe
    comenzi, ``payment_reference`` conține referințele concatenate pentru
    reconciliere și depășește singur limita -- scurtăm în generator, ca facturile
    deja validate să poată fi transmise fără curățarea manuală a câmpului.

    Limitarea stă pe ``account.edi.xml.ubl_ro``, nu pe ``ubl_bis3``: e o cerință
    CIUS-RO, nu una a BIS3, deci nu trebuie să afecteze facturile Peppol non-RO.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.builder = cls.env["account.edi.xml.ubl_ro"]

    def test_long_payment_id_truncated_on_order_separator(self):
        """Tăierea se face la ultimul " - " care încape, fără să rupă un cod."""
        orders = [f"PTCRO3050{index:02d}" for index in range(30)]
        reference = "6246422002 - " + " - ".join(orders)
        document_node = {
            "cac:PaymentMeans": {
                "cbc:PaymentID": {"_text": reference},
                "cbc:InstructionID": {"_text": reference},
            }
        }
        self.builder._l10n_ro_truncate_payment_identifiers(document_node)
        means = document_node["cac:PaymentMeans"]
        for tag in ("cbc:PaymentID", "cbc:InstructionID"):
            value = means[tag]["_text"]
            self.assertLessEqual(len(value), PAYMENT_ID_MAX_LEN)
            self.assertTrue(value.startswith("6246422002 - PTCRO305000"))
            # nu s-a tăiat în mijlocul unui cod de comandă
            self.assertTrue(all(segment in orders or segment == "6246422002" for segment in value.split(" - ")))

    def test_short_payment_id_untouched(self):
        """Sub limită nu se modifică nimic."""
        document_node = {"cac:PaymentMeans": [{"cbc:PaymentID": {"_text": "6246422002 - PTCRO304410"}}]}
        self.builder._l10n_ro_truncate_payment_identifiers(document_node)
        self.assertEqual(
            document_node["cac:PaymentMeans"][0]["cbc:PaymentID"]["_text"],
            "6246422002 - PTCRO304410",
        )

    def test_no_separator_falls_back_to_hard_cut(self):
        """Fără separator utilizabil, tăiem brut la limită."""
        value = "X" * 260
        document_node = {"cac:PaymentMeans": {"cbc:PaymentID": {"_text": value}}}
        self.builder._l10n_ro_truncate_payment_identifiers(document_node)
        self.assertEqual(
            document_node["cac:PaymentMeans"]["cbc:PaymentID"]["_text"],
            "X" * PAYMENT_ID_MAX_LEN,
        )

    def test_missing_nodes_are_tolerated(self):
        """Documentele fără cac:PaymentMeans sau fără identificatori nu crapă."""
        self.builder._l10n_ro_truncate_payment_identifiers({})
        self.builder._l10n_ro_truncate_payment_identifiers({"cac:PaymentMeans": None})
        self.builder._l10n_ro_truncate_payment_identifiers(
            {"cac:PaymentMeans": [{"cbc:PaymentMeansCode": {"_text": 30}}]}
        )

    def test_bis3_non_ro_has_no_limit(self):
        """Limita e CIUS-RO, nu BIS3: generatorul Peppol generic nu o moștenește."""
        self.assertFalse(hasattr(self.env["account.edi.xml.ubl_bis3"], "_l10n_ro_truncate_payment_identifiers"))

    def test_limit_matches_anaf_rule(self):
        """Limita e cea din BR-RO-L140, nu cea presupusă de 200 de caractere.

        Tichet #9441: valoarea 200 fusese preluată din corespondența tichetului
        #9369, nu din răspunsul ANAF, așa că facturile lungi rămâneau respinse și
        după trunchiere. Testul ancorează limita în regula reală de schematron.
        """
        self.assertEqual(PAYMENT_ID_MAX_LEN, 140)

    def test_real_refused_reference_passes_limit(self):
        """Referința reală de pe PTCDRO20689 (43 de comenzi) intră sub limită."""
        orders = [
            "S189895",
            "S189875",
            "S190083",
            "S189903",
            "S189922",
            "S189896",
            "S189884",
            "S189879",
            "S189901",
            "S190060",
            "S189892",
            "S189454",
            "S189883",
            "S189880",
            "S189898",
            "S189887",
            "S190056",
            "S189950",
            "S189894",
            "S189823",
            "S189886",
            "S189897",
            "S189756",
            "S189877",
            "S189869",
            "S189921",
            "S189871",
            "S189872",
            "S189890",
            "S189891",
            "S189893",
            "S189966",
            "S189873",
            "S189888",
            "S189889",
            "S189881",
            "S189878",
            "S189876",
            "S190037",
            "S190080",
            "S189885",
            "S189919",
        ]
        reference = " - ".join(["PTCDRO20689"] + orders)
        self.assertGreater(len(reference), PAYMENT_ID_MAX_LEN)
        document_node = {"cac:PaymentMeans": {"cbc:PaymentID": {"_text": reference}}}
        self.builder._l10n_ro_truncate_payment_identifiers(document_node)
        value = document_node["cac:PaymentMeans"]["cbc:PaymentID"]["_text"]
        self.assertLessEqual(len(value), PAYMENT_ID_MAX_LEN)
        # numărul facturii rămâne primul, ca reconcilierea să aibă de ce să se agațe
        self.assertTrue(value.startswith("PTCDRO20689 - S189895"))
        self.assertTrue(all(segment in orders or segment == "PTCDRO20689" for segment in value.split(" - ")))
