# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestBatchWeightLinesWarning(TransactionCase):
    """Avertismentul pentru mișcările lotului fără linie de greutate.

    Fără el, operatorul vede o listă de greutăți plauzibilă și trimite declarația
    cu greutățile incomplete: mișcările lipsă nu apar nicăieri.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.env.company.id)], limit=1)
        cls.product = cls.env["product.product"].create({"name": "Produs Lot Greutăți", "type": "consu", "weight": 4.0})
        cls.partner = cls.env["res.partner"].create({"name": "Partener Lot"})

    def _batch_with_quantity(self, qty=3.0):
        picking_type = self.env["stock.picking.type"].search(
            [("code", "=", "outgoing"), ("warehouse_id", "=", self.warehouse.id)],
            limit=1,
        )
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "partner_id": self.partner.id,
                "location_id": picking_type.default_location_src_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": qty,
                            "product_uom": self.product.uom_id.id,
                            "location_id": picking_type.default_location_src_id.id,
                            "location_dest_id": picking_type.default_location_dest_id.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.move_ids.quantity = qty
        return self.env["stock.picking.batch"].create({"picking_ids": [(4, picking.id)]})

    def test_warning_when_a_move_has_no_weight_line(self):
        """Mișcările lotului fără linie de greutate sunt semnalate."""
        batch = self._batch_with_quantity()
        batch.l10n_ro_shipping_weights = True
        self.assertIn("1 of 1", batch.l10n_ro_shipping_weight_lines_warning)

    def test_warning_clears_after_computing_the_lines(self):
        """După „Get lines" avertismentul dispare; lotul deleagă la transferuri."""
        batch = self._batch_with_quantity()
        batch.l10n_ro_shipping_weights = True
        batch.l10n_ro_compute_weight_lines()
        self.assertFalse(batch.l10n_ro_shipping_weight_lines_warning)

    def test_no_warning_when_custom_weights_are_off(self):
        """Fără greutăți proprii, avertismentul nu are sens."""
        batch = self._batch_with_quantity()
        batch.l10n_ro_shipping_weights = False
        self.assertFalse(batch.l10n_ro_shipping_weight_lines_warning)
