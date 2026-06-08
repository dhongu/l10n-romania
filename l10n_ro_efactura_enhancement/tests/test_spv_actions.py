# ©  2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSpvActions(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner SPV",
                "country_id": cls.env.ref("base.ro").id,
                "state_id": cls.env.ref("base.RO_B").id,
                "city": "Bucuresti",
                "street": "Str. Test 1",
                "invoice_sending_method": "email",
            }
        )
        # Client companie din afara Romaniei (intracomunitar) cu VAT EU
        cls.foreign_partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner Foreign",
                "is_company": True,
                "country_id": cls.env.ref("base.ie").id,
                "city": "Dublin",
                "street": "Main Street 1",
                "vat": "IE6388047V",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product SPV",
            }
        )

    def _create_posted_invoice(self, partner=None):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": (partner or self.partner).id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        invoice.action_post()
        return invoice

    def test_action_send_to_spv_only_no_invoices(self):
        """Test că acțiunea ridică UserError dacă nu există facturi confirmate selectate."""
        draft_invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
            }
        )
        with self.assertRaises(UserError):
            draft_invoice.action_send_to_spv_only()

    def test_action_send_to_spv_only_calls_generate_and_send(self):
        """Test că action_send_to_spv_only apelează _generate_and_send_invoices cu sending_methods={'manual'}."""
        invoice = self._create_posted_invoice()
        with patch.object(
            type(self.env["account.move.send"]),
            "_generate_and_send_invoices",
        ) as mock_send:
            invoice.action_send_to_spv_only()
            mock_send.assert_called_once()
            args, kwargs = mock_send.call_args
            self.assertEqual(kwargs.get("sending_methods"), {"manual"})

    def test_action_send_to_spv_only_ignores_email_setting(self):
        """Test că acțiunea ignoră setarea email a partenerului (invoice_sending_method='email')."""
        self.assertEqual(self.partner.invoice_sending_method, "email")
        invoice = self._create_posted_invoice()
        with patch.object(
            type(self.env["account.move.send"]),
            "_generate_and_send_invoices",
        ) as mock_send:
            invoice.action_send_to_spv_only()
            args, kwargs = mock_send.call_args
            # Trebuie să fie 'manual', nu 'email'
            self.assertEqual(kwargs.get("sending_methods"), {"manual"})
        # Partenerul nu trebuie modificat
        self.assertEqual(self.partner.invoice_sending_method, "email")

    def test_action_send_to_spv_only_excludes_non_ro(self):
        """Test că facturile catre clienti non-RO sunt excluse de la trimiterea in SPV."""
        ro_invoice = self._create_posted_invoice()
        foreign_invoice = self._create_posted_invoice(partner=self.foreign_partner)
        invoices = ro_invoice | foreign_invoice
        with patch.object(
            type(self.env["account.move.send"]),
            "_generate_and_send_invoices",
        ) as mock_send:
            invoices.action_send_to_spv_only()
            args, kwargs = mock_send.call_args
            sent_invoices = args[0]
            # Doar factura RO trebuie trimisa, cea straina exclusa
            self.assertIn(ro_invoice, sent_invoices)
            self.assertNotIn(foreign_invoice, sent_invoices)

    def test_action_send_to_spv_only_all_non_ro_raises(self):
        """Test că acțiunea ridică UserError dacă toate facturile selectate sunt non-RO."""
        foreign_invoice = self._create_posted_invoice(partner=self.foreign_partner)
        with self.assertRaises(UserError):
            foreign_invoice.action_send_to_spv_only()

    def test_foreign_company_vat_not_prefixed_with_ro(self):
        """Test că VAT-ul unei companii straine nu este prefixat cu 'RO' in XML-ul e-Factura."""
        invoice = self._create_posted_invoice(partner=self.foreign_partner)
        xml_content, _errors = self.env["account.edi.xml.ubl_ro"]._export_invoice(invoice)
        self.assertIn(b"IE6388047V", xml_content)
        self.assertNotIn(b"ROIE6388047V", xml_content)

    def test_spv_cron_no_email_config(self):
        """Test că setarea l10n_ro_spv_cron_no_email se salvează corect pe companie."""
        self.company.l10n_ro_spv_cron_no_email = True
        self.assertTrue(self.company.l10n_ro_spv_cron_no_email)
        self.company.l10n_ro_spv_cron_no_email = False
        self.assertFalse(self.company.l10n_ro_spv_cron_no_email)
