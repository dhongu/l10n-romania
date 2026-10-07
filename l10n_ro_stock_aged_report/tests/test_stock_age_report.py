# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockAgeReport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.env.company.id)], limit=1)
        cls.location = cls.warehouse.lot_stock_id

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "is_storable": True,
                "standard_price": 100.0,
            }
        )

        # Creăm un quant manual pentru a testa logica de bază
        cls.quant = cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.location.id,
                "quantity": 10.0,
            }
        )

    def test_01_quant_dates_update(self):
        """Verifică dacă l10n_ro_last_in_date este setat la creare."""
        self.assertTrue(
            self.quant.l10n_ro_last_in_date,
            "l10n_ro_last_in_date ar trebui să fie setat la crearea quant-ului cu cantitate pozitivă.",
        )

        old_in_date = self.quant.l10n_ro_last_in_date
        # Simulăm o intrare nouă prin write
        self.quant.write({"quantity": 20.0})
        self.assertGreaterEqual(
            self.quant.l10n_ro_last_in_date,
            old_in_date,
            "l10n_ro_last_in_date ar trebui să fie actualizat la creșterea cantității.",
        )

    def test_02_report_generation(self):
        """Verifică generarea raportului și calculul intervalelor."""
        # Setăm o dată de intrare în trecut pentru a testa intervalele
        past_date = fields.Datetime.now() - timedelta(days=45)
        self.quant.write({"l10n_ro_last_in_date": past_date})

        wizard = self.env["l10n.ro.stock.age.report"].create(
            {
                "warehouse_id": self.warehouse.id,
                "interval_days": "30",
                "date_ref": fields.Date.today(),
            }
        )

        # Calculăm raportul
        wizard.do_compute_report()

        self.assertTrue(wizard.line_ids, "Raportul ar trebui să aibă linii generate.")

        # Verificăm dacă linia are intervalul corect (30-60 zile pentru 45 zile vechime)
        # Intervalele de 30 zile sunt: 0-30, 30-60, 60-90, etc.
        line = wizard.line_ids.filtered(lambda l: l.product_id == self.product)
        self.assertEqual(len(line), 1)
        self.assertIn("30 - 60", line.name, "Intervalul pentru 45 de zile ar trebui să fie 30-60.")
        self.assertEqual(line.quantity, 10.0)
        self.assertEqual(line.value, 1000.0)  # 10 * 100.0
