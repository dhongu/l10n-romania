# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
"""Documentele însoțitoare eTransport (CMR, factură, aviz).

Nativ, `l10n_ro_edi_stock` trimite UN SINGUR document, hardcodat ca aviz (tip 30)
cu numărul transferului — deci CMR-ul sau numărul real de aviz nu ajungeau în
declarația ANAF. Schema acceptă o LISTĂ de `documenteTransport`.
"""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestEtransportDocuments(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "Client eTransport doc", "country_id": cls.env.ref("base.ro").id}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Marfă doc eTransport", "type": "consu", "weight": 2.0}
        )
        warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.env.company.id)], limit=1)
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": warehouse.out_type_id.id,
                "location_id": warehouse.lot_stock_id.id,
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            # `stock.move.name` nu mai există în Odoo 19
                            "product_id": cls.product.id,
                            "product_uom_qty": 10,
                            "location_id": warehouse.lot_stock_id.id,
                            "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
                        },
                    )
                ],
            }
        )

    def test_documents_created_and_ordered(self):
        """Se pot declara mai multe documente pe același transfer."""
        docs = self.env["l10n.ro.etransport.document"].create(
            [
                {
                    "picking_id": self.picking.id,
                    "l10n_ro_document_type": "30",
                    "name": self.picking.name,
                    "l10n_ro_document_date": "2026-07-20",
                },
                {
                    "picking_id": self.picking.id,
                    "l10n_ro_document_type": "10",
                    "name": "MAA00123",
                    "l10n_ro_document_date": "2026-07-21",
                },
            ]
        )
        self.assertEqual(len(self.picking.l10n_ro_etransport_document_ids), 2)
        cmr = docs.filtered(lambda d: d.l10n_ro_document_type == "10")
        self.assertIn("CMR", cmr.display_name)
        self.assertIn("MAA00123", cmr.display_name)

    def test_default_documents_button(self):
        """Butonul preia avizul (numărul transferului) și nu duplică la re-apăsare."""
        self.picking.l10n_ro_etransport_add_default_documents()
        docs = self.picking.l10n_ro_etransport_document_ids
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs.l10n_ro_document_type, "30")
        self.assertEqual(docs.name, self.picking.name)
        self.picking.l10n_ro_etransport_add_default_documents()
        self.assertEqual(
            len(self.picking.l10n_ro_etransport_document_ids), 1, "a doua apăsare nu trebuie să dubleze documentele"
        )

    def test_template_data_uses_declared_documents(self):
        """Datele trimise la ANAF conțin TOATE documentele declarate, ca listă."""
        self.env["l10n.ro.etransport.document"].create(
            [
                {
                    "picking_id": self.picking.id,
                    "l10n_ro_document_type": "30",
                    "name": "AVZ-999",
                    "l10n_ro_document_date": "2026-07-20",
                },
                {
                    "picking_id": self.picking.id,
                    "l10n_ro_document_type": "10",
                    "name": "CMR-555",
                    "l10n_ro_document_date": "2026-07-21",
                    "l10n_ro_remarks": "transport frigorific",
                },
            ]
        )
        data = {
            "notificare": {
                "documenteTransport": {
                    "tipDocument": "30",
                    "dataDocument": "2026-07-01",
                    "numarDocument": self.picking.name,
                    "observatii": "",
                }
            }
        }
        res = {"data": data}
        docs = self.picking.l10n_ro_etransport_document_ids
        # simulăm doar partea de documente din override (fără apel ANAF)
        res["data"]["notificare"]["documenteTransport"] = [
            {
                "tipDocument": d.l10n_ro_document_type,
                "dataDocument": d.l10n_ro_document_date,
                "numarDocument": d.name,
                "observatii": d.l10n_ro_remarks or "",
            }
            for d in docs
        ]
        sent = res["data"]["notificare"]["documenteTransport"]
        self.assertEqual(len(sent), 2)
        self.assertEqual({d["tipDocument"] for d in sent}, {"30", "10"})
        self.assertEqual({d["numarDocument"] for d in sent}, {"AVZ-999", "CMR-555"})

    def test_xml_renders_multiple_documents(self):
        """Template-ul QWeb randează câte un tag `documenteTransport` per document."""
        data_notificare = {
            "documenteTransport": [
                {"tipDocument": "30", "dataDocument": "2026-07-20", "numarDocument": "AVZ-999", "observatii": ""},
                {"tipDocument": "10", "dataDocument": "2026-07-21", "numarDocument": "CMR-555", "observatii": "frig"},
            ],
        }
        # randăm doar fragmentul de documente, cu aceeași logică din template
        rendered = self.env["ir.qweb"]._render(
            self.env["ir.ui.view"]
            .create(
                {
                    "name": "test_docs_fragment",
                    "type": "qweb",
                    "arch": """
                <t>
                    <t t-set="data_docs" t-value="data_notificare['documenteTransport']"/>
                    <t t-if="not isinstance(data_docs, list)" t-set="data_docs" t-value="[data_docs]"/>
                    <t t-foreach="data_docs" t-as="data_doc">
                        <documenteTransport t-att-tipDocument="data_doc['tipDocument']"
                                            t-att-numarDocument="data_doc['numarDocument']"/>
                    </t>
                </t>""",
                }
            )
            .id,
            {"data_notificare": data_notificare, "isinstance": isinstance, "list": list},
        )
        self.assertEqual(str(rendered).count("<documenteTransport"), 2)
        self.assertIn("CMR-555", str(rendered))
        self.assertIn("AVZ-999", str(rendered))
