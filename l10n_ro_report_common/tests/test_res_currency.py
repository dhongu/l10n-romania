# © 2026 Terrabit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestResCurrencyAmountToText(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ron = cls.env.ref("base.RON")
        cls.ron.active = True
        cls.usd = cls.env.ref("base.USD")
        cls.usd.active = True

    def test_01_whole_amount(self):
        self.assertEqual(self.ron.amount_to_text(500.0), "cinci sute de lei")

    def test_02_amount_with_bani(self):
        self.assertEqual(
            self.ron.amount_to_text(8382.25),
            "opt mii trei sute optzeci și doi de lei și douăzeci și cinci de bani",
        )

    def test_03_singular(self):
        self.assertEqual(self.ron.amount_to_text(1.0), "un leu")
        self.assertEqual(self.ron.amount_to_text(1.01), "un leu și un ban")

    def test_04_negative(self):
        self.assertEqual(self.ron.amount_to_text(-500.0), "minus cinci sute de lei")

    def test_05_zero_lei(self):
        # 0.81 * 100 este 80.99999... în virgulă mobilă binară
        self.assertEqual(self.ron.amount_to_text(0.81), "zero lei și optzeci și unu de bani")
        self.assertEqual(self.ron.amount_to_text(0.0), "zero lei")

    def test_06_de_particle(self):
        # „de" se leagă doar când ultima grupă a numeralului e 20 sau peste,
        # ori numeralul se termină în sută/mie întreagă
        self.assertEqual(self.ron.amount_to_text(19.0), "nouăsprezece lei")
        self.assertEqual(self.ron.amount_to_text(20.0), "douăzeci de lei")
        self.assertEqual(self.ron.amount_to_text(101.0), "o sută unu lei")
        self.assertEqual(self.ron.amount_to_text(1000.0), "o mie de lei")
        self.assertEqual(self.ron.amount_to_text(1002.0), "o mie doi lei")

    def test_07_rounding_follows_the_currency(self):
        # suma tipărită se rotunjește ROUND_HALF_UP la 2,68 - litera nu are
        # voie să spună 67 de bani, cum ar ieși din rotunjirea Python
        self.assertEqual(self.ron.amount_to_text(2.675), "doi lei și șaizeci și opt de bani")

    def test_08_other_currency_falls_back_to_core(self):
        self.assertIn("One Hundred", self.usd.amount_to_text(100.0))

    def test_09_wording_is_independent_of_lang(self):
        # o sumă în lei pe un document legal românesc se citește în română
        # chiar și pe o factură tipărită în engleză
        self.assertEqual(self.ron.with_context(lang="en_US").amount_to_text(500.0), "cinci sute de lei")
