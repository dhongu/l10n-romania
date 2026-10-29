# ©  2026 Terrabit
# See README.rst file on addons root folder for license details
"""Transportatorul și metoda de livrare ale lotului vin din transferurile LUI."""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestBatchCarrier(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.env.company.id)], limit=1)
        cls.picking_type = warehouse.out_type_id
        service = cls.env["product.product"].create({"name": "Transport lot", "type": "service"})
        cls.carrier_a, cls.carrier_b = cls.env["delivery.carrier"].create(
            [
                {"name": "Curier A", "product_id": service.id},
                {"name": "Curier B", "product_id": service.id},
            ]
        )
        cls.transporter = cls.env["res.partner"].create({"name": "Transportator Lot"})

    def _batch(self, carrier, transporter=None):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type.id,
                "carrier_id": carrier.id,
                "l10n_ro_transport_partner_id": transporter and transporter.id,
            }
        )
        return self.env["stock.picking.batch"].create({"picking_ids": [(4, picking.id)]})

    def test_each_batch_gets_its_own_carrier(self):
        """Pe o selecție de loturi, fiecare primește metoda transferurilor lui."""
        batches = self._batch(self.carrier_a) | self._batch(self.carrier_b)
        batches.invalidate_recordset(["l10n_ro_edi_carrier_id"])
        self.assertEqual(batches.mapped("l10n_ro_edi_carrier_id"), self.carrier_a | self.carrier_b)
        self.assertEqual(batches[1].l10n_ro_edi_carrier_id, self.carrier_b)

    def test_transport_partner_cleared_without_pickings(self):
        """Fără transferuri, transportatorul lotului nu mai păstrează valoarea veche."""
        batch = self._batch(self.carrier_a, self.transporter)
        self.assertEqual(batch.l10n_ro_transport_partner_id, self.transporter)
        batch.picking_ids = [(5, 0, 0)]
        self.assertFalse(batch.l10n_ro_transport_partner_id)
