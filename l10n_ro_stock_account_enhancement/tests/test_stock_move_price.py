# © 2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestStockMovePrice(AccountTestInvoicingCommon):
    """Verificarea prețului unitar nenul pe mișcările de stoc (`stock.move._get_price_unit`)
    și notele contabile ale recepției / livrării pe planul de conturi RO."""

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.stock_journal = cls.env["account.journal"].create(
            {"name": "Stock Journal", "code": "STKJ", "type": "general", "company_id": cls.company.id}
        )
        cls.company.account_stock_journal_id = cls.stock_journal
        cls.categ = cls.env["product.category"].create(
            {
                "name": "Mărfuri FIFO",
                "property_valuation": "real_time",
                "property_cost_method": "fifo",
                "property_stock_valuation_account_id": cls.company.account_stock_valuation_id.id,
                "l10n_ro_stock_account_change": True,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Marfă test",
                "is_storable": True,
                "categ_id": cls.categ.id,
                "purchase_method": "receive",
                "invoice_policy": "delivery",
            }
        )
        cls.supplier = cls.env["res.partner"].create({"name": "Furnizor test"})
        cls.customer = cls.env["res.partner"].create({"name": "Client test"})
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.company.id)], limit=1)
        cls.icp = cls.env["ir.config_parameter"].sudo()

    def _receive(self, qty, price):
        purchase = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
                "order_line": [(0, 0, {"product_id": self.product.id, "product_qty": qty, "price_unit": price})],
            }
        )
        purchase.button_confirm()
        picking = purchase.picking_ids
        # recepție cu aviz: nota Dr 371 / Cr 408 se face la recepție, nu la factură
        picking.l10n_ro_notice = True
        picking.move_ids._set_quantity_done(qty)
        picking.move_ids.picked = True
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        return picking.move_ids

    def _deliver(self, qty):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.out_type_id.id,
                "partner_id": self.customer.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": qty,
                            "location_id": self.warehouse.lot_stock_id.id,
                            "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids._set_quantity_done(qty)
        picking.move_ids.picked = True
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        return picking.move_ids

    def _lines(self, moves):
        """Liniile notei contabile a mișcării, ca (cont, debit, credit), ordonate."""
        lines = moves.account_move_id.line_ids
        return sorted((line.account_id.code, line.debit, line.credit) for line in lines)

    def test_01_reception_and_delivery_entries(self):
        """Recepție cu aviz 5 × 10 și livrare 2: prețul unitar e nenul, notele sunt Dr/Cr corecte."""
        in_move = self._receive(5, 10.0)
        self.assertAlmostEqual(in_move._get_price_unit(), 10.0)
        self.assertTrue(in_move.account_move_id, "Recepția trebuie să genereze notă contabilă")
        self.assertEqual(self._lines(in_move), [("371000", 50.0, 0.0), ("408100", 0.0, 50.0)])

        out_move = self._deliver(2)
        self.assertLess(out_move.value, 0.0, "În 20.0 valoarea mișcării de ieșire e negativă")
        self.assertAlmostEqual(out_move._get_price_unit(), 10.0)
        self.assertEqual(self._lines(out_move), [("371000", 0.0, 20.0), ("607000", 20.0, 0.0)])

    def test_02_zero_price_unit_raises(self):
        """O mișcare fără valoare blochează calculul prețului unitar."""
        in_move = self._receive(3, 0.0)
        self.icp.set_bool("l10n_ro_stock_account.skip_price_unit_check", False)
        with self.assertRaisesRegex(UserError, "Price unit is not set for product"):
            in_move._get_price_unit()

    def test_03_zero_price_unit_skip_param(self):
        """Parametrul `l10n_ro_stock_account.skip_price_unit_check` dezactivează verificarea."""
        in_move = self._receive(3, 0.0)
        self.icp.set_bool("l10n_ro_stock_account.skip_price_unit_check", True)
        self.assertEqual(in_move._get_price_unit(), 0.0)

    def test_04_zero_price_unit_cogs_not_checked(self):
        """Prețul folosit la costul vânzării (COGS) al facturii nu e verificat, ca în 19.0."""
        in_move = self._receive(3, 0.0)
        self.assertEqual(in_move._get_price_unit(include_consigned=True, product=self.product), 0.0)
