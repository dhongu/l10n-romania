# Copyright (C) 2019 NextERP Romania
# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockBase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.account_fiscal_country_id = cls.env.ref("base.ro")
        cls.company._l10n_ro_create_stock_locations()
        cls.warehouse_obj = cls.env["stock.warehouse"]

    def test_company_locations(self):
        self.assertEqual(self.company.l10n_ro_usage_location_id.usage, "usage_giving")
        self.assertEqual(self.company.l10n_ro_consume_location_id.usage, "consume")

    def test_company_locations_are_not_duplicated(self):
        usage = self.company.l10n_ro_usage_location_id
        consume = self.company.l10n_ro_consume_location_id
        self.company._l10n_ro_create_stock_locations()
        self.env["res.company"].l10n_ro_create_missing_stock_locations()
        self.assertEqual(self.company.l10n_ro_usage_location_id, usage)
        self.assertEqual(self.company.l10n_ro_consume_location_id, consume)
        self.assertEqual(
            self.env["stock.location"].search_count(
                [("usage", "=", "usage_giving"), ("company_id", "=", self.company.id)]
            ),
            1,
        )

    def test_existing_location_is_taken_over(self):
        domain = [("usage", "=", "consume"), ("company_id", "=", self.company.id)]
        before = self.env["stock.location"].search_count(domain)
        self.company.l10n_ro_consume_location_id = False
        self.company._l10n_ro_create_stock_locations()
        self.assertTrue(self.company.l10n_ro_consume_location_id)
        self.assertEqual(self.env["stock.location"].search_count(domain), before)

    def test_warehouse_creation(self):
        warehouse = self.warehouse_obj.create(
            {"name": "Warehouse Romania", "code": "ROW", "company_id": self.company.id}
        )
        consume_type = warehouse.l10n_ro_consume_type_id
        usage_type = warehouse.l10n_ro_usage_type_id
        self.assertTrue(consume_type)
        self.assertTrue(usage_type)
        self.assertEqual(consume_type.code, "internal")
        self.assertEqual(consume_type.default_location_src_id, warehouse.lot_stock_id)
        self.assertEqual(
            consume_type.default_location_dest_id,
            self.company.l10n_ro_consume_location_id,
        )
        self.assertEqual(usage_type.code, "internal")
        self.assertEqual(usage_type.default_location_src_id, warehouse.lot_stock_id)
        self.assertEqual(
            usage_type.default_location_dest_id,
            self.company.l10n_ro_usage_location_id,
        )
        self.assertEqual(consume_type.sequence_code, "CONS")
        self.assertEqual(usage_type.sequence_code, "USAGE")

    def test_warehouse_rename(self):
        warehouse = self.warehouse_obj.create({"name": "Warehouse Romania", "code": "ROW"})
        warehouse._update_name_and_code(new_name="Warehouse", new_code="WRO")
        self.assertEqual(warehouse.l10n_ro_consume_type_id.sequence_id.prefix, "WRO/CONS/")
        self.assertEqual(warehouse.l10n_ro_usage_type_id.sequence_id.prefix, "WRO/USAGE/")

    def test_warehouse_outside_romania(self):
        company = self.env["res.company"].create({"name": "Foreign company"})
        company.account_fiscal_country_id = self.env.ref("base.fr")
        warehouse = self.warehouse_obj.create({"name": "Foreign", "code": "FRW", "company_id": company.id})
        self.assertFalse(warehouse.l10n_ro_consume_type_id)
        self.assertFalse(warehouse.l10n_ro_usage_type_id)
        self.assertFalse(company.l10n_ro_usage_location_id)

    def test_new_romanian_company_gets_locations(self):
        company = self.env["res.company"].create({"name": "New RO company", "country_id": self.env.ref("base.ro").id})
        company.account_fiscal_country_id = self.env.ref("base.ro")
        company._create_per_company_locations()
        self.assertTrue(company.l10n_ro_usage_location_id)
        self.assertTrue(company.l10n_ro_consume_location_id)

    def test_consume_and_usage_moves_are_incoming_and_outgoing(self):
        consume = self.company.l10n_ro_consume_location_id
        stock = self.warehouse_obj.search([("company_id", "=", self.company.id)], limit=1).lot_stock_id
        product = self.env["product.product"].create({"name": "P", "is_storable": True})
        move = self.env["stock.move"].create(
            {
                "product_id": product.id,
                "product_uom_qty": 1,
                "location_id": stock.id,
                "location_dest_id": consume.id,
            }
        )
        self.assertTrue(move._is_outgoing())
        move.location_id, move.location_dest_id = consume, stock
        self.assertTrue(move._is_incoming())

    def test_create_product(self):
        product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "is_storable": True,
                "l10n_ro_net_weight": 1.0,
            }
        )
        self.assertTrue(product.product_tmpl_id.l10n_ro_net_weight)
        self.assertTrue(product.product_tmpl_id.l10n_ro_net_weight_uom_name)
        product.product_tmpl_id.l10n_ro_net_weight = 2.0
        self.assertEqual(product.l10n_ro_net_weight, 2.0)
