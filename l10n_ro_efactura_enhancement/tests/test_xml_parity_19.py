# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from lxml import etree

from odoo import Command
from odoo.tests import tagged

from odoo.addons.l10n_ro_edi.tests.common import TestROEdiCommon

NS = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


@tagged("post_install_l10n", "post_install", "-at_install")
class TestXmlParity19(TestROEdiCommon):
    """XML-ul CIUS-RO generat pe 20.0 trebuie sa ramana cel de pe 19.0.

    Odoo 20 a schimbat in l10n_ro_edi / account_edi_ubl_cii: PartyLegalEntity
    (CUI in loc de NRC), cbc:Name al articolului (product.name in loc de
    display_name), cac:CommodityClassification gol fara cod CPV si conturile
    bancare fara currency_id.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_data["company"].partner_id.nrc = "J40/1234/2010"
        cls.partner_ro.nrc = "J40/5678/2015"
        cls.product = cls.env["product.product"].create(
            {"name": "Laptop Business 14", "default_code": "LAP-14", "description_sale": "Garantie 36 luni"}
        )
        cls.icp = cls.env["ir.config_parameter"].sudo()

    def _invoice(self, move_type="out_invoice"):
        return self.create_invoice(
            move_type=move_type,
            invoice_line_ids=[
                Command.create(
                    {
                        "product_id": self.product.id,
                        "quantity": 2,
                        "price_unit": 100.0,
                        "tax_ids": [Command.set(self.tax_19.ids)],
                    }
                )
            ],
        )

    def _tree(self, invoice):
        xml, errors = self.env["account.edi.xml.ubl_ro"]._export_invoice(invoice)
        self.assertFalse(errors)
        return etree.fromstring(xml)

    def test_legal_entity_keeps_nrc(self):
        tree = self._tree(self._invoice())
        supplier = tree.find("cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID", NS)
        customer = tree.find("cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID", NS)
        self.assertEqual(supplier.text, "J40/1234/2010")
        self.assertEqual(customer.text, "J40/5678/2015")

    def test_item_name_is_product_display_name(self):
        tree = self._tree(self._invoice())
        item = tree.find("cac:InvoiceLine/cac:Item", NS)
        self.assertEqual(item.findtext("cbc:Name", namespaces=NS), "[LAP-14] Laptop Business 14")
        self.assertEqual(item.findtext("cbc:Description", namespaces=NS), "Garantie 36 luni")

    def test_no_empty_commodity_classification(self):
        tree = self._tree(self._invoice())
        self.assertIsNone(tree.find("cac:InvoiceLine/cac:Item/cac:CommodityClassification", NS))

    def test_replace_unit_uom_on_credit_note(self):
        self.icp.set_str("efactura.replace_unit_uom", "'H87'")
        tree = self._tree(self._invoice(move_type="out_refund"))
        quantity = tree.find("cac:CreditNoteLine/cbc:CreditedQuantity", NS)
        self.assertEqual(quantity.get("unitCode"), "H87")

    def test_get_all_banks_without_currency_field(self):
        # factura se posteaza inainte de a crea contul (un cont nou, neincrezut,
        # ar bloca postarea), apoi XML-ul il preia prin efactura.get_all_banks
        invoice = self._invoice()
        bank = self.env["res.partner.bank"].create(
            {
                "partner_id": self.company_data["company"].partner_id.id,
                "account_number": "RO49AAAA1B31007593840000",
                "l10n_ro_print_report": True,
            }
        )
        self.icp.set_str("efactura.get_all_banks", "True")
        tree = self._tree(invoice)
        ids = [node.text for node in tree.findall("cac:PaymentMeans/cac:PayeeFinancialAccount/cbc:ID", NS)]
        self.assertIn(bank.sanitized_account_number, ids)

    def test_empty_parameter_value_is_false(self):
        """get_str intoarce '' pentru o valoare goala; nu trebuie sa crape safe_eval."""
        self.icp.set_str("efactura.use_line_description", "")
        self._tree(self._invoice())
