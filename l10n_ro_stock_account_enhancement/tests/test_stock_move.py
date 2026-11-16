# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockMovePriceUnit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["ir.config_parameter"].sudo().set_param("l10n_ro_stock_account.skip_price_unit_check", "False")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Produs fara pret",
                "is_storable": True,
                "standard_price": 0.0,
            }
        )
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.env.company.id)], limit=1)

    def test_01_empty_recordset_no_error(self):
        """Pe un recordset gol nu există produs de verificat: nu se ridică eroare."""
        self.assertEqual(self.env["stock.move"]._get_price_unit(), 0)

    def test_02_empty_recordset_delivery_no_error(self):
        """`_get_price_unit_delivery` (folosit de sale_stock_margin la validarea livrării)
        apelează `_get_price_unit` pe mișcările de retur, de obicei un recordset gol."""
        self.assertEqual(self.env["stock.move"]._get_price_unit_delivery(), 0)

    def test_03_real_move_without_price_raises(self):
        """Verificarea rămâne activă pentru o mișcare reală fără preț."""
        move = self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "location_id": self.warehouse.lot_stock_id.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )
        with self.assertRaisesRegex(UserError, "Price unit is not set for product Produs fara pret"):
            move._get_price_unit()
