# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.l10n_ro_efactura_enhancement.models.account_edi_xml_cius_ro import PAYMENT_ID_MAX_LEN


@tagged("post_install", "-at_install")
class TestPaymentIdLength(TransactionCase):
    """Ticket #9369: ANAF respinge e-Factura dacă ``cbc:PaymentID`` sau
    ``cbc:InstructionID`` depășesc 200 de caractere. Pe facturile care consolidează
    multe comenzi, ``payment_reference`` conține referințele concatenate pentru
    reconciliere și depășește singur limita -- scurtăm în generator, ca facturile
    deja validate să poată fi transmise fără curățarea manuală a câmpului.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.builder = cls.env["account.edi.xml.ubl_bis3"]

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
