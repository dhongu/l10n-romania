# See README.rst file on addons root folder for license details

from lxml import etree

from odoo.tests import tagged

from odoo.addons.l10n_ro_edi.tests.common import TestROEdiCommon

NS = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


@tagged("post_install_l10n", "post_install", "-at_install")
class TestExportNoPartnerWrites(TestROEdiCommon):
    """Exportul XML nu trebuie sa modifice partenerul.

    Pentru persoanele fizice fara strada / fara sector, exportul scria pe partener
    "Principala", "SECTOR1" si company_registry = "0000000000000". Din cron-ul de
    trimitere (fara rollback) valorile ramaneau definitiv in baza si ascundeau
    datele lipsa. Acum ele apar doar in XML.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.person = cls.env["res.partner"].create(
            {
                "name": "Ion Popescu",
                "country_id": cls.env.ref("base.ro").id,
                "state_id": cls.env.ref("base.RO_B").id,
                "city": "SECTOR2",
                "street": "Strada Test 1",
                "invoice_edi_format": "ciusro",
            }
        )

    def _export_customer_party(self, invoice):
        xml, errors = self.env["account.edi.xml.ubl_ro"]._export_invoice(invoice)
        self.assertFalse(errors)
        return etree.fromstring(xml).find("cac:AccountingCustomerParty/cac:Party", NS)

    def _person_invoice_without_street_and_sector(self):
        # check_partner cere strada la confirmare; lipsa ei apare ulterior
        # (ex. facturile din POS, confirmate prin _post).
        invoice = self.create_invoice(partner_id=self.person.id)
        self.person.write({"street": False, "city": "Bucuresti"})
        return invoice

    def test_person_placeholders_only_in_xml(self):
        invoice = self._person_invoice_without_street_and_sector()
        party = self._export_customer_party(invoice)

        self.assertEqual(party.findtext("cac:PostalAddress/cbc:StreetName", namespaces=NS), "Principala")
        self.assertEqual(party.findtext("cac:PostalAddress/cbc:CityName", namespaces=NS), "SECTOR1")
        self.assertEqual(party.findtext("cac:PartyLegalEntity/cbc:CompanyID", namespaces=NS), "0000000000000")

        self.assertFalse(self.person.street)
        self.assertEqual(self.person.city, "Bucuresti")
        self.assertFalse(self.person.company_registry)

    def test_person_real_sector_is_kept(self):
        invoice = self.create_invoice(partner_id=self.person.id)
        self.person.city = "Sector 2"
        party = self._export_customer_party(invoice)
        self.assertEqual(party.findtext("cac:PostalAddress/cbc:CityName", namespaces=NS), "SECTOR2")
        self.assertEqual(party.findtext("cac:PostalAddress/cbc:StreetName", namespaces=NS), "Strada Test 1")

    def test_company_without_street_still_blocked(self):
        invoice = self.create_invoice()
        self.partner_ro.write({"is_company": True, "street": False})
        _xml, errors = self.env["account.edi.xml.ubl_ro"]._export_invoice(invoice)
        self.assertTrue(errors, "Firmele fara strada trebuie in continuare oprite de constrangerea CIUS-RO")
