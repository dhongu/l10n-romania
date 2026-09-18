# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
"""Linii declarate într-o UoM secundară (cutie, bax, pungă).

Cele două defecte acoperite aici au aceeași cauză — `cantitate` e în UoM-ul de
BAZĂ al produsului, în timp ce unitatea și prețul vin de pe LINIE — și aceeași
consecință: o declarație acceptată de ANAF, dar cu conținut greșit.

Cazul real: recepție de import Inedit, 10 cutii × 13 kg de mere. Declarația a
plecat cu `cantitate="130" codUnitateMasura="C62"`, adică „130 de bucăți", și a
primit UIT. XSD-ul ANAF validează fiecare atribut izolat, deci nu prinde
incoerența dintre ele.

Testele mimează ieșirea standardului reproducând sursele lui reale (liniile
826-827 din `l10n_ro_edi_stock/models/stock_picking.py`), ca să nu devină
tautologice: `cantitate` din `move.product_qty`, `codUnitateMasura` din
`move.product_uom`.
"""

from unittest import SkipTest
from unittest.mock import patch

from odoo import Command, fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

NATIVE_PATCH = "odoo.addons.l10n_ro_edi_stock.models.stock_picking.Picking._l10n_ro_edi_stock_get_template_data"


class SecondaryUomCommon(TransactionCase):
    """Produs ținut în kg, cu o cutie de 13 kg ca unitate secundară."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.env.company.id)], limit=1)
        cls.partner = cls.env["res.partner"].create({"name": "Partener UoM", "country_id": cls.env.ref("base.ro").id})
        cls.kg = cls.env.ref("uom.product_uom_kgm")
        # Unitate proprie, ca cele din `terrabit_inedit`: nu are XML ID în lista
        # fixă a lui `_get_unece_code()`, deci se mapează pe fallback-ul `C62`.
        cls.box = cls.env["uom.uom"].create(
            {"name": "Cutie 13 kg", "relative_uom_id": cls.kg.id, "relative_factor": 13}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Mere", "type": "consu", "uom_id": cls.kg.id, "uom_ids": [Command.link(cls.box.id)], "weight": 1.0}
        )

    def _native_template_data(self, move):
        """Reproduce exact ce produce `l10n_ro_edi_stock` pentru o mișcare."""
        return {
            "data": {
                "notificare": {
                    "bunuriTransportate": [
                        {
                            "denumireMarfa": move.product_id.name,
                            "cantitate": move.product_qty,
                            "codUnitateMasura": move.product_uom._get_unece_code(),
                            "valoareLeiFaraTva": move.product_id.standard_price,
                            "greutateNeta": move.product_qty,
                            "greutateBruta": move.product_qty,
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

    def _declare(self, picking):
        move = picking.move_ids
        with patch(NATIVE_PATCH, return_value=self._native_template_data(move)):
            res = picking._l10n_ro_edi_stock_get_template_data(
                {"transport_partner_id": self.partner, "stock_move_ids": move}
            )
        return res["data"]["notificare"]["bunuriTransportate"][0]


@tagged("post_install", "-at_install")
class TestSecondaryUomUnitCode(SecondaryUomCommon):
    """Fixul A — `codUnitateMasura` urmează unitatea cantității."""

    def _picking_with_move(self, uom, qty):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.out_type_id.id,
                "partner_id": self.partner.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )
        self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "product_uom_qty": qty,
                "product_uom": uom.id,
                "picking_id": picking.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
            }
        )
        return picking

    def test_core_would_declare_kilograms_as_pieces(self):
        """Fără fix, 10 cutii × 13 kg pleacă drept „130 bucăți" — cazul Inedit."""
        picking = self._picking_with_move(self.box, 10)
        move = picking.move_ids
        self.assertEqual(move.product_qty, 130, "cantitatea nativă e în UoM-ul de bază al produsului")
        self.assertEqual(
            move.product_uom._get_unece_code(),
            "C62",
            "o unitate proprie nu are mapare UNECE și cade tăcut pe bucată",
        )

    def test_unit_code_follows_product_uom_not_line_uom(self):
        """Linia e în cutii, cantitatea în kg: codul declarat trebuie să fie KGM."""
        item = self._declare(self._picking_with_move(self.box, 10))
        self.assertEqual(item["cantitate"], 130)
        self.assertEqual(item["codUnitateMasura"], "KGM")

    def test_unit_code_unchanged_when_line_uom_equals_product_uom(self):
        """Fără UoM secundară nu se schimbă nimic — cazul majorității clienților."""
        item = self._declare(self._picking_with_move(self.kg, 130))
        self.assertEqual(item["cantitate"], 130)
        self.assertEqual(item["codUnitateMasura"], "KGM")

    def test_alignment_skipped_when_lines_do_not_match_moves(self):
        """Cu linii și mișcări nepotrivite, `zip` ar împerechea greșit: renunțăm."""
        picking = self._picking_with_move(self.box, 10)
        move = picking.move_ids
        native = self._native_template_data(move)
        native["data"]["notificare"]["bunuriTransportate"].append(
            dict(native["data"]["notificare"]["bunuriTransportate"][0])
        )
        with patch(NATIVE_PATCH, return_value=native):
            res = picking._l10n_ro_edi_stock_get_template_data(
                {"transport_partner_id": self.partner, "stock_move_ids": move}
            )
        for item in res["data"]["notificare"]["bunuriTransportate"]:
            self.assertEqual(item["codUnitateMasura"], "C62", "codurile rămân cele generate de standard")


@tagged("post_install", "-at_install")
class TestSecondaryUomOrderPrice(SecondaryUomCommon):
    """Fixul E — prețul din comandă se convertește în UoM-ul de bază.

    `valoareLeiFaraTva` e valoarea liniei, obținută prin `preț unitar × cantitate`,
    iar cantitatea e în kg. Prețul de pe comandă e per cutie, deci fără conversie
    valoarea declarată iese de 13 ori mai mare.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.l10n_ro_etransport_get_order_value = True

    def test_purchase_price_converted_to_product_uom(self):
        """Recepție: 10 cutii a 130 lei = 1.300 lei, nu 16.900."""
        if "purchase.order" not in self.env:
            raise SkipTest("Install purchase to run the reception price test.")
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_qty": 10,
                            "product_uom_id": self.box.id,
                            "price_unit": 130,
                        }
                    )
                ],
            }
        )
        order.button_confirm()
        picking = order.picking_ids
        self.assertTrue(picking, "confirmarea comenzii trebuie să genereze recepția")
        item = self._declare(picking)
        self.assertEqual(item["cantitate"], 130, "cantitatea declarată e în kg")
        self.assertAlmostEqual(item["valoareLeiFaraTva"], 1300.0, places=2)

    def test_sale_price_converted_to_product_uom(self):
        """Livrare: 10 cutii a 130 lei = 1.300 lei, nu 16.900."""
        if "sale.order" not in self.env:
            raise SkipTest("Install sale_stock to run the delivery price test.")
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 10,
                            "product_uom_id": self.box.id,
                            "price_unit": 130,
                        }
                    )
                ],
            }
        )
        order.action_confirm()
        picking = order.picking_ids
        self.assertTrue(picking, "confirmarea comenzii trebuie să genereze livrarea")
        item = self._declare(picking)
        self.assertEqual(item["cantitate"], 130)
        self.assertAlmostEqual(item["valoareLeiFaraTva"], 1300.0, places=2)

    def test_price_unchanged_when_line_uom_equals_product_uom(self):
        """Fără UoM secundară, conversia e neutră — nicio schimbare de valoare."""
        if "purchase.order" not in self.env:
            raise SkipTest("Install purchase to run the reception price test.")
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_qty": 130,
                            "product_uom_id": self.kg.id,
                            "price_unit": 10,
                        }
                    )
                ],
            }
        )
        order.button_confirm()
        item = self._declare(order.picking_ids)
        self.assertEqual(item["cantitate"], 130)
        self.assertAlmostEqual(item["valoareLeiFaraTva"], 1300.0, places=2)
