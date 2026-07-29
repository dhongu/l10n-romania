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
        # Client fara tara completata — cazul tipic de contact B2C intern.
        # country_id: False explicit, ca sa nu preia o valoare implicita
        # (ir.default pe res.partner.country_id) din baza pe care rulam.
        cls.no_country_partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner Fara Tara",
                "country_id": False,
                "city": "Bucuresti",
                "street": "Str. Test 1",
            }
        )
        cls.currency_ron = cls.env.ref("base.RON")
        cls.currency_eur = cls.env.ref("base.EUR")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product SPV",
            }
        )

    def _create_draft_invoice(self, partner=None, currency=None):
        # Facturile catre parteneri fara tara nu se pot confirma (check_partner),
        # deci regula de destinatie se testeaza pe ciorne.
        vals = {
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
        if currency:
            vals["currency_id"] = currency.id
        return self.env["account.move"].create(vals)

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

    def test_ro_edi_not_applicable_for_foreign_partner(self):
        """Facturile catre clienti non-RO nu mai sunt eligibile pentru SPV in Send & Print."""
        from odoo.addons.l10n_ro_edi.models.account_move_send import (
            AccountMoveSend as NativeAccountMoveSend,
        )

        foreign_invoice = self._create_posted_invoice(partner=self.foreign_partner)
        send = self.env["account.move.send"]
        # Verificarea nativa e forțată pe True, ca sa fie clar ca refuzul vine
        # din override-ul nostru, nu dintr-o alta condiție a core-ului.
        with patch.object(NativeAccountMoveSend, "_is_ro_edi_applicable", return_value=True) as native:
            self.assertFalse(send._is_ro_edi_applicable(foreign_invoice))
            native.assert_not_called()
            # In O19 bifa "Send E-Factura to SPV" din wizard vine din extra EDIs
            # implicite, deci nu trebuie sa mai apara deloc pentru clienti non-RO.
            self.assertNotIn("ro_edi", send._get_default_extra_edis(foreign_invoice))

    def test_ro_edi_applicability_delegated_for_ro_partner(self):
        """Pentru clientii RO, override-ul deleaga catre verificarea nativa."""
        from odoo.addons.l10n_ro_edi.models.account_move_send import (
            AccountMoveSend as NativeAccountMoveSend,
        )

        ro_invoice = self._create_posted_invoice()
        send = self.env["account.move.send"]
        with patch.object(NativeAccountMoveSend, "_is_ro_edi_applicable", return_value=True) as native:
            self.assertTrue(send._is_ro_edi_applicable(ro_invoice))
            native.assert_called_once()

    def test_spv_target_follows_partner_country(self):
        """Cu tara completata pe partener, ea decide destinatia facturii."""
        self.assertTrue(self._create_draft_invoice()._l10n_ro_is_spv_target())
        self.assertFalse(self._create_draft_invoice(partner=self.foreign_partner)._l10n_ro_is_spv_target())

    def test_spv_target_no_country_ron_is_domestic(self):
        """Partener fara tara + factura in RON = client considerat roman."""
        invoice = self._create_draft_invoice(partner=self.no_country_partner, currency=self.currency_ron)
        self.assertFalse(invoice.commercial_partner_id.country_id)
        self.assertTrue(invoice._l10n_ro_is_spv_target())

    def test_spv_target_no_country_foreign_currency_is_not_domestic(self):
        """Partener fara tara + factura in alta valuta nu se considera intern."""
        invoice = self._create_draft_invoice(partner=self.no_country_partner, currency=self.currency_eur)
        self.assertFalse(invoice._l10n_ro_is_spv_target())

    def test_spv_target_domain_matches_python_rule(self):
        """Domeniul de căutare selectează exact aceleași facturi ca regula Python.

        Cronul si dashboard-ul filtreaza prin domeniu, iar wizardul si butonul
        manual prin metoda; daca cele doua ar diverge, o factura ar fi trimisa
        pe o cale si ignorata pe alta.
        """
        invoices = (
            self._create_draft_invoice()
            | self._create_draft_invoice(partner=self.foreign_partner)
            | self._create_draft_invoice(partner=self.no_country_partner, currency=self.currency_ron)
            | self._create_draft_invoice(partner=self.no_country_partner, currency=self.currency_eur)
        )
        Move = self.env["account.move"]
        by_domain = Move.search([("id", "in", invoices.ids), *Move._l10n_ro_spv_target_domain()])
        by_method = invoices.filtered(lambda m: m._l10n_ro_is_spv_target())
        self.assertEqual(by_domain, by_method)
        # Verificare de sanitate: setul nu e nici gol, nici totul.
        self.assertEqual(len(by_method), 2)

    def test_ro_edi_applicable_for_no_country_ron_invoice(self):
        """Pentru partener fara tara facturat in RON, override-ul deleaga catre core."""
        from odoo.addons.l10n_ro_edi.models.account_move_send import (
            AccountMoveSend as NativeAccountMoveSend,
        )

        invoice = self._create_draft_invoice(partner=self.no_country_partner, currency=self.currency_ron)
        send = self.env["account.move.send"]
        with patch.object(NativeAccountMoveSend, "_is_ro_edi_applicable", return_value=True) as native:
            self.assertTrue(send._is_ro_edi_applicable(invoice))
            native.assert_called_once()

    def test_ro_edi_not_applicable_for_no_country_foreign_currency(self):
        """Partener fara tara facturat in valuta nu mai primeste bifa SPV."""
        from odoo.addons.l10n_ro_edi.models.account_move_send import (
            AccountMoveSend as NativeAccountMoveSend,
        )

        invoice = self._create_draft_invoice(partner=self.no_country_partner, currency=self.currency_eur)
        send = self.env["account.move.send"]
        with patch.object(NativeAccountMoveSend, "_is_ro_edi_applicable", return_value=True) as native:
            self.assertFalse(send._is_ro_edi_applicable(invoice))
            native.assert_not_called()
            self.assertNotIn("ro_edi", send._get_default_extra_edis(invoice))

    def test_send_mails_flags_validated_email_sent(self):
        """Un e-mail trimis prin account.move.send marcheaza factura, ca cronul
        de dupa validarea SPV sa nu mai trimita al doilea e-mail."""
        self.partner.email = "client@example.com"
        invoice = self._create_posted_invoice()
        self.assertFalse(invoice.l10n_ro_spv_validated_email_sent)
        send = self.env["account.move.send"]
        moves_data = {invoice: {"mail_template": self.env["mail.template"], "mail_lang": "en_US"}}
        with (
            patch.object(type(send), "_generate_dynamic_reports", return_value=None),
            # Fara parametri de mail, bucla nativa sare peste trimiterea efectiva.
            patch.object(type(send), "_get_mail_params", return_value=None),
        ):
            send._send_mails(moves_data)
        self.assertTrue(invoice.l10n_ro_spv_validated_email_sent)

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

    def test_edi_no_auto_bill_default_false(self):
        """Implicit, auto-importul facturilor primite din SPV rămâne activ (default False)."""
        defaults = self.env["res.company"].default_get(["l10n_ro_edi_no_auto_bill"])
        self.assertFalse(defaults.get("l10n_ro_edi_no_auto_bill"))

    def test_edi_no_auto_bill_config(self):
        """Test că setarea l10n_ro_edi_no_auto_bill se salvează corect pe companie."""
        self.company.l10n_ro_edi_no_auto_bill = True
        self.assertTrue(self.company.l10n_ro_edi_no_auto_bill)
        self.company.l10n_ro_edi_no_auto_bill = False
        self.assertFalse(self.company.l10n_ro_edi_no_auto_bill)

    def test_no_auto_bill_true_skips_native_import(self):
        """Cu flagul activ, override-ul nu mai apelează logica nativă de creare a
        facturilor primite (restul cron-ului „Synchronize with ANAF" rămâne neatins)."""
        from odoo.addons.l10n_ro_edi.models.account_move import (
            AccountMove as NativeAccountMove,
        )

        self.company.l10n_ro_edi_no_auto_bill = True
        with patch.object(NativeAccountMove, "_l10n_ro_edi_process_bill_messages") as native:
            self.env["account.move"].with_company(self.company)._l10n_ro_edi_process_bill_messages([{"id": "1"}])
            native.assert_not_called()

    def test_no_auto_bill_false_delegates_to_native(self):
        """Fără flag (implicit), override-ul deleagă către logica nativă de import."""
        from odoo.addons.l10n_ro_edi.models.account_move import (
            AccountMove as NativeAccountMove,
        )

        self.company.l10n_ro_edi_no_auto_bill = False
        with patch.object(NativeAccountMove, "_l10n_ro_edi_process_bill_messages", return_value=None) as native:
            self.env["account.move"].with_company(self.company)._l10n_ro_edi_process_bill_messages([{"id": "1"}])
            native.assert_called_once()
