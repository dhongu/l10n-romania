# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestStockPickingFields(TransactionCase):
    """Testează câmpurile noi adăugate pe stock.picking."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.company.id)], limit=1)
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
        config = self.env["res.config.settings"].create({"l10n_ro_etransport_get_order_value": True})
        config.execute()
        self.assertTrue(self.env.company.l10n_ro_etransport_get_order_value)


@tagged("post_install", "-at_install")
class TestStockPickingWeightLine(TransactionCase):
    """Testează modelul l10n.ro.stock.picking.weight.line."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.company.id)], limit=1)
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
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.company.id)], limit=1)
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
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.company.id)], limit=1)
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

    def _picking_with_quantity(self, qty=2.0):
        """Transfer confirmat, cu cantitate pe mișcare — altfel nu se creează linii."""
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
        return picking

    def test_compute_weight_lines_creates_one_line_per_move(self):
        """O apăsare pe „Get lines" dă o linie pe mișcare, cu greutatea produsului."""
        picking = self._picking_with_quantity(qty=2.0)
        picking.l10n_ro_compute_weight_lines()
        self.assertEqual(len(picking.l10n_ro_shipping_weight_lines), 1)
        self.assertEqual(picking.l10n_ro_shipping_weight_lines.gross_weight, 6.0)  # 3 kg * 2

    def test_recompute_replaces_lines_instead_of_adding(self):
        """A doua apăsare recalculează; fără unlink greutățile ajungeau dublate."""
        picking = self._picking_with_quantity(qty=2.0)
        picking.l10n_ro_compute_weight_lines()
        picking.l10n_ro_compute_weight_lines()
        self.assertEqual(len(picking.l10n_ro_shipping_weight_lines), 1)
        self.assertEqual(picking.l10n_ro_shipping_weight_lines.gross_weight, 6.0)

    def test_recompute_picks_up_the_new_quantity(self):
        """Recalcularea reflectă cantitatea curentă, nu pe cea de la prima apăsare."""
        picking = self._picking_with_quantity(qty=2.0)
        picking.l10n_ro_compute_weight_lines()
        picking.move_ids.quantity = 5.0
        picking.l10n_ro_compute_weight_lines()
        self.assertEqual(len(picking.l10n_ro_shipping_weight_lines), 1)
        self.assertEqual(picking.l10n_ro_shipping_weight_lines.gross_weight, 15.0)  # 3 kg * 5


@tagged("post_install", "-at_install")
class TestTemplateDataTimezone(TransactionCase):
    """Data transportului când utilizatorul care trimite nu are fus orar setat.

    `pytz.timezone(False)` aruncă AttributeError, deci o trimitere din cron (OdooBot
    nu are `tz`) cădea cu traceback în loc să genereze declarația.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.env.company.id)], limit=1)
        cls.transport_partner = cls.env["res.partner"].create(
            {"name": "Transportator TZ", "country_id": cls.env.ref("base.ro").id}
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.warehouse.out_type_id.id,
                "partner_id": cls.transport_partner.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
                # 22:30 UTC devine ziua următoare la ora României; o dată din viitor,
                # altfel override-ul o înlocuiește cu ziua curentă
                "scheduled_date": "2027-07-20 22:30:00",
            }
        )

    def _native_template_data(self):
        """Scheletul pe care îl întoarce standardul, cât să treacă override-ul."""
        return {
            "data": {
                "notificare": {
                    "bunuriTransportate": [],
                    "partenerComercial": {"codTara": "RO"},
                    "dateTransport": {"dataTransport": fields.Date.to_date("2027-07-20")},
                    "locStartTraseuRutier": {},
                    "locFinalTraseuRutier": {},
                    "documenteTransport": {
                        "tipDocument": "30",
                        "dataDocument": fields.Date.to_date("2027-07-20"),
                        "numarDocument": "AVZ-1",
                        "observatii": "",
                    },
                }
            }
        }

    def _get_template_data(self):
        patch_path = "odoo.addons.l10n_ro_edi_stock.models.stock_picking.Picking._l10n_ro_edi_stock_get_template_data"
        with patch(patch_path, return_value=self._native_template_data()):
            return self.picking._l10n_ro_edi_stock_get_template_data(
                {"transport_partner_id": self.transport_partner, "stock_move_ids": self.picking.move_ids}
            )

    def test_missing_user_timezone_falls_back_to_romania(self):
        """Fără fus orar pe utilizator, data se calculează la ora României."""
        self.env.user.tz = False
        res = self._get_template_data()
        self.assertEqual(
            res["data"]["notificare"]["dateTransport"]["dataTransport"],
            fields.Date.to_date("2027-07-21"),
        )

    def test_user_timezone_is_respected(self):
        """Când utilizatorul are fus orar, acela rămâne sursa datei."""
        self.env.user.tz = "UTC"
        res = self._get_template_data()
        self.assertEqual(
            res["data"]["notificare"]["dateTransport"]["dataTransport"],
            fields.Date.to_date("2027-07-20"),
        )


@tagged("post_install", "-at_install")
class TestFallbackPrice(TransactionCase):
    """Prețul liniilor pe care standardul le trimite cu `valoareLeiFaraTva` = 0.

    ANAF respinge declarația cu valoare 0. Când mișcarea nu are preț pe document
    (transfer intern, produs fără cost pe fișă), valoarea se caută în ordinea din
    18.0: valorizarea mișcării, costul standard, prețul de listă.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.env.company.id)], limit=1)
        cls.partner = cls.env["res.partner"].create({"name": "Partener Preț", "country_id": cls.env.ref("base.ro").id})
        cls.product = cls.env["product.product"].create(
            {"name": "Produs Fără Preț", "type": "consu", "weight": 2.0, "list_price": 0.0}
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.warehouse.out_type_id.id,
                "partner_id": cls.partner.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
            }
        )
        cls.move = cls.env["stock.move"].create(
            {
                "product_id": cls.product.id,
                "product_uom_qty": 4.0,
                "product_uom": cls.product.uom_id.id,
                "picking_id": cls.picking.id,
                "location_id": cls.picking.location_id.id,
                "location_dest_id": cls.picking.location_dest_id.id,
            }
        )
        cls.product.standard_price = 0.0

    def _native_template_data(self, value):
        return {
            "data": {
                "notificare": {
                    "bunuriTransportate": [
                        {
                            "denumireMarfa": self.product.name,
                            "cantitate": 4.0,
                            "valoareLeiFaraTva": value,
                            "greutateNeta": 8.0,
                            "greutateBruta": 8.0,
                        }
                    ],
                    "partenerComercial": {"codTara": "RO"},
                    "dateTransport": {"dataTransport": fields.Date.today()},
                    "locStartTraseuRutier": {},
                    "locFinalTraseuRutier": {},
                    "documenteTransport": {},
                }
            }
        }

    def _get_template_data(self, value=0.0):
        patch_path = "odoo.addons.l10n_ro_edi_stock.models.stock_picking.Picking._l10n_ro_edi_stock_get_template_data"
        with patch(patch_path, return_value=self._native_template_data(value)):
            return self.picking._l10n_ro_edi_stock_get_template_data(
                {"transport_partner_id": self.partner, "stock_move_ids": self.picking.move_ids}
            )

    def _patch_valuation(self, value, quantity):
        """`stock.valuation.layer` nu mai există pe stock.move în 19.0; valoarea
        vine din `_get_value_data`, care întoarce valoarea și cantitatea valorizată."""
        return patch.object(
            type(self.move),
            "_get_value_data",
            return_value={"value": value, "quantity": quantity, "description": ""},
        )

    def test_zero_value_falls_back_to_move_valuation(self):
        """Valoarea de stoc a mișcării are prioritate: 250 lei / 10 buc = 25 lei/buc."""
        with self._patch_valuation(250.0, 10.0):
            res = self._get_template_data()
        item = res["data"]["notificare"]["bunuriTransportate"][0]
        self.assertEqual(item["valoareLeiFaraTva"], 100.0)  # 25 * 4

    def test_zero_value_falls_back_to_standard_price(self):
        """Fără cantitate valorizată se trece pe costul standard."""
        self.product.standard_price = 30.0
        with self._patch_valuation(0.0, 0.0):
            res = self._get_template_data()
        item = res["data"]["notificare"]["bunuriTransportate"][0]
        self.assertEqual(item["valoareLeiFaraTva"], 120.0)  # 30 * 4

    def test_zero_value_falls_back_to_list_price(self):
        """Fără cost standard rămâne prețul de listă."""
        self.product.list_price = 12.5
        with self._patch_valuation(0.0, 0.0):
            res = self._get_template_data()
        item = res["data"]["notificare"]["bunuriTransportate"][0]
        self.assertEqual(item["valoareLeiFaraTva"], 50.0)  # 12.5 * 4

    def test_no_price_anywhere_raises(self):
        """Fără niciun preț, trimiterea se oprește explicit în loc să plece cu 0 la ANAF."""
        with self._patch_valuation(0.0, 0.0), self.assertRaises(UserError):
            self._get_template_data()

    def test_non_zero_value_is_left_alone(self):
        """O valoare deja completată de standard nu e rescrisă."""
        self.product.standard_price = 99.0
        res = self._get_template_data(value=7.0)
        item = res["data"]["notificare"]["bunuriTransportate"][0]
        self.assertEqual(item["valoareLeiFaraTva"], 28.0)  # 7 * 4, nu 99


@tagged("post_install", "-at_install")
class TestQuantitiesAndWeights(TransactionCase):
    """Cantitatea 0 și greutățile lipsă pe `bunuriTransportate`.

    Șablonul QWeb randează `cantitate`, `greutateNeta` și `greutateBruta` prin
    `t-att-*`, care scapă tăcut o valoare falsy, iar XSD-ul ANAF le cere pe toate
    trei: un 0 nu lipsește doar din declarație, o invalidează.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.env.company.id)], limit=1)
        cls.partner = cls.env["res.partner"].create(
            {"name": "Partener Cantități", "country_id": cls.env.ref("base.ro").id}
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.warehouse.out_type_id.id,
                "partner_id": cls.partner.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
            }
        )

    def _item(self, cantitate=1.0, neta=1.0, bruta=1.0, name="Marfă"):
        return {
            "denumireMarfa": name,
            "cantitate": cantitate,
            "greutateNeta": neta,
            "greutateBruta": bruta,
        }

    def _fix(self, items):
        self.env["stock.picking"]._l10n_ro_etransport_fix_quantities_and_weights(items)
        return items

    def test_zero_quantity_line_is_removed(self):
        """O linie fără cantitate nu are ce căuta în declarație."""
        items = self._fix([self._item(cantitate=0.0), self._item(cantitate=3.0, name="Rămâne")])
        self.assertEqual([item["denumireMarfa"] for item in items], ["Rămâne"])

    def test_all_lines_can_be_removed(self):
        """Dacă toate liniile sunt fără cantitate, lista rămâne goală (nu crapă)."""
        self.assertEqual(self._fix([self._item(cantitate=0.0)]), [])

    def test_zero_gross_weight_falls_back_to_net(self):
        """Greutatea brută lipsă se aproximează cu cea netă."""
        items = self._fix([self._item(neta=12.5, bruta=0.0)])
        self.assertEqual(items[0]["greutateBruta"], 12.5)
        self.assertEqual(items[0]["greutateNeta"], 12.5)

    def test_zero_net_weight_falls_back_to_gross(self):
        """Și invers: greutatea netă lipsă se aproximează cu cea brută."""
        items = self._fix([self._item(neta=0.0, bruta=8.0)])
        self.assertEqual(items[0]["greutateNeta"], 8.0)
        self.assertEqual(items[0]["greutateBruta"], 8.0)

    def test_both_weights_zero_are_left_alone(self):
        """Fără nicio greutate cunoscută nu se poate deduce nimic."""
        items = self._fix([self._item(neta=0.0, bruta=0.0)])
        self.assertEqual((items[0]["greutateNeta"], items[0]["greutateBruta"]), (0.0, 0.0))

    def test_complete_line_is_untouched(self):
        """O linie completă rămâne exact cum e."""
        items = self._fix([self._item(cantitate=2.0, neta=3.0, bruta=4.0)])
        self.assertEqual((items[0]["cantitate"], items[0]["greutateNeta"], items[0]["greutateBruta"]), (2.0, 3.0, 4.0))

    def test_applied_when_building_the_declaration(self):
        """Curățarea chiar rulează pe declarația generată, nu doar izolat."""
        native = {
            "data": {
                "notificare": {
                    "bunuriTransportate": [
                        dict(self._item(cantitate=0.0, name="Fără cantitate"), valoareLeiFaraTva=5.0),
                        dict(self._item(cantitate=2.0, neta=6.0, bruta=0.0, name="Rămâne"), valoareLeiFaraTva=5.0),
                    ],
                    "partenerComercial": {"codTara": "RO"},
                    "dateTransport": {"dataTransport": fields.Date.today()},
                    "locStartTraseuRutier": {},
                    "locFinalTraseuRutier": {},
                    "documenteTransport": {},
                }
            }
        }
        patch_path = "odoo.addons.l10n_ro_edi_stock.models.stock_picking.Picking._l10n_ro_edi_stock_get_template_data"
        with patch(patch_path, return_value=native):
            res = self.picking._l10n_ro_edi_stock_get_template_data(
                {"transport_partner_id": self.partner, "stock_move_ids": self.picking.move_ids}
            )
        items = res["data"]["notificare"]["bunuriTransportate"]
        self.assertEqual([item["denumireMarfa"] for item in items], ["Rămâne"])
        self.assertEqual(items[0]["greutateBruta"], 6.0)
