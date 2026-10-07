# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
"""XML-ul eTransport trimis efectiv: corecție, greutate brută, cod tarifar, post-avarie.

Toate cele patru defecte erau tăcute: ANAF accepta declarația, iar datele
declarate erau greșite (verificat față de XSD v2 și Schematron v2.0.2).
"""

from odoo.tests import tagged

from .common import NS, SENT_UIT, EtransportDeclarationCommon

PREVIOUS_UIT = "ACDEFHJKLMNPQR34"


@tagged("post_install", "-at_install")
class TestEtransportDeclaration(EtransportDeclarationCommon):
    def _mark_validated(self, picking, uit=PREVIOUS_UIT):
        picking.l10n_ro_edi_stock_document_ids.unlink()
        picking._l10n_ro_edi_stock_create_document_stock_validated(
            {"l10n_ro_edi_stock_load_id": 1, "l10n_ro_edi_stock_uit": uit, "raw_xml": "<eTransport/>"}
        )

    def _skip_with_intrastat(self):
        if "intrastat_code_id" in self.env["product.product"]._fields:
            self.skipTest("cu account_intrastat, codul tarifar e validat de nucleu")

    # ------------------------------------------------------------------ corecție

    def test_initial_notification_has_no_corectie(self):
        picking = self._create_delivery([(self.product_a, 10)])
        tree = self._send(picking)
        self.assertFalse(tree.xpath("//etr:corectie", namespaces=NS))

    def test_amend_sends_corectie_with_previous_uit(self):
        """Corecția poartă UIT-ul corectat, ca prim copil al `notificare`.

        Fără `corectie`, ANAF înregistra o notificare nouă și emitea alt UIT,
        ignorat de Odoo: două UIT-uri active, transferul îl arăta pe cel vechi.
        """
        picking = self._create_delivery([(self.product_a, 10)])
        self._mark_validated(picking)
        picking.l10n_ro_edi_stock_vehicle_number = "B999XYZ"
        tree = self._send(picking, "amend")

        notificare = tree.xpath("//etr:notificare", namespaces=NS)[0]
        first_child = notificare[0]
        self.assertEqual(etree_local_name(first_child), "corectie", "XSD-ul cere `corectie` primul în secvență")
        self.assertEqual(first_child.get("uit"), PREVIOUS_UIT)
        self.assertEqual(
            picking.l10n_ro_edi_stock_document_uit,
            PREVIOUS_UIT,
            "corecția păstrează UIT-ul inițial, nu primește unul nou",
        )
        self.assertNotEqual(PREVIOUS_UIT, SENT_UIT)

    # ------------------------------------------------------------ greutate brută

    def test_gross_weight_without_package_equals_net(self):
        picking = self._create_delivery([(self.product_a, 10)])
        goods = self._goods(self._send(picking))[0]
        self.assertEqual(float(goods.get("greutateNeta")), 20.0)
        self.assertEqual(float(goods.get("greutateBruta")), 20.0)

    def test_gross_weight_counts_package_tare_once(self):
        """Coletul cântărit la 33 kg cu 20 + 10 kg de marfă are 3 kg tară.

        Nucleul declara 20 + 33 = 53 kg și 10 + 33 = 43 kg: marfa numărată de
        două ori și coletul o dată pe fiecare mișcare.
        """
        picking = self._create_delivery([(self.product_a, 10), (self.product_b, 10)])
        package = self.env["stock.package"].create({"name": "PALET-ET-1", "shipping_weight": 33.0})
        picking.move_line_ids.result_package_id = package

        goods = self._goods(self._send(picking))
        gross = {g.get("denumireMarfa"): float(g.get("greutateBruta")) for g in goods}
        self.assertEqual(gross[self.product_a.name], 22.0)
        self.assertEqual(gross[self.product_b.name], 11.0)
        self.assertAlmostEqual(sum(gross.values()), 33.0, places=2, msg="totalul brut = greutatea cântărită")

    def test_gross_weight_uses_package_type_when_not_weighed(self):
        picking = self._create_delivery([(self.product_a, 10)])
        package_type = self.env["stock.package.type"].create({"name": "Palet EUR test", "base_weight": 25.0})
        package = self.env["stock.package"].create({"name": "PALET-ET-2", "package_type_id": package_type.id})
        picking.move_line_ids.result_package_id = package

        goods = self._goods(self._send(picking))[0]
        self.assertEqual(float(goods.get("greutateBruta")), 45.0)

    # -------------------------------------------------------------- cod tarifar

    def test_tariff_code_from_hs_code(self):
        self._skip_with_intrastat()
        picking = self._create_delivery([(self.product_a, 10)])
        goods = self._goods(self._send(picking))[0]
        self.assertEqual(goods.get("codTarifar"), "84713000")

    def test_missing_tariff_code_blocks_the_declaration(self):
        """Fără cod, nucleul trimitea tăcut `00000000`, acceptat de ANAF (BR-034)."""
        self._skip_with_intrastat()
        product = self.env["product.product"].create({"name": "Fara cod", "type": "consu", "weight": 1.0})
        picking = self._create_delivery([(product, 5)])
        errors = picking._l10n_ro_edi_stock_validate_data(self._declaration_data(picking))
        self.assertTrue(any(product.display_name in error for error in errors))

    def test_tariff_code_not_required_for_operation_70(self):
        self._skip_with_intrastat()
        product = self.env["product.product"].create({"name": "Fara cod 70", "type": "consu", "weight": 1.0})
        picking = self._create_delivery([(product, 5)])
        picking.l10n_ro_edi_stock_operation_type = "70"
        errors = picking._l10n_ro_edi_stock_validate_data(self._declaration_data(picking))
        self.assertFalse([error for error in errors if product.display_name in error])

    # -------------------------------------------------------------- post-avarie

    def test_post_outage_flag(self):
        picking = self._create_delivery([(self.product_a, 10)])
        tree = self._send(picking)
        self.assertIsNone(tree.get("declPostAvarie"))

        picking.l10n_ro_edi_stock_document_ids.unlink()
        picking.l10n_ro_etransport_post_outage = True
        tree = self._send(picking)
        self.assertEqual(tree.get("declPostAvarie"), "D")


def etree_local_name(element):
    return element.tag.split("}", 1)[-1]
