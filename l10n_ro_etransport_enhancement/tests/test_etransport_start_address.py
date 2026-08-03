# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
"""Locație de start specifică pentru transportul pe teritoriul național.

Câmpul `l10n_ro_etransport_start_address` permite înlocuirea adresei de start
calculate automat (depozitul) cu adresa unui partener ales manual — util când
transportul național (cod operațiune `30`) pleacă efectiv dintr-un alt loc
decât depozitul (de exemplu un birou vamal de interior, după vămuire).
"""

from unittest.mock import patch

from odoo.tests import tagged

from odoo.addons.l10n_ro_edi_stock.tests.common import TestL10nRoEdiStockCommon


@patch("odoo.addons.l10n_ro_edi_stock.models.etransport_api.ETransportAPI._make_etransport_request")
@tagged("post_install", "-at_install")
class TestETransportStartAddress(TestL10nRoEdiStockCommon):
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
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Client national",
                "vat": "RO1234567897",
                "street": "Strada General Traian Mosoiu 24",
                "city": "Bran",
                "zip": "507025",
                "state_id": cls.env.ref("base.RO_BV").id,
                "country_id": cls.env.ref("base.ro").id,
            }
        )
        cls.transport_partner = cls.env["res.partner"].create(
            {
                "name": "Transportator Local",
                "vat": "8001011234567",
                "street": "Strada Mihai Viteazul 22",
                "city": "Caransebes",
                "zip": "325400",
                "state_id": cls.env.ref("base.RO_CS").id,
                "country_id": cls.env.ref("base.ro").id,
            }
        )
        cls.start_partner = cls.env["res.partner"].create(
            {
                "name": "Birou vamal interior SRL",
                "street": "Strada Vamii 1",
                "city": "Cluj",
                "zip": "400000",
                "state_id": cls.env.ref("base.RO_CJ").id,
                "country_id": cls.env.ref("base.ro").id,
            }
        )
        cls.carrier = cls.env.ref("delivery.free_delivery_carrier")
        cls.carrier.l10n_ro_edi_stock_partner_id = cls.transport_partner
        cls.product_a.weight = 1
        if "intrastat_code_id" in cls.env["product.product"]._fields:
            cls.product_a.intrastat_code_id = cls.env.ref("account_intrastat.commodity_code_2018_1012100")

        cls.upload_response = {
            "content": {
                "dateResponse": "202607281132",
                "ExecutionStatus": 0,
                "index_incarcare": "3006",
                "UIT": "3ND4BJ72YHW7PQ57",
            }
        }

    def _create_delivery(self):
        picking = self.create_stock_picking(
            partner=self.customer,
            product_data=[{"product_id": self.product_a, "product_uom_qty": 10.0, "quantity": 10.0}],
        )
        picking.write(
            {
                "carrier_id": self.carrier.id,
                "l10n_ro_edi_stock_required": True,
                "l10n_ro_edi_stock_operation_type": "30",
                "l10n_ro_edi_stock_operation_scope": "9901",
                "l10n_ro_edi_stock_vehicle_number": "CJ18TRB",
            }
        )
        return picking

    def test_start_address_overrides_default_location(self, make_request):
        """Cu câmpul completat, adresa trimisă la ANAF e a partenerului ales, nu a depozitului."""
        picking = self._create_delivery()
        picking.l10n_ro_etransport_start_address = self.start_partner
        make_request.return_value = self.upload_response
        picking.action_l10n_ro_edi_stock_send_etransport()

        self.assertEqual(picking.l10n_ro_edi_stock_state, "stock_sent")
        xml = str(make_request.call_args.kwargs["data"])
        self.assertIn('denumireLocalitate="Cluj"', xml)
        self.assertIn('denumireStrada="Strada Vamii 1"', xml)
        self.assertIn('codPostal="400000"', xml)
        self.assertNotIn('denumireLocalitate="Botosani"', xml, "adresa depozitului nu mai trebuie trimisă")

    def test_without_start_address_uses_default_location(self, make_request):
        """Fără câmpul completat, comportamentul standard rămâne neschimbat (adresa depozitului)."""
        picking = self._create_delivery()
        make_request.return_value = self.upload_response
        picking.action_l10n_ro_edi_stock_send_etransport()

        self.assertEqual(picking.l10n_ro_edi_stock_state, "stock_sent")
        xml = str(make_request.call_args.kwargs["data"])
        self.assertIn('denumireLocalitate="Botosani"', xml)

    def test_start_address_ignored_when_start_location_is_not_address(self, make_request):
        """Cu locația de start pe punct de trecere a frontierei, câmpul nu are efect.

        Nu există un `locatie` de suprascris — declarația trimite `codPtf`, nu o adresă.
        """
        picking = self._create_delivery()
        picking.l10n_ro_etransport_start_address = self.start_partner
        picking.write(
            {
                "l10n_ro_edi_stock_start_loc_type": "bcp",
                "l10n_ro_edi_stock_start_bcp": "35",  # Constanța Sud Agigea
            }
        )
        make_request.return_value = self.upload_response
        picking.action_l10n_ro_edi_stock_send_etransport()

        self.assertEqual(picking.l10n_ro_edi_stock_state, "stock_sent")
        xml = str(make_request.call_args.kwargs["data"])
        self.assertIn('<locStartTraseuRutier codPtf="35"', xml)
        self.assertNotIn("Cluj", xml)
