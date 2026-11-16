# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date

from odoo.tests import BaseCase, tagged

from ..tools.sni_dvi import SniDviError, TextLine, parse_lines
from .common import IMPORTER_VAT, load_lines


@tagged("post_install", "-at_install")
class TestSniDviParser(BaseCase):
    def test_regime_4000_two_items(self):
        """Two articles, no customs duty (EU–MD preference), VAT 11% on each article."""
        dvi = parse_lines(load_lines("dvi_4000_two_items"))
        self.assertEqual(dvi.mrn, "26ROXX0000000001R1")
        self.assertEqual(dvi.acceptance_date, date(2026, 9, 11))
        self.assertEqual(dvi.release_date, date(2026, 9, 11))
        self.assertEqual(dvi.importer_vat, IMPORTER_VAT)
        self.assertEqual((dvi.currency, dvi.exchange_rate, dvi.invoiced_amount), ("EUR", 5.2452, 9093.12))
        self.assertEqual(dvi.regimes, ["4000"])
        self.assertEqual(dvi.duty_total, 0.0)
        self.assertEqual(dvi.vat_total, 6141.0)
        self.assertAlmostEqual(dvi.vat_base, 48623.17 + 7202.12)
        self.assertEqual(dvi.vat_rates, [0.11])
        self.assertEqual(dvi.totals["B00"]["method"], "D")
        self.assertEqual([item.tax_amount("B00") for item in dvi.items], [5349.0, 792.0])
        self.assertEqual([item.taric for item in dvi.items], ["0808108090", "0809400500"])
        self.assertEqual(
            [(ref.number, ref.date) for ref in dvi.invoice_refs],
            [("EXP/2026/00001", "10.09.2026"), ("002/I", "10.09.2026")],
            "The invoice number keeps its own slashes; the date is split off",
        )

    def test_regime_4000_one_item(self):
        for name, mrn, vat in (
            ("dvi_4000_one_item", "26ROXX0000000002R2", 7443.0),
            ("dvi_4000_one_item_b", "26ROXX0000000003R3", 6258.0),
        ):
            dvi = parse_lines(load_lines(name))
            self.assertEqual(dvi.mrn, mrn)
            self.assertEqual(len(dvi.items), 1)
            self.assertEqual(dvi.vat_total, vat)
            self.assertEqual(dvi.vat_base, dvi.items[0].customs_value, "No duty: the VAT base is the customs value")

    def test_regime_4200_guarantee(self):
        """Regime 4200: the VAT is held as a guarantee (payment type 0, method S)."""
        dvi = parse_lines(load_lines("dvi_4200_two_items"))
        self.assertEqual(dvi.regimes, ["4200"])
        self.assertEqual(dvi.vat_total, 7473.0)
        self.assertEqual(dvi.totals["B00"], {"amount": 7473.0, "payment_type": "0", "method": "S"})
        self.assertEqual([item.tax_amount("B00") for item in dvi.items], [5034.0, 2439.0])

    def test_customs_duty_and_currency(self):
        """Customs duty A00 included in the VAT base B00; invoice in USD; broker invoice among the documents."""
        dvi = parse_lines(load_lines("dvi_4000_customs_duty"))
        self.assertEqual(dvi.duty_total, 144.0)
        self.assertEqual(dvi.vat_total, 1810.0)
        self.assertEqual(dvi.vat_base, 8617.13)
        self.assertEqual(dvi.vat_rates, [0.21])
        self.assertEqual(dvi.items[0].customs_value, 8473.13)
        self.assertEqual(dvi.items[0].taxes[0].rate, 0.017)
        self.assertEqual((dvi.currency, dvi.exchange_rate), ("USD", 4.519))
        self.assertEqual(
            [(ref.number, ref.date) for ref in dvi.invoice_refs],
            [("ROFF0001", "10.09.2026"), ("CI-20260101-ABC-001", "10,07,2026")],
        )

    def test_not_a_declaration(self):
        with self.assertRaises(SniDviError) as error:
            parse_lines([TextLine(1, 800, 30, 200, "FACTURA FISCALA")])
        self.assertEqual(error.exception.code, "not_a_declaration")

    def test_totals_must_match_items(self):
        """An article lost by the extraction must stop the import, not create a smaller DVI."""
        lines = load_lines("dvi_4000_two_items")
        lines = [line for line in lines if not (line.page == 3 and line.text.startswith("Tip taxă: B00"))]
        with self.assertRaises(SniDviError) as error:
            parse_lines(lines)
        self.assertEqual(error.exception.code, "totals")
        self.assertEqual(error.exception.params["code"], "B00")
