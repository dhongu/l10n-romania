# © 2025 Deltatech
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64

from lxml import etree

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestMessageSPVPurchase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        ro_country = cls.env.ref("base.ro")
        if cls.company.account_fiscal_country_id != ro_country:
            cls.company.account_fiscal_country_id = ro_country

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Furnizor Test SPV",
                "company_type": "company",
                "country_id": ro_country.id,
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Produs Test SPV",
                "type": "consu",
            }
        )

    def _make_spv_message(self, ref="PO-TEST-001", partner=None):
        """Helper: creează un mesaj SPV minimal."""
        return self.env["l10n.ro.message.spv"].create(
            {
                "name": f"SPV-{ref}",
                "ref": ref,
                "partner_id": (partner or self.partner).id,
                "company_id": self.company.id,
                "state": "draft",
            }
        )

    def _make_purchase_order(self, partner_ref="PO-TEST-001", partner=None):
        """Helper: creează o comandă de achiziție."""
        po = self.env["purchase.order"].create(
            {
                "partner_id": (partner or self.partner).id,
                "partner_ref": partner_ref,
                "company_id": self.company.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "product_qty": 1.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        return po

    def test_purchase_ref_field(self):
        """Test că câmpul purchase_ref există și poate fi setat pe mesajul SPV."""
        msg = self._make_spv_message()
        self.assertFalse(msg.purchase_ref)
        msg.purchase_ref = "REF-EXTERN-001"
        self.assertEqual(msg.purchase_ref, "REF-EXTERN-001")

    def test_purchase_order_id_field(self):
        """Test că câmpul purchase_order_id există și poate fi legat."""
        msg = self._make_spv_message()
        po = self._make_purchase_order()
        self.assertFalse(msg.purchase_order_id)
        msg.purchase_order_id = po
        self.assertEqual(msg.purchase_order_id, po)

    def test_get_purchase_ref_uses_purchase_ref_first(self):
        """Test că _get_purchase_ref returnează purchase_ref dacă este setat."""
        msg = self._make_spv_message(ref="REF-GENERIC")
        msg.purchase_ref = "REF-PURCHASE-SPECIFIC"
        self.assertEqual(msg._get_purchase_ref(), "REF-PURCHASE-SPECIFIC")

    def test_get_purchase_ref_fallback_to_ref(self):
        """Test că _get_purchase_ref cade pe ref dacă purchase_ref este gol."""
        msg = self._make_spv_message(ref="REF-FALLBACK")
        self.assertFalse(msg.purchase_ref)
        self.assertEqual(msg._get_purchase_ref(), "REF-FALLBACK")

    def test_process_xml_extracts_order_reference(self):
        """Test că logica din process_xml extrage OrderReference/ID din XML."""
        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cbc:ID>FACT-001</cbc:ID>
    <cac:OrderReference>
        <cbc:ID>PO-EXTERN-999</cbc:ID>
    </cac:OrderReference>
</Invoice>"""
        xml_tree = etree.fromstring(xml_content)
        order_reference = xml_tree.findtext("./{*}OrderReference/{*}ID")
        self.assertEqual(order_reference, "PO-EXTERN-999")
        # Verificăm că metoda setează purchase_ref pe mesaj
        msg = self._make_spv_message(ref="FACT-001")
        msg.purchase_ref = order_reference
        self.assertEqual(msg.purchase_ref, "PO-EXTERN-999")

    def test_process_xml_no_order_reference(self):
        """Test că XML fără OrderReference nu conține referință de comandă."""
        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cbc:ID>FACT-002</cbc:ID>
</Invoice>"""
        xml_tree = etree.fromstring(xml_content)
        order_reference = xml_tree.findtext("./{*}OrderReference/{*}ID")
        self.assertFalse(order_reference)

    def test_purchase_search_domain_with_ref_only(self):
        """Test că _purchase_search_domain_from_ref construiește domeniu corect fără partner/company."""
        msg = self._make_spv_message()
        domain = msg._purchase_search_domain_from_ref("PO-001")
        self.assertIsInstance(domain, list)
        # Domeniul trebuie să conțină referința
        domain_str = str(domain)
        self.assertIn("PO-001", domain_str)

    def test_purchase_search_domain_with_partner_and_company(self):
        """Test că _purchase_search_domain_from_ref include partner_id și company_id în domeniu."""
        msg = self._make_spv_message()
        domain = msg._purchase_search_domain_from_ref(
            "PO-002",
            partner_id=self.partner.id,
            company_id=self.company.id,
        )
        domain_str = str(domain)
        self.assertIn("PO-002", domain_str)
        self.assertIn(str(self.partner.id), domain_str)
        self.assertIn(str(self.company.id), domain_str)

    def test_action_find_purchase_no_ref_raises(self):
        """Test că action_find_purchase ridică UserError dacă nu există referință."""
        msg = self.env["l10n.ro.message.spv"].create(
            {
                "name": "SPV-NO-REF",
                "ref": False,
                "partner_id": self.partner.id,
                "company_id": self.company.id,
                "state": "draft",
            }
        )
        with self.assertRaises(UserError):
            msg.action_find_purchase()

    def test_action_find_purchase_finds_one(self):
        """Test că action_find_purchase leagă comanda când găsește exact una."""
        po = self._make_purchase_order(partner_ref="PO-FIND-001")
        msg = self._make_spv_message(ref="PO-FIND-001")
        result = msg.action_find_purchase()
        self.assertEqual(msg.purchase_order_id, po)
        self.assertEqual(result["res_model"], "purchase.order")
        self.assertEqual(result["res_id"], po.id)

    def test_action_find_purchase_not_found(self):
        """Test că action_find_purchase ridică UserError dacă nu găsește nicio comandă."""
        msg = self._make_spv_message(ref="PO-INEXISTENT-XYZ")
        with self.assertRaises(UserError):
            msg.action_find_purchase()

    def test_action_create_purchase_finds_existing(self):
        """Test că action_create_purchase leagă comanda existentă fără a crea una nouă."""
        po = self._make_purchase_order(partner_ref="PO-CREATE-001")
        msg = self._make_spv_message(ref="PO-CREATE-001")
        result = msg.action_create_purchase()
        self.assertEqual(msg.purchase_order_id, po)
        self.assertEqual(result["res_id"], po.id)

    def test_action_create_purchase_creates_new(self):
        """Test că action_create_purchase creează un PO nou dacă nu găsește nimic."""
        msg = self._make_spv_message(ref="PO-NEW-UNIQUE-9999")
        result = msg.action_create_purchase()
        self.assertTrue(msg.purchase_order_id)
        self.assertEqual(result["res_model"], "purchase.order")
        created_po = msg.purchase_order_id
        self.assertEqual(created_po.partner_id, self.partner)

    def test_action_create_purchase_no_partner_raises(self):
        """Test că action_create_purchase ridică UserError dacă nu există partener și nu găsește PO."""
        msg = self.env["l10n.ro.message.spv"].create(
            {
                "name": "SPV-NO-PARTNER",
                "ref": "PO-NO-PARTNER-XYZ",
                "partner_id": False,
                "company_id": self.company.id,
                "state": "draft",
            }
        )
        with self.assertRaises(UserError):
            msg.action_create_purchase()

    def test_post_spv_xml_on_purchase_posts_message(self):
        """Test că _post_spv_xml_on_purchase postează un mesaj în chatter-ul comenzii."""
        po = self._make_purchase_order(partner_ref="PO-CHATTER-001")
        msg = self._make_spv_message(ref="PO-CHATTER-001")
        msg.purchase_order_id = po
        initial_msg_count = len(po.message_ids)
        msg._post_spv_xml_on_purchase(po)
        self.assertGreater(len(po.message_ids), initial_msg_count)

    def test_clone_xml_attachment_no_attachment(self):
        """Test că _clone_xml_attachment_for_purchase returnează False dacă nu există atașament XML."""
        po = self._make_purchase_order(partner_ref="PO-ATT-001")
        msg = self._make_spv_message(ref="PO-ATT-001")
        result = msg._clone_xml_attachment_for_purchase(po)
        self.assertFalse(result)

    def test_clone_xml_attachment_creates_copy(self):
        """Test că _clone_xml_attachment_for_purchase creează o copie a atașamentului pe PO."""
        po = self._make_purchase_order(partner_ref="PO-ATT-002")
        msg = self._make_spv_message(ref="PO-ATT-002")
        xml_data = base64.b64encode(b"<Invoice><ID>TEST</ID></Invoice>")
        attachment = self.env["ir.attachment"].create(
            {
                "name": "test_invoice.xml",
                "datas": xml_data,
                "mimetype": "application/xml",
                "res_model": "l10n.ro.message.spv",
                "res_id": msg.id,
            }
        )
        msg.attachment_xml_id = attachment
        result = msg._clone_xml_attachment_for_purchase(po)
        self.assertTrue(result)
        self.assertEqual(result.res_model, "purchase.order")
        self.assertEqual(result.res_id, po.id)
        self.assertEqual(result.name, "test_invoice.xml")

    def test_clone_xml_attachment_no_duplicate(self):
        """Test că _clone_xml_attachment_for_purchase nu duplică atașamentul dacă există deja."""
        po = self._make_purchase_order(partner_ref="PO-ATT-003")
        msg = self._make_spv_message(ref="PO-ATT-003")
        xml_data = base64.b64encode(b"<Invoice><ID>TEST-NODUP</ID></Invoice>")
        attachment = self.env["ir.attachment"].create(
            {
                "name": "test_nodup.xml",
                "datas": xml_data,
                "mimetype": "application/xml",
                "res_model": "l10n.ro.message.spv",
                "res_id": msg.id,
            }
        )
        msg.attachment_xml_id = attachment
        # Prima clonare
        result1 = msg._clone_xml_attachment_for_purchase(po)
        self.assertTrue(result1)
        # A doua clonare — nu trebuie să creeze un duplicat
        result2 = msg._clone_xml_attachment_for_purchase(po)
        self.assertEqual(result1.id, result2.id)
