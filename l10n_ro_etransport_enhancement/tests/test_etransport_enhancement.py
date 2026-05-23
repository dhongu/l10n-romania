# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
from unittest.mock import patch

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestStockPickingFields(TransactionCase):
    """Testează câmpurile noi adăugate pe stock.picking."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Produs Test eTransport",
                "type": "consu",
                "weight": 1.5,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Partner Test",
                "country_id": cls.env.ref("base.ro").id,
            }
        )

    def _create_picking(self):
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
            }
        )
        return picking

    def test_l10n_ro_edi_stock_required_default_false(self):
        """Câmpul l10n_ro_edi_stock_required este False implicit."""
        picking = self._create_picking()
        self.assertFalse(picking.l10n_ro_edi_stock_required)

    def test_l10n_ro_edi_stock_required_can_be_set(self):
        """Câmpul l10n_ro_edi_stock_required poate fi setat la True."""
        picking = self._create_picking()
        picking.l10n_ro_edi_stock_required = True
        self.assertTrue(picking.l10n_ro_edi_stock_required)

    def test_l10n_ro_shipping_weights_default_false(self):
        """Câmpul l10n_ro_shipping_weights este False implicit."""
        picking = self._create_picking()
        self.assertFalse(picking.l10n_ro_shipping_weights)

    def test_l10n_ro_shipping_weight_lines_empty(self):
        """l10n_ro_shipping_weight_lines este gol la creare."""
        picking = self._create_picking()
        self.assertEqual(len(picking.l10n_ro_shipping_weight_lines), 0)


@tagged("post_install", "-at_install")
class TestResConfigSettings(TransactionCase):
    """Testează câmpul de configurare l10n_ro_etransport_get_order_value."""

    def test_company_field_default_false(self):
        """l10n_ro_etransport_get_order_value este False implicit pe companie."""
        self.assertFalse(self.env.company.l10n_ro_etransport_get_order_value)

    def test_company_field_can_be_set(self):
        """l10n_ro_etransport_get_order_value poate fi setat la True pe companie."""
        self.env.company.l10n_ro_etransport_get_order_value = True
        self.assertTrue(self.env.company.l10n_ro_etransport_get_order_value)

    def test_config_settings_related_field(self):
        """Câmpul din res.config.settings este legat de companie."""
        self.env.company.l10n_ro_etransport_get_order_value = True
        config = self.env["res.config.settings"].create({})
        self.assertTrue(config.l10n_ro_etransport_get_order_value)

    def test_config_settings_write_propagates_to_company(self):
        """Scrierea în res.config.settings propagă valoarea la companie."""
        self.env.company.l10n_ro_etransport_get_order_value = False
        config = self.env["res.config.settings"].create(
            {"l10n_ro_etransport_get_order_value": True}
        )
        config.execute()
        self.assertTrue(self.env.company.l10n_ro_etransport_get_order_value)


@tagged("post_install", "-at_install")
class TestStockPickingWeightLine(TransactionCase):
    """Testează modelul l10n.ro.stock.picking.weight.line."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Produs Greutate",
                "type": "consu",
                "weight": 2.0,
            }
        )
        # set net weight if field exists
        if hasattr(cls.product, "l10n_ro_net_weight"):
            cls.product.l10n_ro_net_weight = 1.8
        cls.partner = cls.env["res.partner"].create({"name": "Partner Greutate"})

    def _create_picking_with_move(self):
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
                            "product_uom_qty": 3.0,
                            "product_uom": self.product.uom_id.id,
                            "location_id": picking_type.default_location_src_id.id,
                            "location_dest_id": picking_type.default_location_dest_id.id,
                        },
                    )
                ],
            }
        )
        return picking

    def test_weight_line_create(self):
        """Linia de greutate poate fi creată manual."""
        picking = self._create_picking_with_move()
        move = picking.move_ids[0]
        weight_line = self.env["l10n.ro.stock.picking.weight.line"].create(
            {
                "picking_id": picking.id,
                "move_id": move.id,
                "net_weight": 5.4,
                "gross_weight": 6.0,
            }
        )
        self.assertEqual(weight_line.picking_id, picking)
        self.assertEqual(weight_line.move_id, move)
        self.assertAlmostEqual(weight_line.net_weight, 5.4)
        self.assertAlmostEqual(weight_line.gross_weight, 6.0)

    def test_weight_line_fields(self):
        """Câmpurile modelului l10n.ro.stock.picking.weight.line sunt corecte."""
        picking = self._create_picking_with_move()
        move = picking.move_ids[0]
        weight_line = self.env["l10n.ro.stock.picking.weight.line"].create(
            {
                "picking_id": picking.id,
                "move_id": move.id,
                "net_weight": 1.0,
                "gross_weight": 1.2,
            }
        )
        self.assertTrue(weight_line.id)
        self.assertEqual(weight_line._name, "l10n.ro.stock.picking.weight.line")


@tagged("post_install", "-at_install")
class TestValidateDataNoWeight(TransactionCase):
    """Testează _l10n_ro_edi_stock_validate_data pentru produse fără greutate."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )
        cls.product_no_weight = cls.env["product.product"].create(
            {
                "name": "Produs Fara Greutate",
                "type": "consu",
                "weight": 0.0,
            }
        )
        cls.product_with_weight = cls.env["product.product"].create(
            {
                "name": "Produs Cu Greutate",
                "type": "consu",
                "weight": 1.5,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner Validare"})

    def _create_picking_with_product(self, product):
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
                            "product_id": product.id,
                            "product_uom_qty": 1.0,
                            "product_uom": product.uom_id.id,
                            "location_id": picking_type.default_location_src_id.id,
                            "location_dest_id": picking_type.default_location_dest_id.id,
                        },
                    )
                ],
            }
        )
        return picking

    def test_validate_data_no_weight_adds_error(self):
        """_l10n_ro_edi_stock_validate_data adaugă eroare pentru produse fără greutate."""
        picking = self._create_picking_with_product(self.product_no_weight)
        move = picking.move_ids[0]
        data = {"stock_move_ids": move}
        patch_path = "odoo.addons.l10n_ro_edi_stock.models.stock_picking.Picking._l10n_ro_edi_stock_validate_data"
        with patch(patch_path, return_value=[]):
            errors = picking._l10n_ro_edi_stock_validate_data(data)
        # Trebuie să existe cel puțin o eroare despre greutate
        weight_errors = [e for e in errors if self.product_no_weight.display_name in e]
        self.assertTrue(len(weight_errors) > 0)

    def test_validate_data_with_weight_no_extra_error(self):
        """_l10n_ro_edi_stock_validate_data nu adaugă eroare pentru produse cu greutate."""
        picking = self._create_picking_with_product(self.product_with_weight)
        move = picking.move_ids[0]
        data = {"stock_move_ids": move}
        patch_path = "odoo.addons.l10n_ro_edi_stock.models.stock_picking.Picking._l10n_ro_edi_stock_validate_data"
        with patch(patch_path, return_value=[]):
            errors = picking._l10n_ro_edi_stock_validate_data(data)
        weight_errors = [e for e in errors if self.product_with_weight.display_name in e]
        self.assertEqual(len(weight_errors), 0)


@tagged("post_install", "-at_install")
class TestComputeWeightLines(TransactionCase):
    """Testează metoda l10n_ro_compute_weight_lines."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Produs Weight Lines",
                "type": "consu",
                "weight": 3.0,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner Weight Lines"})

    def test_compute_weight_lines_empty_when_no_quantity(self):
        """l10n_ro_compute_weight_lines nu creează linii dacă mișcările au qty 0."""
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
                            "product_uom_qty": 2.0,
                            "product_uom": self.product.uom_id.id,
                            "location_id": picking_type.default_location_src_id.id,
                            "location_dest_id": picking_type.default_location_dest_id.id,
                        },
                    )
                ],
            }
        )
        # quantity (done qty) este 0 la draft, deci nu se creează linii
        picking.l10n_ro_compute_weight_lines()
        self.assertEqual(len(picking.l10n_ro_shipping_weight_lines), 0)
