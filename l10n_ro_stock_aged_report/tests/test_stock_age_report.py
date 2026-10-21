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

    def test_03_report_without_product_covers_all_stock(self):
        """Fără produs ales, raportul ia toate cuantele din locații, fără plafon de produse."""
        other = self.env["product.product"].create(
            {"name": "Other Product", "is_storable": True, "standard_price": 5.0}
        )
        self.env["stock.quant"].create({"product_id": other.id, "location_id": self.location.id, "quantity": 3.0})

        wizard = self.env["l10n.ro.stock.age.report"].create({"warehouse_id": self.warehouse.id})
        wizard.do_compute_report()
        self.assertEqual(wizard.line_ids.product_id & (self.product | other), self.product | other)
        quants = self.env["stock.quant"].search(
            [("location_id", "in", wizard.location_ids.location_id.ids), ("quantity", ">", 0)]
        )
        self.assertEqual(len(wizard.line_ids), len(quants), "O linie pentru fiecare cuantă pozitivă.")

        filtered = self.env["l10n.ro.stock.age.report"].create(
            {"warehouse_id": self.warehouse.id, "product_id": other.id}
        )
        filtered.do_compute_report()
        self.assertEqual(filtered.line_ids.product_id, other)
        self.assertEqual(filtered.line_ids.value, 15.0)

    def test_04_recompute_replaces_lines(self):
        """Al doilea calcul pe același dialog înlocuiește liniile, nu le dublează."""
        wizard = self.env["l10n.ro.stock.age.report"].create(
            {"warehouse_id": self.warehouse.id, "product_id": self.product.id}
        )
        wizard.do_compute_report()
        first_lines = wizard.line_ids
        self.assertEqual(len(first_lines), 1)

        wizard.do_compute_report()
        self.assertEqual(len(wizard.line_ids), 1, "Recalculul nu trebuie să dubleze liniile.")
        self.assertFalse(first_lines.exists(), "Liniile calculului anterior sunt șterse.")
        self.assertEqual(wizard.line_ids.quantity, 10.0)

    def test_05_locations_editable(self):
        """Lista de locații se poate restrânge: raportul ia doar locațiile rămase în listă."""
        shelf = self.env["stock.location"].create(
            {"name": "Raft test", "usage": "internal", "location_id": self.location.id}
        )
        self.env["stock.quant"].create({"product_id": self.product.id, "location_id": shelf.id, "quantity": 4.0})

        wizard = self.env["l10n.ro.stock.age.report"].create({"warehouse_id": self.warehouse.id})
        self.assertIn(shelf, wizard.location_ids.location_id)
        wizard.location_ids.filtered(lambda l: l.location_id != shelf).unlink()
        wizard.do_compute_report()
        self.assertEqual(wizard.line_ids.product_id, self.product)
        self.assertEqual(wizard.line_ids.quantity, 4.0)
