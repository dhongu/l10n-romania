# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from unittest.mock import patch

from psycopg2.errors import SerializationFailure

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

    def test_individual_without_vat_default_vat_in_xml_without_partner_write(self):
        """Tichet 10006: placeholder-ul ajunge in XML, dar nu se scrie pe partener."""
        partner = self._partner(name="Ion Popescu", is_company=False)
        invoice = self.create_invoice(partner_id=partner.id)
        partner.invalidate_recordset()
        write_date = partner.write_date
        xml, _errors = self.env["account.edi.xml.ubl_ro"]._export_invoice(invoice)
        self.assertEqual(xml.decode().count("0000000000000"), 2)  # PartyTaxScheme + PartyLegalEntity
        partner.invalidate_recordset()
        self.assertFalse(partner.company_registry)
        self.assertEqual(partner.write_date, write_date)

    def test_company_with_vat_is_sent(self):
        partner = self._partner(vat="RO1234567897")
        invoice = self.create_invoice(partner_id=partner.id)
        self.assertFalse(invoice._l10n_ro_customer_vat_missing_error())
        _errors, send = self._send(invoice)
        send.assert_called_once()

    def test_spv_address_defaults_conditions(self):
        """Aceleasi conditii ca inainte: scrie doar ce lipseste, doar pentru PF din Romania."""
        ro_b = self.env.ref("base.RO_B")
        cluj = self.env.ref("base.RO_CJ")
        cases = [
            # (kwargs, valori de scris asteptate)
            ({"is_company": False, "street": False, "state_id": cluj.id, "city": "Cluj"}, {"street": "Principala"}),
            ({"is_company": False, "street": "Str 1", "state_id": cluj.id, "city": "Cluj"}, {}),
            ({"is_company": False, "street": "Str 1", "state_id": ro_b.id, "city": False}, {"city": "SECTOR1"}),
            ({"is_company": False, "street": "Str 1", "state_id": ro_b.id, "city": "Bucuresti"}, {"city": "SECTOR1"}),
            ({"is_company": False, "street": "Str 1", "state_id": ro_b.id, "city": "Sector3"}, {}),
            ({"is_company": False, "street": "Str 1", "state_id": ro_b.id, "city": "sector 2"}, {}),
            (
                {"is_company": False, "street": False, "state_id": ro_b.id, "city": False},
                {"street": "Principala", "city": "SECTOR1"},
            ),
            ({"is_company": True, "street": False, "state_id": ro_b.id, "city": False}, {}),
            (
                {
                    "is_company": False,
                    "street": False,
                    "country_id": self.env.ref("base.us").id,
                    "state_id": self.env.ref("base.state_us_5").id,
                    "city": False,
                },
                {},
            ),
        ]
        for kwargs, expected in cases:
            with self.subTest(kwargs=kwargs):
                partner = self._partner(name="Client Test", **kwargs)
                self.assertEqual(partner._l10n_ro_spv_address_defaults(), expected)

    def _invoice_with_incomplete_address(self):
        """Factura postata (action_post cere adresa completa), apoi adresa clientului se goleste."""
        partner = self._partner(name="Ion Fara Adresa", is_company=False, state_id=self.env.ref("base.RO_B").id)
        invoice = self.create_invoice(partner_id=partner.id)
        partner.write({"street": False, "city": "Bucuresti"})
        return partner, invoice

    def test_prepare_partners_completes_address_then_export_does_not_write(self):
        partner, invoice = self._invoice_with_incomplete_address()
        invoice._l10n_ro_prepare_partners_for_spv()
        self.assertEqual((partner.street, partner.city), ("Principala", "SECTOR1"))
        partner.invalidate_recordset()
        write_date = partner.write_date
        with patch.object(self.env.registry["res.partner"], "write") as write:
            self.env["account.edi.xml.ubl_ro"]._export_invoice(invoice)
        write.assert_not_called()
        partner.invalidate_recordset()
        self.assertEqual(partner.write_date, write_date)

    def test_prepare_partners_retries_on_serialization_failure(self):
        partner, invoice = self._invoice_with_incomplete_address()
        partner_model = self.env.registry["res.partner"]
        original_write = partner_model.write
        calls = []

        def flaky_write(records, vals):
            calls.append(vals)
            if len(calls) == 1:
                raise SerializationFailure()
            return original_write(records, vals)

        with patch.object(partner_model, "write", flaky_write):
            invoice._l10n_ro_prepare_partners_for_spv()
        self.assertEqual(len(calls), 2)
        self.assertEqual((partner.street, partner.city), ("Principala", "SECTOR1"))

    def test_prepare_partners_gives_up_without_raising(self):
        _partner, invoice = self._invoice_with_incomplete_address()
        with (
            patch.object(self.env.registry["res.partner"], "write", side_effect=SerializationFailure()) as write,
            self.assertLogs("odoo.addons.l10n_ro_efactura_enhancement.models.account_move", "WARNING") as logs,
        ):
            invoice._l10n_ro_prepare_partners_for_spv(retries=2)
        self.assertEqual(write.call_count, 2)
        self.assertTrue(any("not completed" in line for line in logs.output))

    def test_foreign_company_without_vat_not_checked(self):
        partner = self._partner(
            country_id=self.env.ref("base.us").id,
            state_id=self.env.ref("base.state_us_5").id,
            city="San Francisco",
        )
        invoice = self.create_invoice(partner_id=partner.id)
        self.assertFalse(invoice._l10n_ro_customer_vat_missing_error())
