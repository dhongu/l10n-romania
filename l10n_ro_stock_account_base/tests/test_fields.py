# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockAccountFields(TransactionCase):
    FIELDS = {
        "account.account": [
            "l10n_ro_stock_consume_account_id",
            "l10n_ro_reception_in_progress_account_id",
        ],
        "account.move": ["l10n_ro_extra_stock_move_id", "fifo_neg_origin_move_id"],
        "product.category": ["l10n_ro_stock_account_change"],
        "product.template": ["l10n_ro_property_stock_valuation_account_id"],
        "res.company": [
            "fifo_per_location",
            "fifo_location_negative_compensation",
            "l10n_ro_property_stock_picking_payable_account_id",
            "l10n_ro_property_stock_picking_receivable_account_id",
            "l10n_ro_property_stock_usage_giving_account_id",
            "l10n_ro_property_stock_transfer_account_id",
            "l10n_ro_property_uneligible_tax_account_id",
        ],
        "stock.location": [
            "l10n_ro_property_account_income_location_id",
            "l10n_ro_property_account_expense_location_id",
            "l10n_ro_property_stock_valuation_account_id",
        ],
        "stock.move": [
            "l10n_ro_extra_account_move_ids",
            "l10n_ro_move_type",
            "l10n_ro_account_id",
            "l10n_ro_transfer_account_id",
            "fifo_neg_pending_qty",
            "fifo_neg_origin_value",
            "fifo_neg_compensation_move_ids",
        ],
        "stock.picking": ["l10n_ro_notice", "l10n_ro_reception_in_progress"],
        "stock.warehouse": ["l10n_ro_fiscal_position_id"],
    }

    def test_fields_exist(self):
        for model, names in self.FIELDS.items():
            for name in names:
                self.assertIn(name, self.env[model]._fields, f"{model}.{name}")

    def test_values_are_kept(self):
        account = self.env["account.account"].search([], limit=1)
        location = self.env["stock.location"].create(
            {
                "name": "Test RO account",
                "l10n_ro_property_stock_valuation_account_id": account.id,
            }
        )
        location.invalidate_recordset()
        self.assertEqual(
            location.l10n_ro_property_stock_valuation_account_id, account
        )
        picking_type = self.env["stock.picking.type"].search([], limit=1)
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": picking_type.default_location_src_id.id
                or location.id,
                "location_dest_id": picking_type.default_location_dest_id.id
                or location.id,
                "l10n_ro_notice": True,
            }
        )
        picking.invalidate_recordset()
        self.assertTrue(picking.l10n_ro_notice)
