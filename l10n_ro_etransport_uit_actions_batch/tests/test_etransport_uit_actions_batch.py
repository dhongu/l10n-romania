# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
"""Evenimentele UIT pe LOT: aceeași mecanică ca pe transfer, dar părintele e lotul."""

import base64
from unittest.mock import patch

from lxml import etree

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.l10n_ro_etransport_uit_actions.models.etransport_api_actions import ETransportActionsAPI

NS = "mfp:anaf:dgti:eTransport:declaratie:v2"
UPLOAD_OK = {"content": {"index_incarcare": "6001", "dateResponse": "202609101200"}}


@tagged("post_install", "-at_install")
class TestEtransportUitActionsBatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.write(
            {
                "vat": "RO1234567897",
                "country_id": cls.env.ref("base.ro").id,
                "account_fiscal_country_id": cls.env.ref("base.ro").id,
                "l10n_ro_edi_access_token": "test-token",
                "l10n_ro_edi_test_env": True,
            }
        )
        warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.company.id)], limit=1)
        partner = cls.env["res.partner"].create({"name": "Client lot UIT", "country_id": cls.env.ref("base.ro").id})
        product = cls.env["product.product"].create({"name": "Marfă lot UIT", "type": "consu", "weight": 1.0})
        picking = cls.env["stock.picking"].create(
            {
                "partner_id": partner.id,
                "picking_type_id": warehouse.out_type_id.id,
                "location_id": warehouse.lot_stock_id.id,
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 5,
                            "location_id": warehouse.lot_stock_id.id,
                            "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
                        },
                    )
                ],
            }
        )
        cls.batch = cls.env["stock.picking.batch"].create(
            {"picking_ids": [(4, picking.id)], "l10n_ro_edi_stock_vehicle_number": "B99LOT"}
        )
        cls.env["l10n_ro_edi.document"].create(
            {
                "batch_id": cls.batch.id,
                "state": "stock_validated",
                "l10n_ro_edi_stock_uit": "3000000000000777",
                "l10n_ro_edi_stock_load_id": "4777",
                "attachment": base64.b64encode(b"<eTransport/>"),
            }
        )
        cls.batch.invalidate_recordset()

    def _wizard(self, event_type, **values):
        return self.env["l10n.ro.etransport.action.wizard"].create(
            {"batch_id": self.batch.id, "event_type": event_type, **values}
        )

    def test_event_needs_a_parent(self):
        with self.assertRaises(ValidationError):
            self.env["l10n.ro.etransport.event"].create({"event_type": "DEL", "uit": "3000000000000777"})

    def test_delete_on_batch(self):
        self.assertTrue(self.batch.l10n_ro_etransport_enable_actions)
        with patch.object(ETransportActionsAPI, "upload_data", return_value=UPLOAD_OK):
            self._wizard("DEL").action_send()
        event = self.batch.l10n_ro_etransport_event_ids
        self.assertEqual(len(event), 1)
        self.assertFalse(event.picking_id)
        self.assertEqual(event.company_id, self.company)
        root = etree.fromstring(base64.b64decode(event.attachment))
        self.assertEqual(root.get("refDeclarant"), self.batch.name)
        self.assertEqual(root.find(f"{{{NS}}}stergere").get("uit"), "3000000000000777")
        self.assertFalse(self.batch.l10n_ro_etransport_enable_actions)

        with patch.object(ETransportActionsAPI, "get_status", return_value={"content": {"stare": "ok"}}):
            self.batch.action_l10n_ro_etransport_fetch_event_status()
        self.assertEqual(event.state, "validated")
        self.assertTrue(self.batch.l10n_ro_etransport_uit_deleted)
        self.assertEqual(self.batch.l10n_ro_edi_stock_state, "stock_validated")
        # chatter-ul lotului, nu al transferului
        self.assertTrue(self.batch.message_ids.filtered(lambda m: "3000000000000777" in (m.body or "")))

    def test_modify_vehicle_on_batch_after_validation(self):
        with patch.object(ETransportActionsAPI, "upload_data", return_value=UPLOAD_OK):
            self._wizard("MVH", vehicle_number="CJ77LOT").action_send()
        event = self.batch.l10n_ro_etransport_event_ids
        self.assertEqual(self.batch.l10n_ro_edi_stock_vehicle_number, "B99LOT")
        with patch.object(ETransportActionsAPI, "get_status", return_value={"content": {"stare": "ok"}}):
            event.action_fetch_status()
        self.assertEqual(self.batch.l10n_ro_edi_stock_vehicle_number, "CJ77LOT")
