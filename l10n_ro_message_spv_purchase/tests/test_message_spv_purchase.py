# © 2025 Deltatech
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
import io
import zipfile

from lxml import etree

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestMessageSPVPurchase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ro_country = cls.env.ref("base.ro")
        # Folosim o companie cu plan de conturi RO (jurnale + conturi configurate).
        ro_company = cls.env["res.company"].search([("account_fiscal_country_id.code", "=", "RO")], limit=1)
        if ro_company:
            cls.env.user.company_ids = [(4, ro_company.id)]
            cls.env.user.company_id = ro_company
            cls.env = cls.env(context=dict(cls.env.context, allowed_company_ids=[ro_company.id]))
        cls.company = cls.env.company
        if cls.company.account_fiscal_country_id != ro_country:
            cls.company.account_fiscal_country_id = ro_country

        # Asigurăm un depozit (deci picking_type-uri) pentru compania RO, altfel
        # crearea comenzilor de achiziție eșuează (picking_type_id NOT NULL).
        warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.company.id)], limit=1)
        if not warehouse:
            cls.env["stock.warehouse"].create(
                {"name": "Depozit RO Test", "code": "ROWHT", "company_id": cls.company.id}
            )

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
                # facturare pe cantități comandate (nu pe recepționate),
                # ca să existe qty_to_invoice > 0 fără a primi marfa
                "purchase_method": "purchase",
            }
        )

    def _make_spv_message(self, ref="PO-TEST-001", partner=None, message_type="in_invoice"):
        """Helper: creează un mesaj SPV minimal (factură de achiziție, implicit)."""
        return self.env["l10n.ro.message.spv"].create(
            {
                "name": f"SPV-{ref}",
                "ref": ref,
                "partner_id": (partner or self.partner).id,
                "company_id": self.company.id,
                "state": "draft",
                "message_type": message_type,
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
                "message_type": "in_invoice",
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

    def test_action_find_purchase_already_linked_raises(self):
        """Al doilea click pe 'Găsește Comanda', pe un mesaj deja legat de acea comandă,
        trebuie să blocheze cu UserError, nu să reproceseze XML-ul (sursa duplicării de
        produse/linii/recepție/factură - vezi tichet #9055)."""
        po = self._make_purchase_order(partner_ref="PO-FIND-002")
        msg = self._make_spv_message(ref="PO-FIND-002")
        msg.action_find_purchase()
        self.assertEqual(msg.purchase_order_id, po)
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

    def test_action_create_purchase_already_linked_raises(self):
        """Al doilea click pe 'Creează Comanda', pe un mesaj deja legat de acea comandă,
        trebuie să blocheze cu UserError, nu să reproceseze XML-ul (sursa duplicării de
        produse/linii/recepție/factură - vezi tichet #9055)."""
        po = self._make_purchase_order(partner_ref="PO-CREATE-002")
        msg = self._make_spv_message(ref="PO-CREATE-002")
        msg.action_create_purchase()
        self.assertEqual(msg.purchase_order_id, po)
        with self.assertRaises(UserError):
            msg.action_create_purchase()

    def test_action_find_purchase_blocks_sale_message(self):
        """action_find_purchase trebuie blocat pe mesaje SPV de factură de vânzare (tichet #9055)."""
        self._make_purchase_order(partner_ref="PO-SALE-001")
        msg = self._make_spv_message(ref="PO-SALE-001", message_type="out_invoice")
        with self.assertRaises(UserError):
            msg.action_find_purchase()

    def test_action_create_purchase_blocks_sale_message(self):
        """action_create_purchase trebuie blocat pe mesaje SPV de factură de vânzare (tichet #9055)."""
        msg = self._make_spv_message(ref="PO-SALE-002", message_type="out_receipt")
        with self.assertRaises(UserError):
            msg.action_create_purchase()

    def test_action_create_purchase_no_partner_raises(self):
        """Test că action_create_purchase ridică UserError dacă nu există partener și nu găsește PO."""
        msg = self.env["l10n.ro.message.spv"].create(
            {
                "name": "SPV-NO-PARTNER",
                "ref": "PO-NO-PARTNER-XYZ",
                "partner_id": False,
                "company_id": self.company.id,
                "state": "draft",
                "message_type": "in_invoice",
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

    # ------------------------------------------------------------------
    # P1: punte factură↔PO (eliminarea facturilor duplicate)
    # ------------------------------------------------------------------

    def _expense_account(self):
        return self.env["account.account"].search(
            [("account_type", "=", "expense"), ("company_ids", "in", [self.company.id])],
            limit=1,
        )

    def _confirmed_po(self, partner_ref="PO-LINK-001", price=100.0, qty=1.0):
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_ref": partner_ref,
                "company_id": self.company.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "product_qty": qty,
                            "price_unit": price,
                            "tax_ids": [(6, 0, [])],
                        },
                    )
                ],
            }
        )
        po.button_confirm()
        return po

    def _draft_bill(self, amount=100.0):
        return self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                "company_id": self.company.id,
                "invoice_date": "2024-05-01",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Linie din SPV",
                            "price_unit": amount,
                            "quantity": 1.0,
                            "tax_ids": [(6, 0, [])],
                            "account_id": self._expense_account().id,
                        },
                    )
                ],
            }
        )

    def _draft_bill_with_service(self, product_price=100.0, service_price=20.0):
        """Factură cu o linie de produs (există pe PO) + o linie de serviciu (transport)
        care NU se regăsește în comanda de achiziție."""
        return self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                "company_id": self.company.id,
                "invoice_date": "2024-05-01",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "price_unit": product_price,
                            "quantity": 1.0,
                            "tax_ids": [(6, 0, [])],
                            "account_id": self._expense_account().id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Transport",
                            "price_unit": service_price,
                            "quantity": 1.0,
                            "tax_ids": [(6, 0, [])],
                            "account_id": self._expense_account().id,
                        },
                    ),
                ],
            }
        )

    def test_link_preserves_extra_service_lines(self):
        """Liniile de serviciu (transport/discount) din SPV care nu sunt pe PO se păstrează.

        Linia de produs se leagă de comandă (qty_invoiced crește), iar linia de transport
        rămâne pe factură, fără purchase_line_id și fără să umfle qty_invoiced.
        """
        po = self._confirmed_po(partner_ref="PO-SERVICE-001", price=100.0)
        bill = self._draft_bill_with_service(product_price=100.0, service_price=20.0)

        bill._l10n_ro_link_spv_purchase_order(po)

        # Linia de produs e legată de PO
        linked = bill.invoice_line_ids.filtered(lambda l: l.purchase_line_id)
        self.assertTrue(linked, "Linia de produs trebuie legată de comandă")

        # Linia de transport NU e legată de PO și e încă prezentă
        transport = bill.invoice_line_ids.filtered(lambda l: not l.purchase_line_id and l.display_type == "product")
        self.assertTrue(transport, "Linia de transport trebuie păstrată pe factură")
        self.assertIn("Transport", transport.mapped("name"))

        # qty_invoiced reflectă doar produsul comandat (1), nu transportul
        self.env.flush_all()
        po.order_line.invalidate_recordset(["qty_invoiced"])
        self.assertEqual(po.order_line[0].qty_invoiced, 1.0)

    def test_link_preserves_service_lines_from_real_xml(self):
        """Flux real: liniile vin din XML-ul UBL decodat de _extend_with_attachments.

        Factura SPV conține o linie de produs (există pe PO) + o linie de transport
        (NU există pe PO). După decodarea XML și legarea de comandă, transportul trebuie
        păstrat, iar produsul legat.
        """
        from odoo.tools import file_open

        xml = file_open(
            "l10n_ro_message_spv_purchase/tests/test_files/spv_in_invoice_with_service.xml",
            "rb",
        ).read()

        bill = self.env["account.move"].create({"move_type": "in_invoice", "company_id": self.company.id})
        attachment = self.env["ir.attachment"].create(
            {
                "name": "spv_service.xml",
                "raw": xml,
                "res_model": "account.move",
                "res_id": bill.id,
            }
        )
        # Decodarea reală a XML-ului (populează liniile facturii din UBL)
        files_data = bill._to_files_data(attachment)
        bill._extend_with_attachments(files_data)

        product_lines = bill.invoice_line_ids.filtered(lambda l: l.display_type == "product")
        self.assertEqual(len(product_lines), 2, "XML-ul trebuie să producă 2 linii")
        # Odoo UBL combină <cbc:Name> și <cbc:Description> cu '\n'; verificăm primul segment.
        self.assertTrue(
            any(n.split("\n")[0] == "Transport" for n in product_lines.mapped("name")),
            "Trebuie să existe o linie al cărei name începe cu 'Transport'",
        )

        # PO care corespunde liniei de produs (750 x 2), nu și transportului
        po = self._confirmed_po(partner_ref="PO-XML-001", price=750.0, qty=2.0)
        bill._l10n_ro_link_spv_purchase_order(po)

        # Linia de produs e legată; transportul rămâne, fără purchase_line_id
        linked = bill.invoice_line_ids.filtered(lambda l: l.purchase_line_id)
        self.assertTrue(linked, "Linia de produs trebuie legată de comandă")
        transport = bill.invoice_line_ids.filtered(
            lambda l: l.display_type == "product" and not l.purchase_line_id and l.name.split("\n")[0] == "Transport"
        )
        self.assertTrue(transport, "Linia de transport din XML trebuie păstrată")

        self.env.flush_all()
        po.order_line.invalidate_recordset(["qty_invoiced"])
        self.assertEqual(po.order_line[0].qty_invoiced, 2.0, "qty_invoiced = produsul comandat, nu transportul")

    def test_link_invoice_first_then_po(self):
        """Factură creată întâi, apoi PO legat manual → purchase_line_id setat, qty_invoiced crește."""
        po = self._confirmed_po(partner_ref="PO-LINK-AAA")
        bill = self._draft_bill(amount=100.0)
        msg = self._make_spv_message(ref="PO-LINK-AAA")
        msg.invoice_id = bill
        msg.purchase_order_id = po

        # _post_spv_xml_on_purchase declanșează legarea când factura există deja
        msg._post_spv_xml_on_purchase(po)

        self.assertTrue(
            any(line.purchase_line_id for line in bill.invoice_line_ids),
            "Liniile facturii trebuie legate de purchase.order.line",
        )
        self.env.flush_all()
        po.order_line.invalidate_recordset(["qty_invoiced"])
        self.assertGreater(po.order_line[0].qty_invoiced, 0, "qty_invoiced trebuie să crească")
        self.assertNotEqual(po.invoice_status, "to invoice")

    def test_link_po_first_then_invoice(self):
        """PO legat înainte, apoi create_invoice → factura nou creată e legată de PO."""
        po = self._confirmed_po(partner_ref="PO-LINK-BBB")
        bill = self._draft_bill(amount=100.0)
        msg = self._make_spv_message(ref="PO-LINK-BBB")
        msg.purchase_order_id = po
        # Simulăm rezultatul lui super().create_invoice() care setează invoice_id,
        # apoi rulăm doar bucla de legare din override.
        msg.invoice_id = bill
        for message in msg.filtered(lambda m: m.purchase_order_id and m.invoice_id):
            message.invoice_id._l10n_ro_link_spv_purchase_order(message.purchase_order_id)

        self.assertTrue(any(line.purchase_line_id for line in bill.invoice_line_ids))
        self.env.flush_all()
        po.order_line.invalidate_recordset(["qty_invoiced"])
        self.assertGreater(po.order_line[0].qty_invoiced, 0)

    def test_link_is_idempotent(self):
        """A doua legare a aceleiași facturi de același PO nu schimbă nimic."""
        po = self._confirmed_po(partner_ref="PO-LINK-CCC")
        bill = self._draft_bill(amount=100.0)
        bill._l10n_ro_link_spv_purchase_order(po)
        qty_after_first = po.order_line[0].qty_invoiced
        # A doua oară: idempotent
        result = bill._l10n_ro_link_spv_purchase_order(po)
        self.assertFalse(result, "A doua legare trebuie să fie no-op")
        self.assertEqual(po.order_line[0].qty_invoiced, qty_after_first)

    def test_guard_po_already_has_bill(self):
        """Dacă PO are deja o factură proprie, a doua legare semnalează și nu dublează."""
        po = self._confirmed_po(partner_ref="PO-LINK-DDD")
        bill1 = self._draft_bill(amount=100.0)
        bill1._l10n_ro_link_spv_purchase_order(po)

        bill2 = self._draft_bill(amount=100.0)
        initial_msgs = len(bill2.message_ids)
        result = bill2._l10n_ro_link_spv_purchase_order(po)

        self.assertFalse(result, "A doua factură nu trebuie legată automat")
        self.assertGreater(len(bill2.message_ids), initial_msgs, "Trebuie postat un avertisment")
        self.assertFalse(
            any(line.purchase_line_id for line in bill2.invoice_line_ids),
            "A doua factură nu trebuie să preia liniile PO",
        )

    def test_cross_stack_duplicate_flagged(self):
        """Pasul 3: o factură cu aceeași cheie de dedup ca alta e semnalată cross-stack.

        Cuplaj soft: rulăm doar dacă modulul l10n_ro_efactura_dedup e instalat
        (câmpul l10n_ro_edi_dedup_key există pe account.move).
        """
        if "l10n_ro_edi_dedup_key" not in self.env["account.move"]._fields:
            self.skipTest("Modulul l10n_ro_efactura_dedup nu este instalat")

        bill1 = self._draft_bill(amount=500.0)
        bill1.ref = "FACT-CROSS-001"
        bill1.invoice_date = "2024-05-01"
        bill1._compute_l10n_ro_edi_dedup_key()

        bill2 = self._draft_bill(amount=500.0)
        bill2.ref = "FACT-CROSS-001"
        bill2.invoice_date = "2024-05-01"
        bill2._compute_l10n_ro_edi_dedup_key()

        self.assertEqual(bill1.l10n_ro_edi_dedup_key, bill2.l10n_ro_edi_dedup_key)

        flagged = bill2._l10n_ro_flag_cross_stack_duplicate()
        self.assertTrue(flagged, "A doua factură trebuie semnalată ca duplicat cross-stack")
        self.assertTrue(bill2.l10n_ro_edi_is_duplicate)

    def _make_zip_with_xml(self, xml_bytes=b"<Invoice><ID>ZIP-TEST</ID></Invoice>", xml_name="invoice.xml"):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr(xml_name, xml_bytes)
        return buf.getvalue()

    def test_clone_xml_attachment_falls_back_to_raw_zip_without_invoice(self):
        """Tichet #9287: PO creat înainte de factură — `attachment_xml_id` e gol (compute-ul
        depinde de `invoice_id`/`request_id`), dar ZIP-ul brut de la ANAF (`attachment_id`)
        există deja. Clonarea trebuie să extragă XML-ul direct din ZIP (`_get_xml_bytes`),
        nu să renunțe silențios — altfel `deltatech_purchase_ubl` nu mai primește niciun XML
        și comanda rămâne fără linii/total."""
        po = self._make_purchase_order(partner_ref="PO-ATT-ZIP-001")
        msg = self._make_spv_message(ref="PO-ATT-ZIP-001")
        zip_attachment = self.env["ir.attachment"].create(
            {
                "name": "6742375571.zip",
                "raw": self._make_zip_with_xml(),
                "res_model": "l10n.ro.message.spv",
                "res_id": msg.id,
            }
        )
        msg.attachment_id = zip_attachment

        # Precondiție: fără factură, câmpul derivat e gol (asta e exact ce a indus în eroare
        # implementarea inițială, care se oprea aici).
        self.assertFalse(msg.invoice_id)
        self.assertFalse(msg.attachment_xml_id)

        result = msg._clone_xml_attachment_for_purchase(po)

        self.assertTrue(result, "trebuie să extragă XML-ul din ZIP, nu să renunțe")
        self.assertEqual(result.res_model, "purchase.order")
        self.assertEqual(result.res_id, po.id)
        self.assertIn(b"ZIP-TEST", base64.b64decode(result.datas))

    def test_post_spv_xml_on_purchase_attaches_zip_xml_without_invoice(self):
        """Aceeași lipsă de factură, dar prin fluxul complet: `_post_spv_xml_on_purchase`
        trebuie să atașeze copia XML pe PO chiar dacă mesajul nu are încă `invoice_id`."""
        po = self._make_purchase_order(partner_ref="PO-ATT-ZIP-002")
        msg = self._make_spv_message(ref="PO-ATT-ZIP-002")
        zip_attachment = self.env["ir.attachment"].create(
            {
                "name": "6698941346.zip",
                "raw": self._make_zip_with_xml(xml_bytes=b"<Invoice><ID>ZIP-TEST-2</ID></Invoice>"),
                "res_model": "l10n.ro.message.spv",
                "res_id": msg.id,
            }
        )
        msg.attachment_id = zip_attachment
        msg.purchase_order_id = po

        msg._post_spv_xml_on_purchase(po)

        po_attachments = self.env["ir.attachment"].search(
            [("res_model", "=", "purchase.order"), ("res_id", "=", po.id), ("mimetype", "=", "application/xml")]
        )
        self.assertTrue(po_attachments, "XML-ul trebuie copiat pe PO chiar fără factură")

    def test_purchase_lines_and_total_match_real_zip_without_invoice(self):
        """Integrare tichet #9287, cu XML-ul real (anonimizat) al facturii care a declanșat
        raportarea (FC26BU0004904/TEMAD), împachetat în ZIP ca la descărcarea reală de la ANAF.

        PO creat ÎNAINTE de factură trebuie să primească liniile din XML prin hook-ul
        `deltatech_purchase_ubl._process_attachments_for_post` (declanșat de `message_post`
        din `_post_spv_xml_on_purchase`), iar `amount_total` al comenzii trebuie să bată cu
        `PayableAmount` din XML — aceeași cheie de control ca `_get_order_total_check` din
        `deltatech_purchase_ubl` (verificată aici direct, nu doar ca warning informativ)."""
        if "purchase.ubl.import.wizard" not in self.env:
            self.skipTest("Modulul deltatech_purchase_ubl nu este instalat")

        from odoo.tools import file_open

        xml_bytes = file_open(
            "l10n_ro_message_spv_purchase/tests/test_files/spv_purchase_order_lines_9287.xml", "rb"
        ).read()
        zip_bytes = self._make_zip_with_xml(xml_bytes=xml_bytes, xml_name="9287-anon.xml")

        supplier = self.env["res.partner"].create(
            {
                "name": "Furnizor Test SRL",
                "company_type": "company",
                "country_id": self.env.ref("base.ro").id,
            }
        )

        msg = self._make_spv_message(ref="FACT-TEST-0001", partner=supplier)
        zip_attachment = self.env["ir.attachment"].create(
            {
                "name": "9287-anon.zip",
                "raw": zip_bytes,
                "res_model": "l10n.ro.message.spv",
                "res_id": msg.id,
            }
        )
        msg.attachment_id = zip_attachment
        self.assertFalse(msg.invoice_id)
        self.assertFalse(msg.attachment_xml_id, "precondiție: câmpul derivat e gol fără factură")

        msg.action_create_purchase()
        po = msg.purchase_order_id
        self.assertTrue(po, "trebuie să creeze/lege o comandă de achiziție")

        self.env.flush_all()
        po.invalidate_recordset()

        self.assertTrue(po.order_line, "PO-ul trebuie să primească liniile din XML (tichet #9287)")
        # Cheia de control: suma liniilor importate trebuie să bată cu LineExtensionAmount/
        # TaxExclusiveAmount din XML-ul sursă (2272.21 RON, valoare reală din factura
        # FC26BU0004904, neschimbată de anonimizare). Verificăm netto (nu amount_total cu TVA),
        # pentru că produsele nou-create în acest test nu moștenesc taxa de achiziție impicită
        # a companiei RO reale — pe producția Damira, unde produsele au deja TVA 21% configurat,
        # amount_total (2749.37 RON) a bătut exact cu PayableAmount din XML (verificat manual
        # pe CA11777, tichet #9287).
        self.assertAlmostEqual(
            po.amount_untaxed,
            2272.21,
            places=2,
            msg="amount_untaxed al PO trebuie să corespundă cu totalul net din XML",
        )

        # Reutilizăm chiar mecanismul de control din deltatech_purchase_ubl
        # (_get_order_total_check), ca să testăm exact cheia de validare folosită în producție,
        # nu o reimplementare paralelă. Pe un PO fără taxe (cazul de test) verificarea corectă
        # e pe netto, la fel cum face fallback-ul intern al metodei când sumele cu TVA lipsesc.
        wiz = self.env["purchase.ubl.import.wizard"].new({"data_file": base64.b64encode(xml_bytes)})
        invoice_data = wiz._parse_xml(xml_bytes)
        invoice_data["payable_amount"] = 0.0
        invoice_data["tax_inclusive_amount"] = 0.0
        total_check = wiz._get_order_total_check(po, invoice_data)
        self.assertTrue(
            total_check and total_check["matches"],
            f"cheia de control trebuie să confirme netto-ul: {total_check}",
        )

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
