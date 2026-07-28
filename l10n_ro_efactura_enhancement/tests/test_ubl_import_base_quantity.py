# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from lxml import etree

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

NSMAP = {
    None: "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
}

LINE_TEMPLATE = """<cac:InvoiceLine
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
    <cbc:ID>{line_id}</cbc:ID>
    <cbc:InvoicedQuantity unitCode="{uom}">{quantity}</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount currencyID="RON">{line_amount}</cbc:LineExtensionAmount>
    <cac:Item>
        <cbc:Name>{name}</cbc:Name>
    </cac:Item>
    <cac:Price>
        <cbc:PriceAmount currencyID="RON">{price}</cbc:PriceAmount>
        {base_quantity}
    </cac:Price>
</cac:InvoiceLine>"""


@tagged("post_install", "-at_install")
class TestUblImportBaseQuantity(TransactionCase):
    """Import UBL: linia se recalculează din BT-131 când BT-149 e completat greșit."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ubl = cls.env["account.edi.ubl"]
        cls.currency = cls.env.ref("base.RON")

    def _parse_line(self, quantity, line_amount, price, base_quantity=None, uom="MTR", name="Produs test"):
        """Rulează pe o linie UBL pașii de import din core, cu override-ul nostru."""
        base_quantity_node = ""
        if base_quantity is not None:
            base_quantity_node = f'<cbc:BaseQuantity unitCode="{uom}">{base_quantity}</cbc:BaseQuantity>'
        line_tree = etree.fromstring(
            LINE_TEMPLATE.format(
                line_id="1",
                uom=uom,
                quantity=quantity,
                line_amount=line_amount,
                price=price,
                base_quantity=base_quantity_node,
                name=name,
            )
        )
        collected_values = {
            "line_tree": line_tree,
            "file_document_sign": 1,
            "currency_values": {"currency": self.currency},
            "logs": [],
            "to_write": {},
        }
        self.ubl._import_ubl_invoice_line_add_allowance_charges_values(collected_values)
        self.ubl._import_ubl_invoice_line_add_price_unit_quantity_discount(collected_values)
        return collected_values

    def _subtotal(self, to_write):
        return to_write["price_unit"] * to_write["quantity"] * (1 - to_write["discount"] / 100.0)

    def test_base_quantity_equal_to_invoiced_quantity_is_corrected(self):
        """BaseQuantity = InvoicedQuantity: prețul unitar se ia din BT-131, nu din BT-146/BT-149."""
        collected_values = self._parse_line(quantity=400, line_amount=504, price="1.26", base_quantity=400)
        to_write = collected_values["to_write"]

        self.assertEqual(to_write["quantity"], 400)
        self.assertAlmostEqual(to_write["price_unit"], 1.26, places=6)
        self.assertAlmostEqual(to_write["discount"], 0.0, places=6)
        self.assertAlmostEqual(self._subtotal(to_write), 504.0, places=2)
        self.assertTrue(collected_values["logs"], "corecția trebuie semnalată în logurile importului")

    def test_base_quantity_equal_to_invoiced_quantity_integer_price(self):
        """Același tipar, cu preț fără zecimale — toleranța de rotunjire nu maschează eroarea."""
        collected_values = self._parse_line(quantity=20, line_amount=60, price="3", base_quantity=20, uom="H87")
        to_write = collected_values["to_write"]

        self.assertEqual(to_write["quantity"], 20)
        self.assertAlmostEqual(to_write["price_unit"], 3.0, places=6)
        self.assertAlmostEqual(self._subtotal(to_write), 60.0, places=2)

    def test_valid_base_quantity_is_not_touched(self):
        """BaseQuantity > 1 folosit corect (preț pentru 5 bucăți) rămâne neatins."""
        collected_values = self._parse_line(quantity=6, line_amount=1500, price="1250", base_quantity=5, uom="H87")
        to_write = collected_values["to_write"]

        self.assertEqual(to_write["quantity"], 6)
        self.assertAlmostEqual(to_write["price_unit"], 250.0, places=6)
        self.assertAlmostEqual(self._subtotal(to_write), 1500.0, places=2)
        self.assertFalse(collected_values["logs"], "o linie consistentă nu trebuie semnalată")

    def test_without_base_quantity_is_not_touched(self):
        """Linie obișnuită, fără BT-149, rămâne neatinsă."""
        collected_values = self._parse_line(quantity=10, line_amount=125, price="12.5", uom="H87")
        to_write = collected_values["to_write"]

        self.assertEqual(to_write["quantity"], 10)
        self.assertAlmostEqual(to_write["price_unit"], 12.5, places=6)
        self.assertFalse(collected_values["logs"])

    def test_rounded_unit_price_stays_with_core_behaviour(self):
        """Preț unitar rotunjit la 2 zecimale: diferența mică rămâne pe seama core-ului."""
        # 30.36 / 100 = 0.3036, transmis rotunjit ca 0.30 — abatere legitimă de 0,36 lei.
        collected_values = self._parse_line(quantity=100, line_amount="30.36", price="0.30", uom="H87")
        to_write = collected_values["to_write"]

        self.assertAlmostEqual(to_write["price_unit"], 0.30, places=6)
        self.assertFalse(collected_values["logs"], "rotunjirea prețului nu e o inconsistență")
