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
        cls.env.user.group_ids += cls.env.ref("stock.group_stock_multi_locations")
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
        return html_bytes.decode("utf-8") if isinstance(html_bytes, (bytes, bytearray)) else str(html_bytes)

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

    def test_delivery_price_fallback_without_sale_order(self):
        """Livrare fără comandă de vânzare (ex. aviz): prețul cade pe lista de prețuri / list_price."""
        picking = self._create_picking(self.picking_type_out, qty=2.0, partner=self.partner_customer)
        move = picking.move_ids[0]
        self.assertFalse(move.sale_line_id)
        handler = self.env["report.l10n_ro_stock_picking_report.report_delivery_price"]
        res = handler._get_line(move)
        self.assertAlmostEqual(res["price"], 20.0, places=2)
        self.assertAlmostEqual(res["amount"], 40.0, places=2)
        self.assertAlmostEqual(res["amount_tax"], res["amount"] + res["tax"], places=2)
        totals = handler._get_totals(picking.move_ids)
        self.assertAlmostEqual(totals["amount"], 40.0, places=2)

    def test_report_delivery_notice_title(self):
        """Livrarea marcată ca aviz se tipărește cu titlul de aviz de însoțire."""
        if "l10n_ro_notice" not in self.env["stock.picking"]._fields:
            self.skipTest("l10n_ro_stock_account is not installed (no l10n_ro_notice field)")
        picking = self._create_picking(self.picking_type_out, qty=1.0, partner=self.partner_customer)
        picking.l10n_ro_notice = True
        html = self._render_report_html("l10n_ro_stock_picking_report.action_report_delivery_price", picking)
        self.assertIn("Goods Dispatch Note:", html)
        self.assertNotIn("Delivery:", html)

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
        try:
            html = self._render_report_html("l10n_ro_stock_picking_report.action_report_internal_transfer", picking)
        except Exception as e:
            if "rlPyCairo" in str(e) or "_rl_renderPM" in str(e) or "barcode" in str(e).lower():
                self.skipTest("rlPyCairo not installed, skipping barcode render test")
            raise
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

    # -----------------------------
    # Tests for l10n_ro_sale_price fix
    # -----------------------------
    def test_sale_price_stored_at_reception(self):
        """La validarea recepției, l10n_ro_sale_price trebuie populat cu list_price curent."""
        self.product.list_price = 25.0
        picking = self._create_picking(self.picking_type_in, qty=2.0, partner=self.partner_supplier)
        for move in picking.move_ids:
            self.assertAlmostEqual(
                move.l10n_ro_sale_price,
                25.0,
                msg="l10n_ro_sale_price trebuie să fie egal cu list_price la momentul recepției",
            )

    def test_sale_price_not_affected_by_later_price_change(self):
        """Modificarea list_price după recepție nu trebuie să afecteze l10n_ro_sale_price stocat."""
        self.product.list_price = 30.0
        picking = self._create_picking(self.picking_type_in, qty=1.0, partner=self.partner_supplier)
        # Modificăm prețul de vânzare după recepție
        self.product.list_price = 99.0
        for move in picking.move_ids:
            self.assertAlmostEqual(
                move.l10n_ro_sale_price,
                30.0,
                msg="l10n_ro_sale_price nu trebuie modificat după schimbarea list_price",
            )
            # list_price curent este diferit
            self.assertAlmostEqual(move.product_id.list_price, 99.0)

    def test_sale_price_used_in_report_values(self):
        """Raportul NIR trebuie să folosească l10n_ro_sale_price, nu list_price curent."""
        self.product.list_price = 40.0
        picking = self._create_picking(self.picking_type_in, qty=1.0, partner=self.partner_supplier)
        # Modificăm prețul după recepție
        self.product.list_price = 80.0
        report_model = self.env["report.abstract_report.reception_report"]
        for move in picking.move_ids:
            res = report_model._get_line(move)
            self.assertAlmostEqual(
                res["list_price"],
                40.0,
                msg="Raportul trebuie să folosească prețul stocat la recepție (40.0), nu cel curent (80.0)",
            )

    def test_reception_amount_with_packaging_uom(self):
        """Suma de pe NIR trebuie calculată cu prețul și cantitatea în ACEEAȘI unitate.

        `move.price_unit` vine în unitatea de referință a produsului (lei/kg), iar
        cantitatea de pe document e în unitatea liniei (cutii). Înmulțite ca atare,
        NIR-ul ieșea mai mic cu exact factorul unității — la Inedit, o recepție de
        1.344 de cutii a 13 kg la 2,90 lei/kg afișa 3.897,60 lei în loc de 50.668,80.

        Cazul apare DOAR cu `stock.propagate_uom = 1`. Implicit, Odoo convertește
        mișcarea în unitatea de referință a produsului (`_adjust_uom_quantities`),
        deci preț și cantitate ajung amândouă în kg și suma iese corectă — de aceea
        eroarea a trecut neobservată în configurația standard.
        """
        self.env["ir.config_parameter"].sudo().set_param("stock.propagate_uom", "1")
        uom_kg = self.product.uom_id
        uom_box = self.env["uom.uom"].create(
            {
                "name": "Cutie 13 kg (test)",
                "relative_uom_id": uom_kg.id,
                "relative_factor": 13.0,
            }
        )
        purchase = self.env["purchase.order"].create(
            {
                "partner_id": self.partner_supplier.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_qty": 10.0,
                            "product_uom_id": uom_box.id,
                            "price_unit": 37.70,
                            "tax_ids": [(6, 0, [])],
                        },
                    )
                ],
            }
        )
        purchase.button_confirm()
        picking = purchase.picking_ids[:1]
        self.assertTrue(picking, "comanda de achiziție nu a generat recepție")
        for move in picking.move_ids:
            move.move_line_ids.quantity = move.product_uom_qty
        picking.move_ids.picked = True
        picking._action_done()

        move = picking.move_ids[0]
        # prețul de pe mișcare e per kg (unitatea de referință)
        self.assertAlmostEqual(move.price_unit, 37.70 / 13.0, places=4)
        # cantitatea de pe document e în cutii
        self.assertAlmostEqual(move.quantity, 10.0)
        self.assertAlmostEqual(move.product_qty, 130.0)

        res = self.env["report.abstract_report.reception_report"]._get_line(move)
        self.assertAlmostEqual(
            res["price"],
            37.70,
            places=2,
            msg="Prețul afișat trebuie să fie per cutie, nu per kg",
        )
        self.assertAlmostEqual(
            res["amount"],
            377.00,
            places=2,
            msg="Suma trebuie să fie 10 cutii × 37,70 lei, nu 10 × 2,90",
        )

    def test_sale_price_not_set_for_outgoing(self):
        """l10n_ro_sale_price nu trebuie populat pentru livrări (outgoing)."""
        self.product.list_price = 50.0
        picking = self._create_picking(self.picking_type_out, qty=1.0, partner=self.partner_customer)
        for move in picking.move_ids:
            self.assertAlmostEqual(
                move.l10n_ro_sale_price,
                0.0,
                msg="l10n_ro_sale_price nu trebuie setat pentru livrări",
            )

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
