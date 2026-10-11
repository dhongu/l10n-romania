# Copyright (C) 2017 Forest and Biomass Romania
# Copyright (C) 2020 NextERP Romania
# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged

PARAM = "l10n_ro_partner_unique.vat_nrc_unique"


@tagged("post_install", "-at_install")
class TestVatUnique(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.account_fiscal_country_id = cls.env.ref("base.ro")
        cls.env["ir.config_parameter"].sudo().set_param(PARAM, "vat")
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner",
                "vat": "RO30834857",
                "nrc": "J35/2622/2012",
                "is_company": True,
            }
        )

    def _create(self, **vals):
        values = {
            "name": "Second partner",
            "vat": "RO30834857",
            "nrc": "J35/2622/2012",
            "is_company": True,
        }
        values.update(vals)
        return self.env["res.partner"].create(values)

    def _set_mode(self, mode):
        self.env["ir.config_parameter"].sudo().set_param(PARAM, mode)

    def test_duplicated_vat_nrc_creation(self):
        self._set_mode("vat_nrc")
        with self.assertRaises(ValidationError):
            self._create()
        # same VAT, other NRC: allowed when NRC is part of the key
        self._create(nrc="J2012002622359")

    def test_duplicated_vat_creation(self):
        self._set_mode("vat")
        with self.assertRaises(ValidationError):
            self._create()
        with self.assertRaises(ValidationError):
            self._create(nrc="J2012002622359")

    def test_duplicated_vat_creation_without_prefix(self):
        with self.assertRaises(ValidationError):
            self._create(vat="30834857")

    def test_disabled(self):
        self._set_mode("off")
        self._create()
        self._create(nrc="J2012002622359")

    def test_unknown_value_is_disabled(self):
        self._set_mode("something")
        self._create()

    def test_unset_parameter_is_disabled(self):
        self.env["ir.config_parameter"].sudo().search([("key", "=", PARAM)]).unlink()
        self._create()

    def test_not_checked_outside_romania(self):
        self.env.company.account_fiscal_country_id = self.env.ref("base.fr")
        self._create()

    def test_contact_vat_creation(self):
        self._create(name="child", parent_id=self.partner.id, is_company=False)
        self._create(name="child company", parent_id=self.partner.id)

    def test_partial_vat_creation(self):
        for vat in ("RO308", "RO3083485789"):
            partner = self._create(name="Test partner 1", vat=vat)
            with self.assertRaises(ValidationError):
                partner.vat = "RO30834857"

    def test_duplicated_vat_creation_individual(self):
        partner = self._create(is_company=False)
        with self.assertRaises(ValidationError):
            partner.is_company = True

    def test_partner_merge_context_skips_check(self):
        self.env["res.partner"].with_context(partner_merge=True).create(
            {"name": "Merged", "vat": "RO30834857", "is_company": True}
        )
