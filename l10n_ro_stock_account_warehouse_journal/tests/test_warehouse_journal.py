# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.l10n_ro_stock_account.tests.common import TestROStockCommon


@tagged("post_install", "-at_install")
class TestWarehouseJournal(TestROStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.main_warehouse = cls.location.warehouse_id
        cls.warehouse = cls.location1.warehouse_id
        cls.warehouse_journal = cls.env["account.journal"].create(
            {"name": "Stock TW2", "code": "STW2", "type": "general", "company_id": cls.env.company.id}
        )
        cls.warehouse.l10n_ro_property_stock_journal_id = cls.warehouse_journal
        cls.product_avg.standard_price = 10.0

    def _inventory(self, location, qty):
        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {"product_id": self.product_avg.id, "location_id": location.id, "inventory_quantity": qty}
        ).action_apply_inventory()
        return self.env["stock.move"].search(
            [("product_id", "=", self.product_avg.id), ("location_dest_id", "=", location.id), ("state", "=", "done")],
            order="id desc",
            limit=1,
        )

    def _entries(self, move):
        return move.account_move_id | self.env["account.move"].search([("l10n_ro_extra_stock_move_id", "=", move.id)])

    def test_entry_of_warehouse_with_journal(self):
        move = self._inventory(self.location1, 5)
        entries = self._entries(move)
        self.assertTrue(entries, "the inventory gain should be posted")
        self.assertEqual(entries.journal_id, self.warehouse_journal)

    def test_entry_of_warehouse_without_journal(self):
        move = self._inventory(self.location, 5)
        entries = self._entries(move)
        self.assertTrue(entries)
        self.assertEqual(entries.journal_id, self.stock_journal)

    def test_transfer_between_warehouses_with_different_journals_is_refused(self):
        other_journal = self.env["account.journal"].create(
            {"name": "Stock WH", "code": "SWH", "type": "general", "company_id": self.env.company.id}
        )
        self.main_warehouse.l10n_ro_property_stock_journal_id = other_journal
        self._inventory(self.location, 5)
        move = self.env["stock.move"].create(
            {
                "product_id": self.product_avg.id,
                "product_uom_qty": 2,
                "location_id": self.location.id,
                "location_dest_id": self.location1.id,
            }
        )
        move._action_confirm()
        move._action_assign()
        move.quantity = 2
        self.assertTrue(move._should_create_account_move(), "the two warehouses have different stock accounts")
        with self.assertRaises(UserError):
            move._action_done()

    def test_other_entries_keep_their_journal(self):
        sale_journal = self.company_data["default_journal_sale"]
        entry = (
            self.env["account.move"]
            .with_context(l10n_ro_stock_journal_id=self.warehouse_journal.id)
            .create({"move_type": "entry", "journal_id": sale_journal.id})
        )
        self.assertEqual(entry.journal_id, sale_journal)
