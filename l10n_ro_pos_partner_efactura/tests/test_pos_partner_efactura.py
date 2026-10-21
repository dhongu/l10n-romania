from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPosPartnerEfactura(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country_ro = cls.env.ref("base.ro")
        cls.state_cj = cls.env.ref("base.RO_CJ")
        cls.state_b = cls.env.ref("base.RO_B")
        cls.Partner = cls.env["res.partner"].with_context(pos_efactura_check=True)

    def _vals(self, **vals):
        data = {
            "name": "TEST POS Partner",
            "is_company": True,
            "vat": "RO1234567897",
            "street": "Str. Memorandumului 1",
            "city": "Cluj-Napoca",
            "state_id": self.state_cj.id,
            "country_id": self.country_ro.id,
        }
        data.update(vals)
        return data

    def test_complete_partner(self):
        partner = self.Partner.create(self._vals())
        self.assertFalse(partner._get_pos_efactura_missing_data())

    def test_missing_address_blocks_create(self):
        with self.assertRaisesRegex(ValidationError, "Street"):
            self.Partner.create(self._vals(street=False))
        with self.assertRaisesRegex(ValidationError, "City"):
            self.Partner.create(self._vals(city=False))
        with self.assertRaisesRegex(ValidationError, "State"):
            self.Partner.create(self._vals(state_id=False))

    def test_company_requires_vat(self):
        with self.assertRaisesRegex(ValidationError, "Tax ID"):
            self.Partner.create(self._vals(vat=False))
        # An individual is invoiced without a Tax ID
        partner = self.Partner.create(self._vals(is_company=False, vat=False))
        self.assertFalse(partner._get_pos_efactura_missing_data())

    def test_bucharest_city_must_be_sector(self):
        with self.assertRaisesRegex(ValidationError, "sector"):
            self.Partner.create(self._vals(state_id=self.state_b.id, city="Bucuresti"))
        partner = self.Partner.create(self._vals(state_id=self.state_b.id, city="Sector 3"))
        self.assertFalse(partner._get_pos_efactura_missing_data())

    def test_write_from_pos_checks_data(self):
        partner = self.Partner.create(self._vals())
        with self.assertRaisesRegex(ValidationError, "City"):
            partner.write({"city": False})

    def test_back_office_not_checked(self):
        # Without the POS context key, an incomplete partner can still be saved
        partner = self.env["res.partner"].create({"name": "TEST Back Office", "is_company": True})
        self.assertTrue(partner._get_pos_efactura_missing_data())

    def test_contact_person_not_checked(self):
        company = self.Partner.create(self._vals())
        contact = self.Partner.create({"name": "TEST Contact", "parent_id": company.id, "type": "contact"})
        self.assertFalse(contact._get_pos_efactura_missing_data())
