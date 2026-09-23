# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from unittest.mock import patch

from odoo.tests import tagged

from odoo.addons.l10n_ro_edi.tests.common import TestROEdiCommon

SEND_PATH = "odoo.addons.l10n_ro_edi.models.account_move._request_ciusro_send_invoice"


@tagged("post_install_l10n", "post_install", "-at_install")
class TestCustomerCompanyVat(TestROEdiCommon):
    """O firmă din România fără CUI nu trebuie să plece în SPV.

    l10n_ro_edi completează CUI-ul lipsă al clientului cu ``0000000000000`` și,
    pe 19.0, nu mai blochează exportul. Pentru o persoană fizică e corect; pentru
    o firmă, factura ajunge la ANAF fără cumpărător identificat.
    """

    def _partner(self, **kwargs):
        vals = {
            "name": "Firma Fara CUI SRL",
            "is_company": True,
            "country_id": self.env.ref("base.ro").id,
            "state_id": self.env.ref("base.RO_B").id,
            "city": "SECTOR2",
            "zip": "020202",
            "street": "Strada Client, 5",
            "vat": False,
            "invoice_edi_format": "ciusro",
        }
        vals.update(kwargs)
        return self.env["res.partner"].with_context(no_vat_validation=True).create(vals)

    def _send(self, invoice):
        with patch(SEND_PATH, return_value={"key_loading": "123"}) as send:
            errors = invoice._l10n_ro_edi_send_invoice(b"<xml>test</xml>")
        return errors, send

    def test_company_without_vat_is_blocked_before_spv(self):
        invoice = self.create_invoice(partner_id=self._partner().id)
        errors, send = self._send(invoice)
        send.assert_not_called()
        self.assertTrue(any("CUI" in error for error in errors))

    def test_company_with_placeholder_vat_is_blocked(self):
        partner = self._partner(vat="0000000000000")
        invoice = self.create_invoice(partner_id=partner.id)
        errors, send = self._send(invoice)
        send.assert_not_called()
        self.assertTrue(any("CUI" in error for error in errors))

    def test_company_without_vat_fails_export_constraints(self):
        invoice = self.create_invoice(partner_id=self._partner().id)
        _xml, errors = self.env["account.edi.xml.ubl_ro"]._export_invoice(invoice)
        self.assertTrue(any("CUI" in str(error) for error in errors or []))

    def test_individual_without_vat_is_sent(self):
        partner = self._partner(name="Ion Popescu", is_company=False)
        invoice = self.create_invoice(partner_id=partner.id)
        self.assertFalse(invoice._l10n_ro_customer_vat_missing_error())
        _errors, send = self._send(invoice)
        send.assert_called_once()

    def test_company_with_vat_is_sent(self):
        partner = self._partner(vat="RO1234567897")
        invoice = self.create_invoice(partner_id=partner.id)
        self.assertFalse(invoice._l10n_ro_customer_vat_missing_error())
        _errors, send = self._send(invoice)
        send.assert_called_once()

    def test_foreign_company_without_vat_not_checked(self):
        partner = self._partner(
            country_id=self.env.ref("base.us").id,
            state_id=self.env.ref("base.state_us_5").id,
            city="San Francisco",
        )
        invoice = self.create_invoice(partner_id=partner.id)
        self.assertFalse(invoice._l10n_ro_customer_vat_missing_error())
