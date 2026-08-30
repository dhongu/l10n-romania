# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
from unittest.mock import patch

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.l10n_ro_edi_stock.models.stock_picking import Picking as CorePicking


@tagged("post_install", "-at_install")
class TestETransportUitIsNotTrackingRef(TransactionCase):
    """UIT-ul rămâne în documentul eTransport; referința curierului nu e atinsă."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        # Starea eTransport se calculează doar pentru companii cu țara fiscală RO.
        romania = cls.env.ref("base.ro")
        cls.company.write({"country_id": romania.id, "account_fiscal_country_id": romania.id})
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.company.id)], limit=1)
        cls.partner = cls.env["res.partner"].create({"name": "Partner UIT"})

    def _create_validated_picking(self, tracking_ref):
        picking_type = self.env["stock.picking.type"].search(
            [("code", "=", "outgoing"), ("warehouse_id", "=", self.warehouse.id)],
            limit=1,
        )
        return self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "partner_id": self.partner.id,
                "location_id": picking_type.default_location_src_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id,
                "carrier_tracking_ref": tracking_ref,
                "l10n_ro_edi_stock_document_ids": [
                    (0, 0, {"state": "stock_validated", "l10n_ro_edi_stock_uit": "3Y5J439586740194"}),
                ],
            }
        )

    def test_fetch_status_keeps_courier_tracking_ref(self):
        """UIT-ul validat nu suprascrie AWB-ul curierului și nu umple o referință goală."""
        if "carrier_tracking_ref" not in self.env["stock.picking"]._fields:
            self.skipTest("stock_delivery is not installed")

        with_awb = self._create_validated_picking("AWB-123456")
        without_awb = self._create_validated_picking(False)
        self.assertEqual(with_awb.l10n_ro_edi_stock_state, "stock_validated")
        self.assertEqual(with_awb.l10n_ro_edi_stock_document_uit, "3Y5J439586740194")

        # Starea vine de la ANAF; aici nu interesează transportul, doar efectul local.
        with patch.object(CorePicking, "action_l10n_ro_edi_stock_fetch_status", return_value=True):
            (with_awb | without_awb).action_l10n_ro_edi_stock_fetch_status()

        self.assertEqual(with_awb.carrier_tracking_ref, "AWB-123456")
        self.assertFalse(without_awb.carrier_tracking_ref)
