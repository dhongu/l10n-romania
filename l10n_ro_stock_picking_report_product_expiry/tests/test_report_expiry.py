# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestReportExpiry(TransactionCase):
    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.logo = False
        cls.env.user.group_ids += cls.env.ref("stock.group_production_lot")
        cls.partner = cls.env["res.partner"].create({"name": "Client SRL"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Produs cu termen",
                "is_storable": True,
                "tracking": "lot",
                "use_expiration_date": True,
            }
        )
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.lot = cls.env["stock.lot"].create(
            {
                "name": "LOT-EXP-1",
                "product_id": cls.product.id,
                "expiration_date": datetime(2031, 3, 17, 12, 0),
            }
        )
        cls.env["stock.quant"]._update_available_quantity(cls.product, cls.stock, 5.0, lot_id=cls.lot)
        picking_type = cls.env["stock.picking.type"].search(
            [("code", "=", "outgoing"), ("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "partner_id": cls.partner.id,
                "location_id": cls.stock.id,
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
            }
        )
        cls.env["stock.move"].create(
            {
                "product_id": cls.product.id,
                "product_uom_qty": 2.0,
                "uom_id": cls.product.uom_id.id,
                "picking_id": cls.picking.id,
                "location_id": cls.picking.location_id.id,
                "location_dest_id": cls.picking.location_dest_id.id,
            }
        )
        cls.picking.action_confirm()
        cls.picking.action_assign()
        cls.picking.move_ids.picked = True
        cls.picking._action_done()

    def _render(self):
        html, _ = self.env["ir.actions.report"]._render_qweb_html(
            "l10n_ro_picking_report.action_report_delivery", self.picking.ids
        )
        return html.decode() if isinstance(html, bytes | bytearray) else str(html)

    def test_expiration_date_shown_with_group(self):
        self.env.user.group_ids += self.env.ref("product_expiry.group_expiry_date_on_delivery_slip")
        self.assertEqual(self.picking.move_line_ids.lot_id, self.lot)
        html = self._render()
        self.assertIn("Expiration Date", html)
        self.assertIn("03/17/2031", html)

    def test_expiration_date_hidden_without_group(self):
        self.env.user.group_ids -= self.env.ref("product_expiry.group_expiry_date_on_delivery_slip")
        html = self._render()
        self.assertNotIn("Expiration Date", html)
        self.assertNotIn("03/17/2031", html)
