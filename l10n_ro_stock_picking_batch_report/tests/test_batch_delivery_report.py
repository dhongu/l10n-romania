# ©  2026 Terrabit
# See README.rst file on addons root folder for license details
"""Avizul lotului: cumularea pe produs și valoarea în unitatea liniei de comandă."""

import re

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestBatchDeliveryReport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.env.company.id)], limit=1)
        cls.partner = cls.env["res.partner"].create({"name": "Client Aviz Lot"})
        cls.product = cls.env["product.product"].create({"name": "Pix Aviz Lot", "type": "consu", "list_price": 2.0})
        cls.dozen = cls.env.ref("uom.product_uom_dozen")

    def _delivery(self, qty, uom, price):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": qty,
                            "product_uom_id": uom.id,
                            "price_unit": price,
                        },
                    )
                ],
            }
        )
        order.action_confirm()
        picking = order.picking_ids
        picking.move_ids.quantity = picking.move_ids.product_uom_qty
        return picking

    def _render(self, batch):
        html, _type = self.env["ir.actions.report"]._render_qweb_html(
            "l10n_ro_stock_picking_batch_report.report_batch_delivery", batch.ids
        )
        return html.decode()

    def test_value_uses_the_order_line_unit(self):
        """2 duzini la 24 lei duzina + 6 bucăți la 2 lei = 30 de bucăți, 60 de lei."""
        pickings = self._delivery(2, self.dozen, 24.0) | self._delivery(6, self.product.uom_id, 2.0)
        batch = self.env["stock.picking.batch"].create({"picking_ids": [(6, 0, pickings.ids)]})
        # o comandă în duzini păstrează pe mișcare unitatea comenzii sau o trece în bucăți;
        # avizul trebuie să dea aceeași valoare în ambele cazuri
        html = self._render(batch)
        # cifrele fără separatori, ca testul să nu depindă de formatul limbii
        qty = re.search(r'data-oe-expression="product_qty">([^<]+)<', html).group(1)
        values = re.findall(r'oe_currency_value">([^<]+)<', html)
        self.assertEqual(re.sub(r"\D", "", qty), "3000")
        # preț unitar mediu 2,00, valoarea liniei 60,00, totalul 60,00
        self.assertEqual([re.sub(r"\D", "", v) for v in values], ["200", "6000", "6000"])
