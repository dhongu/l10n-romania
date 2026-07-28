# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
"""Traseul rutier între punctul de trecere a frontierei și biroul vamal.

Nativ, `l10n_ro_edi_stock` permite biroul vamal doar la plecare pentru import (40)
și doar la sosire pentru export (50), celălalt capăt fiind obligatoriu o locație.
Așa nu se putea obține UIT pe tronsonul sub supraveghere vamală: PTF -> birou vamal
la import, respectiv birou vamal -> PTF la export.
"""

from unittest.mock import patch

from odoo.tests import tagged

from odoo.addons.l10n_ro_edi_stock.tests.common import TestL10nRoEdiStockCommon


@patch("odoo.addons.l10n_ro_edi_stock.models.etransport_api.ETransportAPI._make_etransport_request")
@tagged("post_install", "-at_install")
class TestETransportCustomsRoute(TestL10nRoEdiStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.tz = "Europe/Bucharest"
        cls.env.company.write(
            {
                "vat": "9000123456789",
                "street": "Calea Nationala 85",
                "city": "Botosani",
                "zip": "710052",
                "state_id": cls.env.ref("base.RO_BT").id,
                "l10n_ro_edi_access_token": "some access token",
            }
        )
        cls.transport_partner = cls.env["res.partner"].create(
            {
                "name": "Transportator RO",
                "vat": "8001011234567",
                "street": "Strada Mihai Viteazul 22",
                "city": "Caransebes",
                "zip": "325400",
                "state_id": cls.env.ref("base.RO_CS").id,
                "country_id": cls.env.ref("base.ro").id,
            }
        )
        # furnizor extracomunitar: la import, partenerul comercial din declarație
        cls.supplier = cls.env["res.partner"].create(
            {
                "name": "Furnizor Turcia",
                "vat": "1234567890",
                "street": "Ataturk Cd 10",
                "city": "Istanbul",
                "country_id": cls.env.ref("base.tr").id,
            }
        )
        cls.product_a.weight = 1
        if "intrastat_code_id" in cls.env["product.product"]._fields:
            cls.product_a.intrastat_code_id = cls.env.ref("account_intrastat.commodity_code_2018_1012100")

        cls.carrier = cls.env.ref("delivery.free_delivery_carrier")
        cls.carrier.l10n_ro_edi_stock_partner_id = cls.transport_partner

        cls.upload_response = {
            "content": {
                "dateResponse": "202607281132",
                "ExecutionStatus": 0,
                "index_incarcare": "3006",
                "UIT": "3ND4BJ72YHW7PQ57",
            }
        }

    def _create_receipt(self):
        picking = self.create_stock_picking(
            name="receipt_vama",
            partner=self.supplier,
            picking_type=self.warehouse.in_type_id,
            product_data=[{"product_id": self.product_a, "product_uom_qty": 10.0, "quantity": 10.0}],
        )
        picking.write(
            {
                "carrier_id": self.carrier.id,
                "l10n_ro_transport_partner_id": self.transport_partner.id,
                "l10n_ro_edi_stock_required": True,
            }
        )
        return picking

    def test_available_location_types_import(self, make_request):
        """La import, ambele capete pot fi PTF sau birou vamal."""
        picking = self._create_receipt()
        picking.l10n_ro_edi_stock_operation_type = "40"
        self.assertEqual(picking.l10n_ro_edi_stock_available_start_loc_types, "location,bcp,customs")
        self.assertEqual(picking.l10n_ro_edi_stock_available_end_loc_types, "location,bcp,customs")

    def test_available_location_types_export(self, make_request):
        """La export, biroul vamal de plecare devine disponibil (birou vamal -> PTF)."""
        picking = self._create_receipt()
        picking.l10n_ro_edi_stock_operation_type = "50"
        self.assertEqual(picking.l10n_ro_edi_stock_available_start_loc_types, "location,bcp,customs")
        self.assertEqual(picking.l10n_ro_edi_stock_available_end_loc_types, "location,bcp,customs")

    def test_available_location_types_other_operations_unchanged(self, make_request):
        """Celelalte operațiuni păstrează exact restricțiile din standard."""
        picking = self._create_receipt()
        cases = {
            # tip operațiune: (capete disponibile la plecare, la sosire)
            "10": ("location,bcp", "location,bcp"),
            "20": ("location", "location,bcp"),
            "30": ("location", "location"),
            "60": ("location,bcp", "location"),
            "70": ("location", "location,bcp"),
        }
        for operation_type, (start, end) in cases.items():
            picking.l10n_ro_edi_stock_operation_type = operation_type
            self.assertEqual(picking.l10n_ro_edi_stock_available_start_loc_types, start, operation_type)
            self.assertEqual(picking.l10n_ro_edi_stock_available_end_loc_types, end, operation_type)

    def test_import_bcp_to_customs_office_no_errors(self, make_request):
        """Validarea acceptă traseul PTF -> birou vamal, fără să ceară o locație."""
        picking = self._create_receipt()
        picking.with_context(demo_mode=True).button_validate()
        picking.write(
            {
                "l10n_ro_edi_stock_operation_type": "40",
                "l10n_ro_edi_stock_operation_scope": "9999",
                "l10n_ro_edi_stock_vehicle_number": "CT18TRB",
                "l10n_ro_edi_stock_start_loc_type": "bcp",
                # Constanța Sud Agigea -> BVI Antrepozite/Ilfov
                "l10n_ro_edi_stock_start_bcp": "35",
                "l10n_ro_edi_stock_end_loc_type": "customs",
                "l10n_ro_edi_stock_end_customs_office": "232801",
            }
        )
        errors = picking._l10n_ro_edi_stock_validate_data(self._build_send_data(picking))
        self.assertFalse(errors, "\n".join(errors))

    def test_import_bcp_to_customs_office_xml(self, make_request):
        """Declarația trimisă conține codPtf la plecare și codBirouVamal la sosire."""
        picking = self._create_receipt()
        picking.with_context(demo_mode=True).button_validate()
        picking.write(
            {
                "l10n_ro_edi_stock_operation_type": "40",
                "l10n_ro_edi_stock_operation_scope": "9999",
                "l10n_ro_edi_stock_vehicle_number": "CT18TRB",
                "l10n_ro_edi_stock_start_loc_type": "bcp",
                "l10n_ro_edi_stock_start_bcp": "35",
                "l10n_ro_edi_stock_end_loc_type": "customs",
                "l10n_ro_edi_stock_end_customs_office": "232801",
            }
        )
        make_request.return_value = self.upload_response
        picking.action_l10n_ro_edi_stock_send_etransport()

        self.assertEqual(picking.l10n_ro_edi_stock_state, "stock_sent")
        xml = str(make_request.call_args.kwargs["data"])
        self.assertIn('codTipOperatiune="40"', xml)
        self.assertIn('<locStartTraseuRutier codPtf="35">', xml)
        self.assertIn('<locFinalTraseuRutier codBirouVamal="232801">', xml)
        self.assertNotIn("<locatie", xml, "traseul vamal nu declară locații")

    def _build_send_data(self, picking):
        """Datele pe care standardul le compune înainte de validare."""
        return {
            "partner_id": picking.partner_id,
            "transport_partner_id": picking.carrier_id.l10n_ro_edi_stock_partner_id,
            "company_id": picking.company_id,
            "scheduled_date": picking.scheduled_date,
            "name": picking.name,
            "send_type": "send",
            "l10n_ro_edi_stock_operation_type": picking.l10n_ro_edi_stock_operation_type,
            "l10n_ro_edi_stock_operation_scope": picking.l10n_ro_edi_stock_operation_scope,
            "stock_move_ids": picking.move_ids,
            "l10n_ro_edi_stock_vehicle_number": picking.l10n_ro_edi_stock_vehicle_number,
            "l10n_ro_edi_stock_trailer_1_number": picking.l10n_ro_edi_stock_trailer_1_number,
            "l10n_ro_edi_stock_trailer_2_number": picking.l10n_ro_edi_stock_trailer_2_number,
            "l10n_ro_edi_stock_start_loc_type": picking.l10n_ro_edi_stock_start_loc_type,
            "l10n_ro_edi_stock_end_loc_type": picking.l10n_ro_edi_stock_end_loc_type,
            "l10n_ro_edi_stock_remarks": picking.l10n_ro_edi_stock_remarks,
            "picking_type_id": picking.picking_type_id,
            "l10n_ro_edi_stock_start_bcp": picking.l10n_ro_edi_stock_start_bcp,
            "l10n_ro_edi_stock_end_bcp": picking.l10n_ro_edi_stock_end_bcp,
            "l10n_ro_edi_stock_start_customs_office": picking.l10n_ro_edi_stock_start_customs_office,
            "l10n_ro_edi_stock_end_customs_office": picking.l10n_ro_edi_stock_end_customs_office,
            "l10n_ro_edi_stock_document_uit": picking.l10n_ro_edi_stock_document_uit,
        }
