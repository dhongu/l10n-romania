# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
"""Bază pentru testele care trimit o declarație eTransport completă.

Declarația trece prin fluxul real: validarea, `_l10n_ro_edi_stock_get_template_data`
și randarea template-ului QWeb. Doar apelul la ANAF (`ETransportAPI.upload_data`)
e simulat, iar XML-ul trimis e capturat și parsat, ca testele să verifice ce
ajunge efectiv la ANAF, nu un dicționar intermediar.
"""

from unittest.mock import patch

from lxml import etree

from odoo.tests.common import TransactionCase

UPLOAD_PATCH = "odoo.addons.l10n_ro_edi_stock.models.etransport_api.ETransportAPI.upload_data"
NS = {"etr": "mfp:anaf:dgti:eTransport:declaratie:v2"}
SENT_UIT = "ACDEFHJKLMNPQR12"


class EtransportDeclarationCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ro = cls.env.ref("base.ro")
        cls.company = cls.env.company
        cls.company.write(
            {
                "vat": "9000123456789",
                "street": "Calea Nationala 85",
                "city": "Botosani",
                "zip": "710052",
                "state_id": cls.env.ref("base.RO_BT").id,
                "country_id": ro.id,
                "l10n_ro_edi_access_token": "test-token",
            }
        )
        # starea și UIT-ul curent al declarației se calculează doar pentru RO
        cls.company.account_fiscal_country_id = ro
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.company.id)], limit=1)
        cls.warehouse.partner_id = cls.company.partner_id
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Client eTransport",
                "vat": "RO1234567897",
                "street": "Strada General Traian Mosoiu 24",
                "city": "Bran",
                "zip": "507025",
                "state_id": cls.env.ref("base.RO_BV").id,
                "country_id": ro.id,
            }
        )
        cls.transporter = cls.env["res.partner"].create(
            {
                "name": "Transportator eTransport",
                "vat": "8001011234567",
                "street": "Strada Mihai Viteazul 22",
                "city": "Caransebes",
                "zip": "325400",
                "state_id": cls.env.ref("base.RO_CS").id,
                "country_id": ro.id,
            }
        )
        cls.product_a = cls.env["product.product"].create(
            {"name": "Marfa A eTransport", "type": "consu", "weight": 2.0, "hs_code": "8471.30.00"}
        )
        cls.product_b = cls.env["product.product"].create(
            {"name": "Marfa B eTransport", "type": "consu", "weight": 1.0, "hs_code": "847150"}
        )

    @classmethod
    def _declaration_values(cls):
        return {
            "l10n_ro_edi_stock_operation_type": "30",
            "l10n_ro_edi_stock_operation_scope": "101",
            "l10n_ro_edi_stock_vehicle_number": "B123ABC",
            "l10n_ro_edi_stock_start_loc_type": "location",
            "l10n_ro_edi_stock_end_loc_type": "location",
        }

    @classmethod
    def _create_delivery(cls, lines):
        """Livrare confirmată, cu cantitățile pregătite (deci cu linii de mișcare)."""
        picking_type = cls.warehouse.out_type_id
        picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.customer.id,
                "picking_type_id": picking_type.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
                "l10n_ro_edi_stock_required": True,
                "l10n_ro_transport_partner_id": cls.transporter.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": qty,
                            "product_uom": product.uom_id.id,
                            "location_id": cls.warehouse.lot_stock_id.id,
                            "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
                        },
                    )
                    for product, qty in lines
                ],
            }
        )
        picking.action_confirm()
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
        picking.write(cls._declaration_values())
        return picking

    @staticmethod
    def _declaration_data(picking, send_type="send"):
        """Dicționarul construit de nucleu în `_l10n_ro_edi_stock_send_etransport_document`."""
        data = {
            "partner_id": picking.partner_id,
            "transport_partner_id": picking.carrier_id.l10n_ro_edi_stock_partner_id,
            "company_id": picking.company_id,
            "scheduled_date": picking.scheduled_date,
            "name": picking.name,
            "send_type": send_type,
            "stock_move_ids": picking.move_ids,
            "picking_type_id": picking.picking_type_id,
        }
        for suffix in (
            "operation_type",
            "operation_scope",
            "vehicle_number",
            "trailer_1_number",
            "trailer_2_number",
            "start_loc_type",
            "end_loc_type",
            "remarks",
            "start_bcp",
            "end_bcp",
            "start_customs_office",
            "end_customs_office",
            "document_uit",
        ):
            data[f"l10n_ro_edi_stock_{suffix}"] = picking[f"l10n_ro_edi_stock_{suffix}"]
        return data

    def _send(self, record, send_type="send"):
        """Trimite declarația și întoarce XML-ul ajuns la „ANAF”, parsat."""
        sent = []

        def upload(company_id, data):
            sent.append(data)
            return {"content": {"index_incarcare": 1, "UIT": SENT_UIT}}

        with patch(UPLOAD_PATCH, side_effect=upload):
            record._l10n_ro_edi_stock_send_etransport_document(send_type)
        failed = record.l10n_ro_edi_stock_document_ids.filtered(lambda d: d.state == "stock_sending_failed")
        self.assertFalse(failed, f"declarația nu a trecut validarea: {failed.mapped('message')}")
        self.assertEqual(len(sent), 1, "declarația trebuie trimisă o singură dată")
        return etree.fromstring(str(sent[0]).split("?>", 1)[1].encode())

    def _goods(self, tree):
        return tree.xpath("//etr:bunuriTransportate", namespaces=NS)
