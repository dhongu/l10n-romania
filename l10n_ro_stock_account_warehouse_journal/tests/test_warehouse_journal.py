# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestWarehouseJournal(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product1 = cls.env["product.product"].create({"name": "Stock product", "is_storable": True})
        cls.main_warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.env.company.id)], limit=1)
        cls.other_warehouse = cls.env["stock.warehouse"].create(
            {"name": "Second warehouse", "code": "SW2", "company_id": cls.env.company.id}
        )
        cls.journal_a = cls.env["account.journal"].create(
            {"name": "Stock A", "code": "STA", "type": "general", "company_id": cls.env.company.id}
        )
        cls.journal_b = cls.env["account.journal"].create(
            {"name": "Stock B", "code": "STB", "type": "general", "company_id": cls.env.company.id}
        )

    def _move(self, src, dest):
        return self.env["stock.move"].new(
            {"product_id": self.product1.id, "product_uom_qty": 1, "location_id": src.id, "location_dest_id": dest.id}
        )

    def test_journal_of_warehouse(self):
        self.other_warehouse.l10n_ro_property_stock_journal_id = self.journal_a
        move = self._move(self.env.ref("stock.stock_location_suppliers"), self.other_warehouse.lot_stock_id)
        self.assertEqual(move._l10n_ro_get_warehouse_stock_journal(), self.journal_a)

    def test_warehouse_without_journal_uses_company_journal(self):
        move = self._move(self.env.ref("stock.stock_location_suppliers"), self.main_warehouse.lot_stock_id)
        self.assertFalse(move._l10n_ro_get_warehouse_stock_journal())

    def test_transfer_between_warehouses_with_different_journals_is_refused(self):
        self.main_warehouse.l10n_ro_property_stock_journal_id = self.journal_a
        self.other_warehouse.l10n_ro_property_stock_journal_id = self.journal_b
        move = self._move(self.main_warehouse.lot_stock_id, self.other_warehouse.lot_stock_id)
        with self.assertRaises(UserError):
            move._l10n_ro_get_warehouse_stock_journal()

    def test_other_entries_keep_their_journal(self):
        sale_journal = self.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", self.env.company.id)], limit=1
        )
        entry = (
            self.env["account.move"]
            .with_context(l10n_ro_stock_journal_id=self.journal_a.id)
            .create({"move_type": "entry", "journal_id": sale_journal.id})
        )
        self.assertEqual(entry.journal_id, sale_journal)

    def test_stock_entry_is_posted_in_the_company_stock_journal_swapped(self):
        stock_journal = self.env.company.account_stock_journal_id
        entry = (
            self.env["account.move"]
            .with_context(l10n_ro_stock_journal_id=self.journal_a.id)
            .create({"move_type": "entry", "journal_id": stock_journal.id})
        )
        self.assertEqual(entry.journal_id, self.journal_a)
