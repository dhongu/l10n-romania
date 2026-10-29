# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
"""Declarația pe LOT poartă greutățile cântărite, documentele și marcajul lotului.

`l10n_ro_edi_stock_batch` construiește declarația lotului pe un `stock.picking`
GOL, deci override-urile de pe `stock.picking.batch` nu rulau niciodată: XML-ul
pleca tăcut cu greutățile nucleului și un singur aviz cu numele lotului.
"""

from odoo.tests import tagged

from odoo.addons.l10n_ro_etransport_enhancement.tests.common import NS, EtransportDeclarationCommon


@tagged("post_install", "-at_install")
class TestBatchDeclaration(EtransportDeclarationCommon):
    def _create_batch(self):
        picking = self._create_delivery([(self.product_a, 10)])
        batch = self.env["stock.picking.batch"].create(
            {
                "picking_ids": [(4, picking.id)],
                "picking_type_id": picking.picking_type_id.id,
                "l10n_ro_edi_stock_required": True,
                **self._declaration_values(),
            }
        )
        return batch, picking

    def test_batch_sends_weighed_weights(self):
        batch, picking = self._create_batch()
        batch.l10n_ro_shipping_weights = True
        self.env["l10n.ro.stock.picking.weight.line"].create(
            {"picking_id": picking.id, "move_id": picking.move_ids.id, "net_weight": 19.5, "gross_weight": 23.25}
        )
        self.assertEqual(batch.l10n_ro_shipping_weight_lines.move_id, picking.move_ids)

        goods = self._goods(self._send(batch))[0]
        self.assertEqual(float(goods.get("greutateNeta")), 19.5)
        self.assertEqual(float(goods.get("greutateBruta")), 23.25)

    def test_batch_sends_batch_and_picking_documents(self):
        batch, picking = self._create_batch()
        self.env["l10n.ro.etransport.document"].create(
            [
                {"batch_id": batch.id, "document_type": "10", "name": "CMR-LOT-1", "date": "2026-10-07"},
                {"picking_id": picking.id, "document_type": "30", "name": "AVZ-LOT-1", "date": "2026-10-07"},
            ]
        )
        docs = self._send(batch).xpath("//etr:documenteTransport", namespaces=NS)
        self.assertEqual({doc.get("numarDocument") for doc in docs}, {"CMR-LOT-1", "AVZ-LOT-1"})

    def test_batch_post_outage_flag(self):
        batch, _picking = self._create_batch()
        batch.l10n_ro_etransport_post_outage = True
        self.assertEqual(self._send(batch).get("declPostAvarie"), "D")

    def test_batch_amend_sends_corectie(self):
        batch, _picking = self._create_batch()
        batch._l10n_ro_edi_stock_create_document_stock_validated(
            {"l10n_ro_edi_stock_load_id": 1, "l10n_ro_edi_stock_uit": "ACDEFHJKLMNPQR56", "raw_xml": "<eTransport/>"}
        )
        corectie = self._send(batch, "amend").xpath("//etr:notificare/etr:corectie", namespaces=NS)
        self.assertEqual(len(corectie), 1)
        self.assertEqual(corectie[0].get("uit"), "ACDEFHJKLMNPQR56")
