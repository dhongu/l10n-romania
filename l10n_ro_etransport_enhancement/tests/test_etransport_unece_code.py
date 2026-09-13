# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
"""De unde ia declarația codul unității de măsură.

Codul trimis în `codUnitateMasura` vine din `uom.uom._get_unece_code()`. Metoda
din standard mapează unitatea exclusiv prin XML ID, dintr-o listă fixă de 28 de
intrări, și întoarce `C62` — o bucată — pentru orice altceva, fără să ridice
eroare. Orice unitate creată de client cade acolo.

`deltatech_uom_unece` (suita deltatech) suprascrie metoda cu un cod configurabil
pe fiecare unitate. Testele de aici verifică faptul care nu e evident din niciun
fișier al acestui modul: că declarația **chiar** trece prin acel cod, și că
unitatea din care îl ia e cea a PRODUSULUI, nu cea a liniei.

Modulul nu depinde de `deltatech_uom_unece` — e o suită separată, cu altă
licență. Testele se sar când nu e instalat.
"""

from unittest import SkipTest
from unittest.mock import patch

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

NATIVE_PATCH = "odoo.addons.l10n_ro_edi_stock.models.stock_picking.Picking._l10n_ro_edi_stock_get_template_data"


@tagged("post_install", "-at_install")
class TestEtransportUneceCode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if "unece_code_id" not in cls.env["uom.uom"]._fields:
            raise SkipTest("Install deltatech_uom_unece to run the configurable unit code tests.")
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.env.company.id)], limit=1)
        cls.partner = cls.env["res.partner"].create({"name": "Partener UM", "country_id": cls.env.ref("base.ro").id})
        cls.kg = cls.env.ref("uom.product_uom_kgm")
        cls.carton = cls.env["uom.unece.code"].search([("code", "=", "XCT")], limit=1)
        if not cls.carton:
            raise SkipTest("The UNECE nomenclature does not carry XCT on this database.")
        # Unitate proprie, ca „Cutie 13 kg" de la Inedit: fără codul configurat
        # ar cădea pe `C62`, fiindcă nu are cum să figureze în lista standard.
        cls.box = cls.env["uom.uom"].create(
            {
                "name": "Cutie 13 kg",
                "relative_uom_id": cls.kg.id,
                "relative_factor": 13,
                "unece_code_id": cls.carton.id,
            }
        )

    def _declare(self, product, uom, qty):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.in_type_id.id,
                "partner_id": self.partner.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.warehouse.lot_stock_id.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "product_id": product.id,
                "product_uom_qty": qty,
                "product_uom": uom.id,
                "picking_id": picking.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
            }
        )
        native = {
            "data": {
                "notificare": {
                    "bunuriTransportate": [
                        {
                            "denumireMarfa": product.name,
                            "cantitate": move.product_qty,
                            "codUnitateMasura": move.product_uom._get_unece_code(),
                            "valoareLeiFaraTva": product.standard_price or 1.0,
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
        with patch(NATIVE_PATCH, return_value=native):
            res = picking._l10n_ro_edi_stock_get_template_data(
                {"transport_partner_id": self.partner, "stock_move_ids": move}
            )
        return res["data"]["notificare"]["bunuriTransportate"][0]

    def _product(self, uom):
        return self.env["product.product"].create(
            {
                "name": "Mere",
                "type": "consu",
                "uom_id": uom.id,
                "uom_ids": [(4, self.box.id)] if uom == self.kg else False,
                "weight": 1.0,
                "standard_price": 3.0,
            }
        )

    def test_configured_code_is_used_when_the_product_is_kept_in_that_unit(self):
        """Produs ținut în cutii: declarația ia codul configurat, nu `C62`."""
        item = self._declare(self._product(self.box), self.box, 10)
        self.assertEqual(item["cantitate"], 10)
        self.assertEqual(item["codUnitateMasura"], "XCT")

    def test_code_follows_the_product_unit_not_the_line_unit(self):
        """Cazul Inedit: produsul e în kg, linia în cutii.

        Declarația trebuie să spună „130 KGM", nu „130 XCT": `cantitate` e
        `move.product_qty`, exprimat în unitatea de bază a produsului. Codul de
        pe cutie e corect configurat și rămâne deliberat nefolosit aici — altfel
        declarația ar susține că se transportă 130 de cutii.
        """
        product = self._product(self.kg)
        self.assertEqual(self.box._get_unece_code(), "XCT", "cutia chiar are codul configurat")
        item = self._declare(product, self.box, 10)
        self.assertEqual(item["cantitate"], 130)
        self.assertEqual(item["codUnitateMasura"], "KGM")

    def test_unit_without_configured_code_keeps_the_core_mapping(self):
        """Kilogramul n-are codul completat și nici nu-i trebuie: standardul îl
        mapează corect, iar override-ul cade pe el."""
        self.assertFalse(self.kg.unece_code_id)
        item = self._declare(self._product(self.kg), self.kg, 130)
        self.assertEqual(item["codUnitateMasura"], "KGM")

    def test_custom_unit_without_code_still_falls_back_to_pieces(self):
        """Fără cod configurat, o unitate proprie rămâne `C62` — comportamentul
        pe care modulul de coduri există ca să-l repare."""
        crate = self.env["uom.uom"].create(
            {"name": "Ladă fără cod", "relative_uom_id": self.kg.id, "relative_factor": 20}
        )
        item = self._declare(self._product(crate), crate, 5)
        self.assertEqual(item["codUnitateMasura"], "C62")
