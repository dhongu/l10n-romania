# Copyright (C) 2024 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestDropshipReport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.write(
            {
                "l10n_ro_accounting": True,
                "anglo_saxon_accounting": True,
            }
        )

        cls.account_valuation = cls.env["account.account"].search(
            [("code", "=", "371000"), ("company_id", "=", cls.env.company.id)], limit=1
        )
        if not cls.account_valuation:
            cls.account_valuation = cls.env["account.account"].create(
                {
                    "name": "Marfa",
                    "code": "371000",
                    "account_type": "asset_current",
                    "company_id": cls.env.company.id,
                }
            )

        cls.stock_journal = cls.env["account.journal"].search(
            [("code", "=", "STJ"), ("company_id", "=", cls.env.company.id)], limit=1
        )
        if not cls.stock_journal:
            cls.stock_journal = cls.env["account.journal"].create(
                {"name": "Stock Journal", "code": "STJ", "type": "general", "company_id": cls.env.company.id}
            )

        cls.category = cls.env["product.category"].create(
            {
                "name": "Dropship Category",
                "property_cost_method": "fifo",
                "property_valuation": "real_time",
                "property_stock_valuation_account_id": cls.account_valuation.id,
                "property_stock_journal": cls.stock_journal.id,
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Dropship Product",
                "is_storable": True,
                "categ_id": cls.category.id,
                "list_price": 100.0,
                "standard_price": 60.0,
            }
        )

        cls.vendor = cls.env["res.partner"].create({"name": "Dropship Vendor"})
        cls.customer = cls.env["res.partner"].create({"name": "Dropship Customer"})

        # Seller info for dropship
        cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.vendor.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "price": 60.0,
            }
        )

        cls.dropship_route = cls.env.ref("stock_dropshipping.route_drop_shipping")
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.env.company.id)], limit=1)
        cls.location = cls.warehouse.lot_stock_id

    def test_dropship_stock_report(self):
        # Create Sale Order with dropship route
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.customer
        with so_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 10.0
            line.route_id = self.dropship_route
        so = so_form.save()
        so.action_confirm()

        # Check that a Purchase Order was created
        po = self.env["purchase.order"].search([("origin", "=", so.name)])
        self.assertTrue(po, "Purchase Order should be created for dropship")
        po.button_confirm()

        # Validate the dropship picking
        picking = po.picking_ids[0]
        self.assertEqual(picking.picking_type_id, self.env.ref("stock_dropshipping.picking_type_dropship"))

        # We need to make sure the SVL is created.
        # In Odoo 18, we can use the following to validate:
        picking.move_ids.quantity = 10.0
        picking.button_validate()

        self.assertEqual(picking.state, "done")

        # Verify SVL exists for the dropship move
        svl = self.env["stock.valuation.layer"].search([("stock_move_id", "in", picking.move_ids.ids)])
        self.assertTrue(svl, "Stock Valuation Layer should be created for dropship move")

        # Now check the storage sheet wizard
        wizard_form = Form(self.env["l10n.ro.stock.storage.sheet"])
        wizard_form.location_id = self.location  # Even if it's dropship, we need a location in wizard usually
        wizard = wizard_form.save()

        # Check if product is included in products with moves
        product_ids = wizard.get_products_with_move_sql()
        self.assertIn(self.product.id, product_ids, "Dropship product should be in the list of products with moves")

        # Generate report lines
        wizard.button_show_sheet_pdf()

        lines = self.env["l10n.ro.stock.storage.sheet.line"].search(
            [("report_id", "=", wizard.id), ("product_id", "=", self.product.id)]
        )

        self.assertTrue(lines, "Report lines should be generated for the dropship product")

        # Check if any line has valued_type 'dropship'
        dropship_lines = lines.filtered(lambda l: l.valued_type == "dropship")
        self.assertTrue(dropship_lines, "There should be report lines with valued_type 'dropship'")

        # Check quantities (should be in both in and out for dropship)
        self.assertEqual(sum(dropship_lines.mapped("quantity_in")), 10.0)
        self.assertEqual(sum(dropship_lines.mapped("quantity_out")), 10.0)
