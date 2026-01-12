# Copyright (C) 2025 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import base64
import logging

from odoo.tests.common import TransactionCase, tagged

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestSaleOrderReport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.logo = False
        # Partner
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
                "street": "Test Street 1",
                "city": "Bucharest",
                "country_id": cls.env.ref("base.ro").id,
                "email": "customer@example.com",
            }
        )

        # Simple 1x1 transparent PNG for product image_256
        png_1x1 = base64.b64encode(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
            b"\x00\x00\x00\x0cIDATx\x9cc``\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "list_price": 10.0,
                "image_256": png_1x1,
                "type": "consu",
            }
        )

        # Payment term with exactly two percent lines (50/50) so the template renders the "Transa" blocks
        # Provide the lines at creation time to avoid the default 100% line injected by the model's default.
        cls.pay_term = cls.env["account.payment.term"].create(
            {
                "name": "50/50",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "value": "percent",
                            "value_amount": 50.0,
                            "nb_days": 0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "value": "percent",
                            "value_amount": 50.0,
                            "nb_days": 30,
                        },
                    ),
                ],
            }
        )

        # Create a sale order with one line
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "payment_term_id": cls.pay_term.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 2,
                            "price_unit": 10.0,
                            "name": cls.product.display_name,
                        },
                    )
                ],
            }
        )

    def test_render_standard_sale_order_report_with_custom_columns(self):
        # Render the standard sale order report which our module customizes via xpath
        action = self.env.ref("sale.action_report_saleorder")
        html_bytes, _ = self.env["ir.actions.report"]._render_qweb_html(action, [self.so.id])
        html = html_bytes.decode("utf-8", errors="ignore")

        # Our template injects a numbering column header and a Customer label block
        self.assertIn("No.", html, "Expected 'No.' column header injected by l10n_ro_sale_order_report")
        self.assertIn("Customer", html, "Expected 'Customer' block injected by l10n_ro_sale_order_report")

        # # The image column should embed the product image as data URI
        # self.assertIn("data:image/", html, "Expected product image embedded as data URI in the report lines")

        # Since we set a 50/50 payment term with 2 lines, our template should render the "Transa:" labels
        self.assertIn("Transa:", html, "Expected 'Transa:' block rendered from payment terms")

        # Log for quick visual diagnostics when running tests with --log-level=info
        _logger.info("Rendered Sale Order report length: %s", len(html))

    def test_render_custom_proforma_template(self):
        # Ensure the custom proforma template compiles with a basic context
        qweb = self.env["ir.qweb"]
        if not self.so.pricelist_id:
            self.so.pricelist_id = self.env["product.pricelist"].search([], limit=1)
        values = {
            "doc": self.so.with_context(lang=self.so.partner_id.lang or self.env.lang),
            "docs": self.so,
            "proforma_type": "init",  # drive the percent path
        }
        html = qweb._render("l10n_ro_sale_order_report.saleorder_proforma_percent_document", values)
        self.assertTrue(html and isinstance(html, str), "Custom proforma template should render to a string")
