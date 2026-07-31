# © 2026 Terrabit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import unittest

from odoo.tests.common import TransactionCase, tagged

try:
    from num2words import num2words
except ImportError:
    num2words = None


@tagged("post_install", "-at_install")
@unittest.skipIf(num2words is None, "num2words nu este instalat")
class TestResCurrencyAmountToText(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ron = cls.env.ref("base.RON")
        cls.ron.active = True
        cls.usd = cls.env.ref("base.USD")
        cls.usd.active = True

    def test_01_whole_amount(self):
        self.assertEqual(self.ron.amount_to_text(500.0), "cinci sute lei")

    def test_02_amount_with_bani(self):
        self.assertEqual(
            self.ron.amount_to_text(8382.25),
            "opt mii trei sute optzeci și doi lei și douăzeci și cinci bani",
        )

    def test_03_singular(self):
        self.assertEqual(self.ron.amount_to_text(1.0), "un leu")
        self.assertEqual(self.ron.amount_to_text(1.01), "un leu și un ban")

    def test_04_negative(self):
        self.assertEqual(self.ron.amount_to_text(-500.0), "minus cinci sute lei")

    def test_05_zero_lei(self):
        # 0.81 * 100 este 80.99999... în virgulă mobilă binară
        self.assertEqual(self.ron.amount_to_text(0.81), "zero lei și optzeci și unu bani")
        self.assertEqual(self.ron.amount_to_text(0.0), "zero lei")

    def test_06_other_currency_falls_back_to_core(self):
        self.assertIn("One Hundred", self.usd.amount_to_text(100.0))

    def test_07_wording_is_independent_of_lang(self):
        # o sumă în lei pe un document legal românesc se citește în română
        # chiar și pe o factură tipărită în engleză
        self.assertEqual(self.ron.with_context(lang="en_US").amount_to_text(500.0), "cinci sute lei")
