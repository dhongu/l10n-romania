# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
"""Documentele însoțitoare eTransport (CMR, factură, aviz).

Nativ, `l10n_ro_edi_stock` trimite UN SINGUR document, hardcodat ca aviz (tip 30)
cu numărul transferului — deci CMR-ul sau numărul real de aviz nu ajungeau în
declarația ANAF. Schema acceptă o LISTĂ de `documenteTransport`.
"""

from unittest.mock import patch

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
                    "document_type": "30",
                    "name": self.picking.name,
                    "date": "2026-07-20",
                },
                {
                    "picking_id": self.picking.id,
                    "document_type": "10",
                    "name": "MAA00123",
                    "date": "2026-07-21",
                },
            ]
        )
        self.assertEqual(len(self.picking.l10n_ro_etransport_document_ids), 2)
        cmr = docs.filtered(lambda d: d.document_type == "10")
        self.assertIn("CMR", cmr.display_name)
        self.assertIn("MAA00123", cmr.display_name)

    def test_default_documents_button(self):
        """Butonul preia avizul (numărul transferului) și nu duplică la re-apăsare."""
        self.picking.l10n_ro_etransport_add_default_documents()
        docs = self.picking.l10n_ro_etransport_document_ids
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs.document_type, "30")
        self.assertEqual(docs.name, self.picking.name)
        self.picking.l10n_ro_etransport_add_default_documents()
        self.assertEqual(
            len(self.picking.l10n_ro_etransport_document_ids), 1, "a doua apăsare nu trebuie să dubleze documentele"
        )

    def _native_template_data(self):
        """Scheletul minim pe care îl întoarce standardul, cât să treacă override-ul."""
        return {
            "data": {
                "notificare": {
                    "bunuriTransportate": [],
                    "partenerComercial": {"codTara": "RO"},
                    "dateTransport": {"dataTransport": "2026-07-20"},
                    "locStartTraseuRutier": {},
                    "locFinalTraseuRutier": {},
                    "documenteTransport": {
                        "tipDocument": "30",
                        "dataDocument": "2026-07-01",
                        "numarDocument": self.picking.name,
                        "observatii": False,
                    },
                }
            }
        }

    def _get_template_data(self):
        patch_path = "odoo.addons.l10n_ro_edi_stock.models.stock_picking.Picking._l10n_ro_edi_stock_get_template_data"
        with patch(patch_path, return_value=self._native_template_data()):
            return self.picking._l10n_ro_edi_stock_get_template_data(
                {"transport_partner_id": self.picking.partner_id, "stock_move_ids": self.picking.move_ids}
            )

    def test_template_data_uses_declared_documents(self):
        """Datele trimise la ANAF conțin TOATE documentele declarate, ca listă."""
        self.env["l10n.ro.etransport.document"].create(
            [
                {
                    "picking_id": self.picking.id,
                    "document_type": "30",
                    "name": "AVZ-999",
                    "date": "2026-07-20",
                },
                {
                    "picking_id": self.picking.id,
                    "document_type": "10",
                    "name": "CMR-555",
                    "date": "2026-07-21",
                    "remarks": "transport frigorific",
                },
            ]
        )
        res = self._get_template_data()
        sent = res["data"]["notificare"]["documenteTransport"]
        self.assertEqual(len(sent), 2)
        self.assertEqual({d["tipDocument"] for d in sent}, {"30", "10"})
        self.assertEqual({d["numarDocument"] for d in sent}, {"AVZ-999", "CMR-555"})

    def test_empty_remarks_is_not_sent_as_empty_string(self):
        """Fără observație, `observatii` NU pleacă spre template ca string gol.

        XSD-ul ANAF tipează atributul ca `Str200` (minLength=1), deci un
        `observatii=""` în XML e respins cu
        `cvc-minLength-valid: Value '' with length = '0'`.
        """
        self.env["l10n.ro.etransport.document"].create(
            [
                {
                    "picking_id": self.picking.id,
                    "document_type": "30",
                    "name": "AVZ-1000",
                    "date": "2026-07-20",
                },
                {
                    "picking_id": self.picking.id,
                    "document_type": "10",
                    "name": "CMR-1000",
                    "date": "2026-07-20",
                    # numai spații: ANAF ar primi un atribut fără conținut util
                    "remarks": "   ",
                },
            ]
        )
        sent = self._get_template_data()["data"]["notificare"]["documenteTransport"]
        self.assertEqual(len(sent), 2)
        for doc in sent:
            self.assertIs(doc["observatii"], False, "observația goală trebuie să fie False, nu string gol")

    def test_xml_renders_multiple_documents(self):
        """Template-ul QWeb randează câte un tag `documenteTransport` per document."""
        data_notificare = {
            "documenteTransport": [
                {"tipDocument": "30", "dataDocument": "2026-07-20", "numarDocument": "AVZ-999", "observatii": False},
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
                                            t-att-numarDocument="data_doc['numarDocument']"
                                            t-att-observatii="data_doc.get('observatii') or False"/>
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
        # atributul apare o singură dată — cel gol e omis, nu randat ca `observatii=""`
        self.assertEqual(str(rendered).count("observatii="), 1)
        self.assertNotIn('observatii=""', str(rendered))
