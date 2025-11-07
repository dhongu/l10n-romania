# Copyright (C) 2025 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestL10nRoStockPickingReport(TransactionCase):
    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        super().setUpClass()
        # Basic partner for customer/supplier
        cls.partner_customer = cls.env["res.partner"].create({"name": "Client SRL", "company_type": "company"})
        cls.partner_supplier = cls.env["res.partner"].create({"name": "Furnizor SRL", "company_type": "company"})
        cls.env.user.groups_id += cls.env.ref("stock.group_stock_multi_locations")
        # Simple storable product
        cls.env.company.logo = False
        cls.product = cls.env["product.product"].create(
            {
                "name": "Produs Test",
                "is_storable": True,
                "standard_price": 10.0,
                "list_price": 20.0,
            }
        )

        # Picking types (must exist from stock module setup)
        cls.picking_type_out = cls.env["stock.picking.type"].search([("code", "=", "outgoing")], limit=1)
        cls.picking_type_in = cls.env["stock.picking.type"].search([("code", "=", "incoming")], limit=1)
        cls.picking_type_int = cls.env["stock.picking.type"].search([("code", "=", "internal")], limit=1)
        if not cls.picking_type_int:
            cls.picking_type_int = cls.env["stock.picking.type"].create(
                {
                    "name": "Internal Transfer",
                    "code": "internal",
                    "use_create_lots": True,
                    "use_existing_lots": True,
                    "sequence_code": "INT1",
                    "default_location_src_id": cls.env.ref("stock.stock_location_stock").id,
                    "default_location_dest_id": cls.env.ref("stock.stock_location_stock").id,
                }
            )

        assert cls.picking_type_out and cls.picking_type_in and cls.picking_type_int, "Picking types missing"

    # -----------------------------
    # Helpers
    # -----------------------------
    def _create_picking(self, picking_type, qty=1.0, partner=None, scheduled_date="2025-01-15"):
        picking_vals = {
            "picking_type_id": picking_type.id,
            "location_id": picking_type.default_location_src_id.id,
            "location_dest_id": picking_type.default_location_dest_id.id,
            "origin": "TEST",
            "scheduled_date": scheduled_date,
        }
        if partner:
            picking_vals["partner_id"] = partner.id
        picking = self.env["stock.picking"].create(picking_vals)
        move = self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "product_uom_qty": qty,
                "product_uom": self.product.uom_id.id,
                "picking_id": picking.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
            }
        )

        picking.action_assign()
        for move in picking.move_ids:
            if move.product_uom_qty > 0 and move.product_qty == 0:
                move._set_quantity_done(move.product_uom_qty)
        picking.move_ids.picked = True
        picking._action_done()

        return picking

    def _render_report_html(self, action_xmlid, record):
        """Render report to HTML and return as decoded string."""

        html_bytes, _ = self.env["ir.actions.report"]._render_qweb_html(action_xmlid, [record.id])
        return html_bytes.decode("utf-8") if isinstance(html_bytes, bytes | bytearray) else str(html_bytes)

    # -----------------------------
    # Single picking reports
    # -----------------------------
    def test_report_delivery(self):
        picking = self._create_picking(self.picking_type_out, qty=2.0, partner=self.partner_customer)
        html = self._render_report_html("l10n_ro_stock_picking_report.action_report_delivery", picking)
        # Basic sanity checks: title and company/customer blocks from templates
        self.assertIn("Delivery:", html)
        self.assertIn("Company", html)
        self.assertIn("Customer", html)

    def test_report_delivery_with_price(self):
        picking = self._create_picking(self.picking_type_out, qty=1.0, partner=self.partner_customer)
        html = self._render_report_html("l10n_ro_stock_picking_report.action_report_delivery_price", picking)
        # Presence of the same blocks; price columns may be empty without SO link, but template should render
        self.assertIn("Delivery:", html)
        self.assertIn("Price", html)
        self.assertIn("Amount", html)

    def test_report_reception(self):
        picking = self._create_picking(self.picking_type_in, qty=3.0, partner=self.partner_supplier)
        html = self._render_report_html("l10n_ro_stock_picking_report.action_report_reception", picking)
        self.assertIn("Reception:", html)
        self.assertIn("Supplier", html)
        self.assertIn(self.product.display_name, html)

    def test_report_reception_no_tax(self):
        picking = self._create_picking(self.picking_type_in, qty=1.0, partner=self.partner_supplier)
        html = self._render_report_html("l10n_ro_stock_picking_report.action_report_reception_no_tax", picking)
        self.assertIn("Reception:", html)

    def test_report_reception_sale_price(self):
        picking = self._create_picking(self.picking_type_in, qty=1.0, partner=self.partner_supplier)
        html = self._render_report_html("l10n_ro_stock_picking_report.action_report_reception_sale_price", picking)
        self.assertIn("Reception:", html)
        # Template includes Sale Price column
        self.assertIn("Sale price", html)

    def test_report_internal_transfer(self):
        picking = self._create_picking(self.picking_type_int, qty=1.0)
        html = self._render_report_html("l10n_ro_stock_picking_report.action_report_internal_transfer", picking)
        # For internal, the title prints the picking type name followed by ':'
        self.assertIn(self.picking_type_int.name, html)
        self.assertIn("Location source", html)
        self.assertIn("Location destination", html)

    def test_report_consume_voucher(self):
        # Use internal picking; template will still render consume table/signature
        picking = self._create_picking(self.picking_type_int, qty=2.0)
        html = self._render_report_html("l10n_ro_stock_picking_report.action_report_consume_voucher", picking)
        self.assertIn("Consume", html)  # generic text in section ids/titles
        self.assertIn("Signature", html)  # signature block wording

    # -----------------------------
    # Cumulative reports
    # -----------------------------
    def test_report_cumulative_internal_transfer(self):
        # Create a couple of done internal moves in date range
        self._create_picking(self.picking_type_int, qty=1.0)
        self._create_picking(self.picking_type_int, qty=2.0)
        wiz = self.env["stock.picking.cumulative"].create(
            {
                "picking_type_id": self.picking_type_int.id,
                "report_id": self.env.ref("l10n_ro_stock_picking_report.action_report_c_internal_transfer").id,
            }
        )
        # Fill move_ids through button_show domain or directly
        wiz.button_show()
        html = self._render_report_html("l10n_ro_stock_picking_report.action_report_c_internal_transfer", wiz)
        self.assertIn("Quantity", html)
        self.assertIn("Product", html)

    def test_report_cumulative_reception_sale_price(self):
        # Ensure some incoming moves exist
        self._create_picking(self.picking_type_in, qty=1.0, partner=self.partner_supplier)
        wiz = self.env["stock.picking.cumulative"].create(
            {
                "picking_type_id": self.picking_type_in.id,
                "report_id": self.env.ref("l10n_ro_stock_picking_report.action_report_c_recep_sale_price").id,
            }
        )
        wiz.button_show()
        html = self._render_report_html("l10n_ro_stock_picking_report.action_report_c_recep_sale_price", wiz)
        self.assertIn("Sale price", html)
        self.assertIn("Product", html)
