# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAccountMove(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_storable = cls.env["product.product"].create(
            {
                "name": "Storable Product",
                "is_storable": True,
                "standard_price": 10.0,
                "list_price": 20.0,
            }
        )
        cls.product_service = cls.env["product.product"].create(
            {
                "name": "Service Product",
                "type": "service",
                "list_price": 15.0,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})

    def test_01_out_invoice_storable_no_so(self):
        """Test that an customer invoice with a storable product and no SO line fails on post if param is set"""
        self.env["ir.config_parameter"].sudo().set_param("l10n_ro_stock_account.check_storable_line_source", "True")
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_storable.id,
                            "quantity": 1,
                            "price_unit": 20.0,
                        },
                    )
                ],
            }
        )
        with self.assertRaisesRegex(UserError, "must have a reference to a sales order line"):
            invoice.action_post()

    def test_02_out_invoice_service_no_so(self):
        """Test that an customer invoice with a service product and no SO line succeeds on post"""
        self.env["ir.config_parameter"].sudo().set_param("l10n_ro_stock_account.check_storable_line_source", "True")
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_service.id,
                            "quantity": 1,
                            "price_unit": 15.0,
                        },
                    )
                ],
            }
        )
        # This should not raise an error
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")

    def test_03_in_invoice_storable_no_po(self):
        """Test that a vendor bill with a storable product and no PO line fails on post if param is set"""
        self.env["ir.config_parameter"].sudo().set_param("l10n_ro_stock_account.check_storable_line_source", "True")
        bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_storable.id,
                            "quantity": 1,
                            "price_unit": 10.0,
                        },
                    )
                ],
            }
        )
        with self.assertRaisesRegex(UserError, "must have a reference to a purchase order line"):
            bill.action_post()

    def test_04_out_invoice_storable_no_so_param_false(self):
        """Test that an customer invoice with a storable product and no SO line succeeds on post if param is NOT set"""
        self.env["ir.config_parameter"].sudo().set_param("l10n_ro_stock_account.check_storable_line_source", "False")
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_storable.id,
                            "quantity": 1,
                            "price_unit": 20.0,
                        },
                    )
                ],
            }
        )
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")
