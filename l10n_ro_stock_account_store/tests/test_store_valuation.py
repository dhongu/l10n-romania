# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestStoreValuation(AccountTestInvoicingCommon):
    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        super().setUpClass()
        company = cls.env.company
        if not company.account_stock_journal_id:
            company.account_stock_journal_id = cls.env["account.journal"].create(
                {"name": "Stock Journal", "code": "STKT", "type": "general"}
            )
        cls.account_371 = company.account_stock_valuation_id
        cls.account_378 = cls._get_or_create_account("378000", "asset_current")
        cls.account_4428 = cls._get_or_create_account("442800", "liability_current")
        company.l10n_ro_property_uneligible_tax_account_id = cls.account_4428
        cls.tax_21 = cls.env["account.tax"].create(
            {
                "name": "TVA 21% test",
                "amount": 21,
                "amount_type": "percent",
                "type_tax_use": "sale",
            }
        )
        cls.category = cls.env["product.category"].create(
            {
                "name": "Marfuri magazin",
                "property_valuation": "real_time",
                "property_cost_method": "average",
                "property_stock_valuation_account_id": cls.account_371.id,
                "l10n_ro_property_store_markup_account_id": cls.account_378.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Produs magazin",
                "is_storable": True,
                "categ_id": cls.category.id,
                "list_price": 100.0,
                "standard_price": 60.0,
                "taxes_id": [(6, 0, cls.tax_21.ids)],
            }
        )
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1)
        cls.location_depot = cls.warehouse.lot_stock_id
        cls.location_store = cls.env["stock.location"].create(
            {
                "name": "Magazin",
                "usage": "internal",
                "location_id": cls.warehouse.view_location_id.id,
                "l10n_ro_merchandise_type": "store",
            }
        )
        cls.supplier = cls.env["res.partner"].create({"name": "Furnizor"})
        cls.customer = cls.env["res.partner"].create({"name": "Client"})

    @classmethod
    def _get_or_create_account(cls, code, account_type):
        account = cls.env["account.account"].search(
            [("code", "=", code), ("company_ids", "in", cls.env.company.id)], limit=1
        )
        return account or cls.env["account.account"].create({"code": code, "name": code, "account_type": account_type})

    def _move(self, src, dest, qty, price_unit=0.0, picking_type=None, partner=None):
        picking_type = picking_type or self.warehouse.int_type_id
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": src.id,
                "location_dest_id": dest.id,
                "partner_id": partner and partner.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": qty,
                            "price_unit": price_unit,
                            "location_id": src.id,
                            "location_dest_id": dest.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.quantity = qty
        picking.move_ids.picked = True
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        return picking.move_ids

    def _receive_in_store(self, qty=10, price_unit=60.0):
        return self._move(
            self.supplier.property_stock_supplier,
            self.location_store,
            qty,
            price_unit,
            self.warehouse.in_type_id,
            self.supplier,
        )

    def _store_lines(self, move):
        return move.l10n_ro_store_account_move_id.line_ids.sorted(lambda line: (line.account_id.code, line.debit))

    def test_reception_in_store(self):
        """Reception at cost 60, sale price 100 + 21% VAT.

        371 = 378 with 10 x (100 - 60) and 371 = 4428 with 10 x 21.
        """
        move = self._receive_in_store()
        self.assertRecordValues(
            move,
            [
                {
                    "value": 600.0,
                    "l10n_ro_store_sale_amount": 1210.0,
                    "l10n_ro_store_markup_amount": 400.0,
                    "l10n_ro_store_tax_amount": 210.0,
                }
            ],
        )
        lines = move.l10n_ro_store_account_move_id.line_ids
        self.assertEqual(move.l10n_ro_store_account_move_id.state, "posted")
        self.assertEqual(
            sum(lines.filtered(lambda x: x.account_id == self.account_371).mapped("balance")),
            610.0,
        )
        self.assertEqual(
            sum(lines.filtered(lambda x: x.account_id == self.account_378).mapped("balance")),
            -400.0,
        )
        self.assertEqual(
            sum(lines.filtered(lambda x: x.account_id == self.account_4428).mapped("balance")),
            -210.0,
        )

    def test_delivery_from_store_releases_at_entry_price(self):
        """The exit releases markup and VAT at the entry sale price, even if
        the sale price of the product changed in between."""
        self._receive_in_store()
        self.product.list_price = 150.0
        move = self._move(
            self.location_store,
            self.customer.property_stock_customer,
            4,
            picking_type=self.warehouse.out_type_id,
            partner=self.customer,
        )
        self.assertRecordValues(
            move,
            [
                {
                    # 20.0: the value of an outgoing move is negative
                    "value": -240.0,
                    "l10n_ro_store_sale_amount": 484.0,
                    "l10n_ro_store_markup_amount": -160.0,
                    "l10n_ro_store_tax_amount": -84.0,
                }
            ],
        )
        lines = move.l10n_ro_store_account_move_id.line_ids
        self.assertEqual(
            sum(lines.filtered(lambda x: x.account_id == self.account_371).mapped("balance")),
            -244.0,
        )
        self.assertEqual(
            sum(lines.filtered(lambda x: x.account_id == self.account_378).mapped("balance")),
            160.0,
        )
        self.assertEqual(
            sum(lines.filtered(lambda x: x.account_id == self.account_4428).mapped("balance")),
            84.0,
        )
        self.assertFalse(lines.filtered("is_storno"))

    def test_return_to_supplier_is_storno(self):
        """A return to the supplier reverses in red the entry of the reception."""
        reception = self._receive_in_store()
        return_picking = reception.picking_id._create_return()
        return_picking.move_ids.product_uom_qty = 2
        return_picking.move_ids.quantity = 2
        return_picking.move_ids.picked = True
        return_picking.button_validate()
        move = return_picking.move_ids
        self.assertEqual(move.origin_returned_move_id, reception)
        lines = move.l10n_ro_store_account_move_id.line_ids
        self.assertTrue(lines)
        self.assertTrue(all(lines.mapped("is_storno")))
        # same accounts as the reception (371 = 378 / 4428), negative amounts
        markup_debit = lines.filtered(lambda x: x.account_id == self.account_371)
        self.assertEqual(sum(markup_debit.mapped("debit")), -122.0)
        self.assertEqual(move.l10n_ro_store_sale_amount, 242.0)

    def test_transfer_depot_to_store(self):
        """Goods moved from the depot (at cost) to the store get the markup."""
        self._move(
            self.supplier.property_stock_supplier,
            self.location_depot,
            5,
            60.0,
            self.warehouse.in_type_id,
            self.supplier,
        )
        move = self._move(self.location_depot, self.location_store, 5)
        self.assertEqual(move.l10n_ro_store_sale_amount, 605.0)
        self.assertEqual(move.l10n_ro_store_markup_amount, 200.0)
        self.assertEqual(move.l10n_ro_store_tax_amount, 105.0)

    def test_depot_has_no_store_entry(self):
        move = self._move(
            self.supplier.property_stock_supplier,
            self.location_depot,
            5,
            60.0,
            self.warehouse.in_type_id,
            self.supplier,
        )
        self.assertFalse(move.l10n_ro_store_account_move_id)
        self.assertFalse(move.l10n_ro_store_sale_amount)

    def test_missing_markup_account(self):
        self.category.l10n_ro_property_store_markup_account_id = False
        with self.assertRaises(UserError):
            self._receive_in_store()

    def test_exit_from_shelf_uses_store_entry_price(self):
        """Goods received on the store and sold from one of its shelves are
        released at the entry price of the store."""
        shelf = self.env["stock.location"].create(
            {
                "name": "Raft 1",
                "usage": "internal",
                "location_id": self.location_store.id,
                "l10n_ro_merchandise_type": "store",
            }
        )
        self._receive_in_store()
        self._move(self.location_store, shelf, 10)
        self.product.list_price = 150.0
        move = self._move(
            shelf,
            self.customer.property_stock_customer,
            2,
            picking_type=self.warehouse.out_type_id,
            partner=self.customer,
        )
        self.assertEqual(move.l10n_ro_store_sale_amount, 242.0)

    def test_dedicated_uneligible_tax_account(self):
        account_44282 = self._get_or_create_account("442802", "liability_current")
        self.category.l10n_ro_property_store_uneligible_tax_account_id = account_44282
        move = self._receive_in_store()
        lines = move.l10n_ro_store_account_move_id.line_ids
        self.assertEqual(
            sum(lines.filtered(lambda x: x.account_id == account_44282).mapped("balance")),
            -210.0,
        )
        self.assertFalse(lines.filtered(lambda x: x.account_id == self.account_4428))

    def test_is_store_for_picking_report(self):
        """With l10n_ro_stock_picking_report, a store location is a store."""
        if "is_store" not in self.env["stock.location"]._fields:
            self.skipTest("l10n_ro_stock_picking_report not installed")
        self.assertTrue(self.location_store.is_store)
        self.assertFalse(self.location_depot.is_store)

    def _nir_line(self, move):
        """The NIR at sale price line of `l10n_ro_stock_picking_report` for `move`."""
        if "l10n_ro_sale_price" not in self.env["stock.move"]._fields:
            self.skipTest("l10n_ro_stock_picking_report not installed")
        return self.env["report.abstract_report.reception_report"]._get_line(move)

    def _assert_nir_matches_store_entry(self, move, sale_amount, markup, tax):
        self.assertRecordValues(
            move,
            [
                {
                    "l10n_ro_store_sale_amount": sale_amount,
                    "l10n_ro_store_markup_amount": markup,
                    "l10n_ro_store_tax_amount": tax,
                }
            ],
        )
        line = self._nir_line(move)
        self.assertAlmostEqual(line["amount_tax_sale"], sale_amount, places=2)
        self.assertAlmostEqual(line["tax_sale"], tax, places=2)
        self.assertAlmostEqual(line["amount_sale"] - line["amount"], markup, places=2)

    def test_nir_matches_store_entry(self):
        """The NIR at sale price and the 378 / 4428 entry use the same sale price."""
        move = self._receive_in_store()
        self._assert_nir_matches_store_entry(move, 1210.0, 400.0, 210.0)

    def test_store_pricelist_drives_nir_and_store_entry(self):
        """A store with its own pricelist: NIR and store entry both at the store price.

        Cost 60, store price 120 + 21% VAT, 10 pieces: markup 600, VAT 252, sale value 1.452,
        not the product price of 100.
        """
        if "store_pricelist_id" not in self.location_store._fields:
            self.skipTest("l10n_ro_stock_picking_report not installed")
        self.location_store.store_pricelist_id = self.env["product.pricelist"].create(
            {
                "name": "Preturi magazin",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "0_product_variant",
                            "product_id": self.product.id,
                            "compute_price": "fixed",
                            "fixed_price": 120.0,
                        },
                    )
                ],
            }
        )
        move = self._receive_in_store()
        self.assertEqual(move.l10n_ro_sale_price, 120.0)
        self._assert_nir_matches_store_entry(move, 1452.0, 600.0, 252.0)
        lines = move.l10n_ro_store_account_move_id.line_ids
        self.assertEqual(sum(lines.filtered(lambda x: x.account_id == self.account_378).mapped("balance")), -600.0)
        self.assertEqual(sum(lines.filtered(lambda x: x.account_id == self.account_4428).mapped("balance")), -252.0)
