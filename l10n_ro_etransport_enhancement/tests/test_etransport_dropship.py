# Copyright 2026
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from unittest import SkipTest
from unittest.mock import patch

from lxml import etree

from odoo import Command, fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestEtransportDropship(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if "dropship" not in dict(cls.env["stock.picking.type"]._fields["code"]._description_selection(cls.env)):
            raise SkipTest("Install stock_dropshipping to run the dropship workflow tests.")
        cls.env.user.tz = "Europe/Bucharest"
        cls.ro = cls.env.ref("base.ro")
        cls.company = cls.env.company
        cls.company.write(
            {
                "country_id": cls.ro.id,
                "account_fiscal_country_id": cls.ro.id,
                "vat": "RO1234567897",
                "l10n_ro_edi_access_token": "test-only",
            }
        )
        cls.partner_values = {
            "country_id": cls.ro.id,
            "state_id": cls.env.ref("base.RO_CJ").id,
            "city": "Cluj-Napoca",
            "street": "Factory Street 1",
            "zip": "400000",
        }
        cls.supplier = cls.env["res.partner"].create(dict(cls.partner_values, name="Factory", is_company=True))
        cls.customer = cls.env["res.partner"].create(dict(cls.partner_values, name="Buyer", is_company=True))
        cls.delivery = cls.env["res.partner"].create(
            dict(
                cls.partner_values,
                name="Building Site",
                parent_id=cls.customer.id,
                type="delivery",
                city="Turda",
                street="Site Street 2",
                zip="401000",
            )
        )
        cls.carrier_partner = cls.env["res.partner"].create(
            dict(
                cls.partner_values,
                name="Carrier",
                vat="RO1234567897",
            )
        )
        cls.picking_type = cls.env["stock.picking.type"].create(
            {
                "name": "Dropship eTransport Test",
                "code": "dropship",
                "sequence_code": "ETDS",
                "company_id": cls.company.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Dropship Goods",
                "type": "consu",
                "weight": 2,
                "standard_price": 0,
            }
        )
        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "partner_shipping_id": cls.delivery.id,
                "company_id": cls.company.id,
                "currency_id": cls.env.ref("base.RON").id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 10,
                            "price_unit": 100,
                            "discount": 10,
                            "tax_ids": [Command.clear()],
                        }
                    )
                ],
            }
        )
        cls.purchase = cls.env["purchase.order"].create(
            {
                "partner_id": cls.supplier.id,
                "dest_address_id": cls.delivery.id,
                "company_id": cls.company.id,
                "picking_type_id": cls.picking_type.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_qty": 10,
                            "price_unit": 60,
                            "sale_line_id": cls.sale.order_line.id,
                        }
                    )
                ],
            }
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.supplier.id,
                "picking_type_id": cls.picking_type.id,
                "location_id": cls.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
                "scheduled_date": fields.Datetime.now(),
                "l10n_ro_edi_stock_required": True,
                "l10n_ro_transport_partner_id": cls.carrier_partner.id,
                "l10n_ro_edi_stock_operation_type": "30",
                "l10n_ro_edi_stock_operation_scope": "101",
                "l10n_ro_edi_stock_start_loc_type": "location",
                "l10n_ro_edi_stock_end_loc_type": "location",
                "l10n_ro_edi_stock_vehicle_number": "CJ01ABC",
            }
        )
        cls.move = cls.env["stock.move"].create(
            {
                "product_id": cls.product.id,
                "product_uom_qty": 10,
                "product_uom": cls.product.uom_id.id,
                "picking_id": cls.picking.id,
                "location_id": cls.picking.location_id.id,
                "location_dest_id": cls.picking.location_dest_id.id,
                "purchase_line_id": cls.purchase.order_line.id,
                "sale_line_id": cls.sale.order_line.id,
            }
        )

    def _send(self):
        with patch(
            "odoo.addons.l10n_ro_edi_stock.models.etransport_api.ETransportAPI._make_etransport_request"
        ) as request:
            request.return_value = {
                "content": {
                    "dateResponse": "202609091200",
                    "ExecutionStatus": 0,
                    "index_incarcare": "123",
                    "UIT": "TESTONLY12345678",
                }
            }
            self.picking.action_l10n_ro_edi_stock_send_etransport()
            return request

    def test_domestic_route_and_sale_value(self):
        request = self._send()
        self.assertTrue(request.called, self.picking.l10n_ro_edi_stock_document_ids.mapped("message"))
        xml = etree.fromstring(str(request.call_args.kwargs["data"]).encode())
        self.assertEqual(xml.xpath("//*[local-name()='locStartTraseuRutier']/*/@denumireStrada"), ["Factory Street 1"])
        self.assertEqual(xml.xpath("//*[local-name()='locFinalTraseuRutier']/*/@denumireStrada"), ["Site Street 2"])
        self.assertEqual(xml.xpath("//*[local-name()='partenerComercial']/@denumire"), ["Buyer"])
        self.assertEqual(float(xml.xpath("//*[local-name()='bunuriTransportate']/@valoareLeiFaraTva")[0]), 900)
        self.assertNotIn("dropship_address", str(request.call_args.kwargs["data"]))
        self.assertEqual(self.picking.picking_type_code, "dropship")
        self.assertFalse(self.picking.picking_type_id.warehouse_id)
        self.assertEqual(self.picking.partner_id, self.supplier)
        self.assertEqual(self.picking.state, "draft")

    def test_loading_address_override(self):
        factory_gate = self.env["res.partner"].create(
            dict(self.partner_values, name="Loading Gate", street="Gate Street 3")
        )
        self.picking.l10n_ro_etransport_start_address = factory_gate
        request = self._send()
        self.assertTrue(request.called)
        self.assertIn('denumireStrada="Gate Street 3"', str(request.call_args.kwargs["data"]))

    def test_invalid_loading_address_blocks_upload(self):
        self.picking.l10n_ro_etransport_start_address = self.env["res.partner"].create({"name": "Incomplete Factory"})
        self.assertFalse(self._send().called)
        self.assertEqual(self.picking.l10n_ro_edi_stock_state, "stock_sending_failed")

    def test_missing_delivery_postcode_blocks_upload(self):
        self.delivery.zip = False
        self.assertFalse(self._send().called)

    def test_international_operation_blocks_upload(self):
        """Selecting LIC alone must not relabel a domestic shipment."""
        self.picking.l10n_ro_edi_stock_operation_type = "20"
        self.assertFalse(self._send().called)

    def _set_international(self, operation, country):
        incoming = operation in ("10", "40")
        partner = self.supplier if incoming else self.customer
        partner.write({"country_id": country.id, "vat": "DE123456788" if country.code == "DE" else "US123456789"})
        if not incoming:
            self.delivery.country_id = country
        self.picking.write(
            {
                "l10n_ro_edi_stock_operation_type": operation,
                "l10n_ro_edi_stock_operation_scope": "101" if operation in ("10", "20") else "9999",
                "l10n_ro_edi_stock_start_loc_type": "bcp" if incoming else "location",
                "l10n_ro_edi_stock_end_loc_type": "location" if incoming else "bcp",
                "l10n_ro_edi_stock_start_bcp": "35" if incoming else False,
                "l10n_ro_edi_stock_end_bcp": False if incoming else "35",
            }
        )

    def test_intracommunity_purchase_uses_supplier_and_purchase_value(self):
        self._set_international("10", self.env.ref("base.de"))
        self.purchase.currency_id = self.env.ref("base.RON")
        request = self._send()
        self.assertTrue(request.called, self.picking.l10n_ro_edi_stock_document_ids.mapped("message"))
        xml = etree.fromstring(str(request.call_args.kwargs["data"]).encode())
        self.assertEqual(xml.xpath("//*[local-name()='locStartTraseuRutier']/@codPtf"), ["35"])
        self.assertEqual(xml.xpath("//*[local-name()='partenerComercial']/@denumire"), ["Factory"])
        self.assertEqual(float(xml.xpath("//*[local-name()='bunuriTransportate']/@valoareLeiFaraTva")[0]), 600)

    def test_intracommunity_sale_uses_customer(self):
        self._set_international("20", self.env.ref("base.de"))
        request = self._send()
        self.assertTrue(request.called, self.picking.l10n_ro_edi_stock_document_ids.mapped("message"))
        xml = etree.fromstring(str(request.call_args.kwargs["data"]).encode())
        self.assertEqual(xml.xpath("//*[local-name()='locFinalTraseuRutier']/@codPtf"), ["35"])
        self.assertEqual(xml.xpath("//*[local-name()='partenerComercial']/@denumire"), ["Buyer"])

    def test_import_border_to_customs(self):
        self._set_international("40", self.env.ref("base.us"))
        self.picking.write(
            {"l10n_ro_edi_stock_end_loc_type": "customs", "l10n_ro_edi_stock_end_customs_office": "12801"}
        )
        request = self._send()
        self.assertTrue(request.called, self.picking.l10n_ro_edi_stock_document_ids.mapped("message"))
        self.assertIn('codBirouVamal="12801"', str(request.call_args.kwargs["data"]))

    def test_export_customs_to_border(self):
        self._set_international("50", self.env.ref("base.us"))
        self.picking.write(
            {"l10n_ro_edi_stock_start_loc_type": "customs", "l10n_ro_edi_stock_start_customs_office": "12801"}
        )
        self.assertTrue(self._send().called)

    def test_missing_border_point_blocks_upload(self):
        self._set_international("10", self.env.ref("base.de"))
        self.picking.l10n_ro_edi_stock_start_bcp = False
        self.assertFalse(self._send().called)

    def test_eu_supplier_not_silently_treated_as_import(self):
        self._set_international("40", self.env.ref("base.de"))
        self.assertFalse(self._send().called)

    def test_foreign_to_foreign_transaction_requires_review(self):
        self._set_international("20", self.env.ref("base.de"))
        self.supplier.country_id = self.env.ref("base.fr")
        self.assertFalse(self._send().called)

    def test_currency_conversion_uses_transport_date(self):
        self.sale.currency_id = self.env.ref("base.EUR")
        self.env["res.currency.rate"].create(
            [
                {
                    "currency_id": self.env.ref("base.RON").id,
                    "company_id": self.company.id,
                    "name": fields.Date.today(),
                    "rate": 5,
                },
                {
                    "currency_id": self.env.ref("base.EUR").id,
                    "company_id": self.company.id,
                    "name": fields.Date.today(),
                    "rate": 1,
                },
            ]
        )
        request = self._send()
        self.assertTrue(request.called)
        xml = etree.fromstring(str(request.call_args.kwargs["data"]).encode())
        self.assertEqual(float(xml.xpath("//*[local-name()='bunuriTransportate']/@valoareLeiFaraTva")[0]), 4500)

    def test_enable_recomputes_when_required_changes(self):
        self.picking.l10n_ro_edi_stock_required = False
        self.assertFalse(self.picking.l10n_ro_edi_stock_enable)
        self.picking.l10n_ro_edi_stock_required = True
        self.assertTrue(self.picking.l10n_ro_edi_stock_enable)

    def test_measured_weights_independent_from_order_price_setting(self):
        self.company.l10n_ro_etransport_get_order_value = False
        self.picking.l10n_ro_shipping_weights = True
        self.env["l10n.ro.stock.picking.weight.line"].create(
            {
                "picking_id": self.picking.id,
                "move_id": self.move.id,
                "net_weight": 18,
                "gross_weight": 25,
            }
        )
        request = self._send()
        self.assertTrue(request.called)
        xml = etree.fromstring(str(request.call_args.kwargs["data"]).encode())
        self.assertEqual(float(xml.xpath("//*[local-name()='bunuriTransportate']/@greutateNeta")[0]), 18)
        self.assertEqual(float(xml.xpath("//*[local-name()='bunuriTransportate']/@greutateBruta")[0]), 25)

    def test_intermodal_incoming_uses_explicit_romanian_loading_address(self):
        port = self.env["res.partner"].create(dict(self.partner_values, name="Romanian Road Start"))
        self._set_international("10", self.env.ref("base.de"))
        self.picking.write(
            {"l10n_ro_etransport_start_address": port.id, "l10n_ro_edi_stock_start_loc_type": "location"}
        )
        self.assertTrue(self._send().called)

    def test_foreign_factory_blocks_domestic_upload(self):
        self.supplier.country_id = self.env.ref("base.de")
        self.assertFalse(self._send().called)

    def test_missing_sale_blocks_upload(self):
        self.move.sale_line_id = False
        self.purchase.order_line.sale_line_id = False
        self.assertFalse(self._send().called)

    def test_purchase_sale_link_fallback(self):
        self.move.sale_line_id = False
        self.assertTrue(self._send().called)

    def test_conflicting_delivery_addresses_block_upload(self):
        self.purchase.dest_address_id = self.customer
        self.assertFalse(self._send().called)

    def test_zero_sale_value_blocks_upload(self):
        self.sale.order_line.price_unit = 0
        self.assertFalse(self._send().called)

    def test_native_carrier_validation_preserved(self):
        self.carrier_partner.vat = False
        self.assertFalse(self._send().called)

    def test_native_vehicle_validation_preserved(self):
        self.picking.l10n_ro_edi_stock_vehicle_number = False
        self.assertFalse(self._send().called)

    def test_return_blocks_upload(self):
        self.picking.location_id, self.picking.location_dest_id = (
            self.picking.location_dest_id,
            self.picking.location_id,
        )
        self.assertFalse(self._send().called)

    def test_secondary_sale_unit(self):
        box = self.env["uom.uom"].create(
            {"name": "Test Box of 10", "relative_factor": 10, "relative_uom_id": self.product.uom_id.id}
        )
        self.sale.order_line.write({"product_uom_id": box.id, "price_unit": 1000, "discount": 10})
        request = self._send()
        self.assertTrue(request.called)
        xml = etree.fromstring(str(request.call_args.kwargs["data"]).encode())
        self.assertEqual(float(xml.xpath("//*[local-name()='bunuriTransportate']/@valoareLeiFaraTva")[0]), 900)

    def test_compiled_view_exposes_loading_address_for_dropship(self):
        view = self.env["stock.picking"].get_view(view_id=self.env.ref("stock.view_picking_form").id, view_type="form")
        arch = etree.fromstring(view["arch"])
        field = arch.xpath("//field[@name='l10n_ro_etransport_start_address']")[0]
        self.assertIn("'dropship'", field.get("invisible"))
        self.assertEqual(field.get("readonly"), "l10n_ro_edi_stock_fields_readonly")
        self.assertEqual(len(arch.xpath("//group[@name='weights']/group/field[@name='l10n_ro_shipping_weights']")), 1)

    def test_native_sale_purchase_dropship_workflow(self):
        self.product.write(
            {
                "route_ids": [Command.set(self.env.ref("stock_dropshipping.route_drop_shipping").ids)],
                "seller_ids": [Command.create({"partner_id": self.supplier.id, "price": 60, "delay": 0})],
            }
        )
        sale = self.sale.copy()
        sale.action_confirm()
        purchase = self.env["purchase.order"].search([("order_line.sale_line_id", "in", sale.order_line.ids)])
        self.assertEqual(len(purchase), 1)
        purchase.button_confirm()
        picking = purchase.picking_ids
        self.assertEqual(len(picking), 1)
        self.assertEqual(picking.picking_type_code, "dropship")
        picking.write(
            {
                "l10n_ro_edi_stock_required": True,
                "l10n_ro_transport_partner_id": self.carrier_partner.id,
                "l10n_ro_edi_stock_operation_type": "30",
                "l10n_ro_edi_stock_operation_scope": "101",
                "l10n_ro_edi_stock_start_loc_type": "location",
                "l10n_ro_edi_stock_end_loc_type": "location",
                "l10n_ro_edi_stock_vehicle_number": "CJ01ABC",
            }
        )
        self.picking = picking
        self.assertTrue(self._send().called, picking.l10n_ro_edi_stock_document_ids.mapped("message"))
        self.assertEqual(picking.l10n_ro_edi_stock_state, "stock_sent")
        self.assertNotEqual(picking.state, "done")
