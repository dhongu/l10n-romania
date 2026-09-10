# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.l10n_ro_efactura_enhancement.models.account_edi_xml_cius_ro import (
    ADDRESS_LINE_MAX_LEN,
    CONTACT_NAME_MAX_LEN,
)


@tagged("post_install", "-at_install")
class TestAddressLineLength(TransactionCase):
    """Tichet #9441: ANAF respinge e-Factura (BR-RO-L100) dacă Adresa - Linia 2
    (BT-51 cumpărător / BT-76 livrare) sau Punctul de contact al Cumpărătorului
    (BT-56) depășesc 100 de caractere.

    Cazuri reale din producție: ``street2`` folosit de clienții din magazin drept
    câmp de observații (PTCSRO198653) și denumiri de instituții mai lungi de 100
    de caractere (PTCSRO198808).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.builder = cls.env["account.edi.xml.ubl_ro"]

    def test_long_street2_truncated(self):
        """street2 folosit ca observații nu mai blochează transmiterea."""
        partner = self.env["res.partner"].create(
            {
                "name": "NICOLAE-GABRIEL CHIRIGUT",
                "street": "str. George Enescu 21/7 Baia Mare MM",
                "street2": (
                    "Sa fiu sunat inainte va rog și vreau să verific comanda. "
                    "Daca se poate sa mi trimiteți comanda lunimultumeac"
                ),
                "city": "Baia Mare",
            }
        )
        self.assertGreater(len(partner.street2), ADDRESS_LINE_MAX_LEN)
        node = self.builder._ubl_get_partner_address_node({}, partner)
        value = node["cbc:AdditionalStreetName"]["_text"]
        self.assertLessEqual(len(value), ADDRESS_LINE_MAX_LEN)
        self.assertTrue(partner.street2.startswith(value))
        # strada rămâne neatinsă: pentru BT-50 nu avem o limită confirmată de ANAF
        self.assertEqual(node["cbc:StreetName"]["_text"], partner.street)

    def test_short_street2_untouched(self):
        """Sub limită nu se modifică nimic."""
        partner = self.env["res.partner"].create({"name": "Client scurt", "street2": "Bloc 2, Ap. 5"})
        node = self.builder._ubl_get_partner_address_node({}, partner)
        self.assertEqual(node["cbc:AdditionalStreetName"]["_text"], "Bloc 2, Ap. 5")

    def test_long_contact_name_truncated(self):
        """Denumirea lungă de instituție nu mai blochează transmiterea (BT-56)."""
        partner = self.env["res.partner"].create(
            {
                "name": (
                    "INSTITUTUL NAŢIONAL DE CERCETARE-DEZVOLTARE ÎN CONSTRUCŢII, URBANISM "
                    'ŞI DEZVOLTARE TERITORIALĂ DURABILĂ "URBAN-INCERC"'
                ),
            }
        )
        self.assertGreater(len(partner.name), CONTACT_NAME_MAX_LEN)
        vals = {"party_vals": {"partner": partner}, "party_node": {}}
        self.builder._ubl_add_party_contact_node(vals)
        value = vals["party_node"]["cac:Contact"]["cbc:Name"]["_text"]
        self.assertLessEqual(len(value), CONTACT_NAME_MAX_LEN)
        self.assertTrue(partner.name.startswith(value))

    def test_missing_nodes_are_tolerated(self):
        """Nodurile absente sau fără text nu crapă."""
        self.builder._l10n_ro_truncate_node_text(None, "cbc:Name", CONTACT_NAME_MAX_LEN)
        self.builder._l10n_ro_truncate_node_text({}, "cbc:Name", CONTACT_NAME_MAX_LEN)
        self.builder._l10n_ro_truncate_node_text({"cbc:Name": None}, "cbc:Name", CONTACT_NAME_MAX_LEN)
        self.builder._l10n_ro_truncate_node_text({"cbc:Name": {"_text": None}}, "cbc:Name", CONTACT_NAME_MAX_LEN)
