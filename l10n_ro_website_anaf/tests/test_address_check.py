# ©  2026 Terrabit
# See README.rst file on addons root folder for license details

from unittest.mock import patch

from odoo.tests import TransactionCase, tagged

from odoo.addons.http_routing.tests.common import MockRequest

from .. import anaf
from ..controllers.website_sale import WebsiteSaleAnaf


@tagged("post_install", "-at_install")
class TestAddressCheck(TransactionCase):
    """The tax code of a Romanian billing address, checked at ANAF when the address is sent."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.controller = WebsiteSaleAnaf()
        cls.ro = cls.env.ref("base.ro")
        cls.state_cj = cls.env["res.country.state"].search(
            [("country_id", "=", cls.ro.id), ("code", "=", "CJ")], limit=1
        )
        product = cls.env["product.product"].create({"name": "Produs", "list_price": 10})
        customer = cls.env["res.partner"].create({"name": "Client"})
        cls.cart = cls.env["sale.order"].create(
            {"partner_id": customer.id, "order_line": [(0, 0, {"product_id": product.id})]}
        )

    def _company(self, **values):
        return {
            "name": "FIRMA ANAF SRL",
            "street": "Str. Anaf Nr. 7",
            "city": "Cluj-Napoca",
            "zip": "400001",
            "state_id": self.state_cj,
            "company_type": "company",
            "anaf_radiated": False,
            "anaf_inactive": False,
            "anaf_inactive_date": "",
            **values,
        }

    def _validate(self, address_values, answer=("not_found", {})):
        address_values = {"country_id": self.ro.id, **address_values}
        with (
            patch.object(anaf, "anaf_lookup", return_value=answer) as lookup,
            MockRequest(self.env) as request,
        ):
            request.cart = self.cart
            invalid_fields, _missing, messages = self.controller._validate_address_values(
                address_values=address_values,
                partner_sudo=self.env["res.partner"].sudo(),
                address_type="billing",
                use_delivery_as_billing=False,
                required_fields="vat",
            )
        return invalid_fields, messages, lookup

    def _notes(self, text):
        return self.cart.message_ids.filtered(lambda m: text in (m.body or ""))

    def test_found_values(self):
        address_values = {
            "country_id": self.ro.id,
            "name": "Ion Popescu",
            "street": "Depozit, Str. Fabricii 3",
            "vat": "RO1234567897",
        }
        with patch.object(anaf, "anaf_lookup", return_value=("found", self._company())), MockRequest(self.env):
            self.controller._validate_address_values(
                address_values=address_values,
                partner_sudo=self.env["res.partner"].sudo(),
                address_type="billing",
                use_delivery_as_billing=False,
                required_fields="vat",
            )
        self.assertEqual(address_values["name"], "FIRMA ANAF SRL", "the invoice is issued to the legal name")
        self.assertEqual(address_values["street"], "Depozit, Str. Fabricii 3", "what the customer typed stays")
        self.assertEqual(address_values["zip"], "400001", "an empty field is filled from ANAF")
        self.assertEqual(address_values["state_id"], self.state_cj.id)
        self.assertTrue(address_values["is_company"])

    def test_not_found_refused(self):
        invalid_fields, messages, _lookup = self._validate({"vat": "RO1234567897"})
        self.assertIn("vat", invalid_fields)
        self.assertTrue(any("ANAF" in message for message in messages))

    def test_struck_off_refused(self):
        invalid_fields, messages, _lookup = self._validate(
            {"vat": "RO1234567897"}, ("found", self._company(anaf_radiated=True))
        )
        self.assertIn("vat", invalid_fields)
        self.assertTrue(any("struck off" in message for message in messages))

    def test_inactive_allowed_with_note(self):
        invalid_fields, _messages, _lookup = self._validate(
            {"vat": "RO1234567897"},
            ("found", self._company(anaf_inactive=True, anaf_inactive_date="2026-05-04")),
        )
        self.assertNotIn("vat", invalid_fields)
        self.assertIn("2026-05-04", self._notes("fiscally inactive").body)

    def test_unavailable_does_not_block(self):
        invalid_fields, messages, _lookup = self._validate({"vat": "RO1234567897"}, ("unavailable", {}))
        self.assertNotIn("vat", invalid_fields)
        self.assertFalse(any("ANAF" in message for message in messages))
        self.assertTrue(self._notes("could not be checked at ANAF"))

    def test_cnp_message_without_anaf(self):
        invalid_fields, messages, lookup = self._validate({"vat": "1900101400012"})
        self.assertIn("vat", invalid_fields)
        self.assertTrue(any("CNP" in message for message in messages))
        self.assertFalse(lookup.called)

    def test_other_country_not_checked(self):
        invalid_fields, _messages, lookup = self._validate(
            {"vat": "BE0477472701", "country_id": self.env.ref("base.be").id}
        )
        self.assertNotIn("vat", invalid_fields)
        self.assertFalse(lookup.called)
