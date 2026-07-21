# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestDropshipAccount(TransactionCase):
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
            [("code", "=", "371000"), ("company_ids", "in", cls.env.company.ids)], limit=1
        )
        if not cls.account_valuation:
            cls.account_valuation = cls.env["account.account"].create(
                {
                    "name": "Marfa",
                    "code": "371000",
                    "account_type": "asset_current",
                    "company_ids": [(6, 0, cls.env.company.ids)],
                }
            )

        cls.account_income = cls.env["account.account"].search(
            [("code", "=", "707000"), ("company_ids", "in", cls.env.company.ids)], limit=1
        )
        if not cls.account_income:
            cls.account_income = cls.env["account.account"].create(
                {
                    "name": "Venituri din vanzarea marfurilor",
                    "code": "707000",
                    "account_type": "income",
                    "company_ids": [(6, 0, cls.env.company.ids)],
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
                "property_stock_account_input_categ_id": cls.account_valuation.id,
                "property_stock_account_output_categ_id": cls.account_valuation.id,
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

        cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.vendor.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "price": 60.0,
            }
        )

        cls.dropship_route = cls.env.ref("stock_dropshipping.route_drop_shipping")
        cls.env.user.write({"groups_id": [(4, cls.env.ref("stock.group_adv_location").id)]})
        cls.env.invalidate_all()

    def _create_dropship_layers(self):
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.customer
        with so_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 10.0
        so = so_form.save()
        so.order_line.write({"route_id": self.dropship_route.id})
        so.action_confirm()

        po = self.env["purchase.order"].search([("partner_id", "=", self.vendor.id), ("origin", "=", so.name)])
        po.button_confirm()

        picking = po.picking_ids[0]
        picking.move_ids.quantity = 10.0
        picking.button_validate()

        return so, self.env["stock.valuation.layer"].search([("stock_move_id", "in", picking.move_ids.ids)])

    def test_sale_invoice_does_not_hijack_reception_account(self):
        """A dropship stock.move has both a purchase_line_id and a sale_line_id, so
        action_post() on the customer invoice can link its line to the RECEPTION
        valuation layer too (whichever invoice posts first "wins" every unlinked
        layer of the move). _compute_account() must then refuse to reuse that sale
        invoice line's income account for a reception layer.
        """
        so, svls = self._create_dropship_layers()
        reception = svls.filtered(lambda l: l.l10n_ro_valued_type in ("reception", "reception_return"))
        delivery = svls.filtered(lambda l: l.l10n_ro_valued_type in ("delivery", "delivery_return"))
        self.assertTrue(reception)
        self.assertTrue(delivery)

        customer_invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.customer.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 10.0,
                            "price_unit": 100.0,
                            "account_id": self.account_income.id,
                            "sale_line_ids": [(6, 0, so.order_line.ids)],
                        },
                    )
                ],
            }
        )
        invoice_line = customer_invoice.invoice_line_ids

        # Reproduce what account_move.py's action_post() does: it claims every
        # unlinked SVL of the stock move it finds via sale_line_id, including the
        # reception layer, before the reception even has a vendor bill.
        reception.write(
            {
                "l10n_ro_invoice_line_id": invoice_line.id,
                "l10n_ro_invoice_id": customer_invoice.id,
            }
        )
        reception._compute_account()

        self.assertEqual(
            reception.l10n_ro_account_id,
            self.account_valuation,
            "The reception (incoming) valuation layer must keep the merchandise "
            "account even though a customer (sale) invoice line claimed it first.",
        )
        self.assertNotEqual(
            reception.l10n_ro_account_id,
            self.account_income,
            "The reception valuation layer must never end up on a sale/income account.",
        )
