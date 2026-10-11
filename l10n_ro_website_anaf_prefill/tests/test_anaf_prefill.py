# ©  2026 Terrabit
# See README.rst file on addons root folder for license details

from unittest.mock import patch

import odoo
from odoo.tests import HttpCase, new_test_user, tagged

from ..controllers import main
from ..controllers.main import AnafPrefill


@tagged("post_install", "-at_install")
class TestAnafPrefill(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.state_cj = cls.env["res.country.state"].search(
            [("country_id", "=", cls.env.ref("base.ro").id), ("code", "=", "CJ")], limit=1
        )

    def setUp(self):
        super().setUp()
        main._cache.clear()
        main._hits.clear()

    def _company(self, **values):
        return {
            "name": "FIRMA ANAF SRL",
            "street": "Str. Anaf Nr. 7",
            "city": "Cluj-Napoca",
            "zip": "400001",
            "nrc": "J12/345/2020",
            "state_id": self.state_cj,
            "l10n_ro_vat_subjected": True,
            "anaf_inactive": False,
            "anaf_radiated": False,
            **values,
        }

    def _lookup(self, vat, answer=None):
        with patch.object(AnafPrefill, "_anaf_lookup", return_value=answer) as lookup:
            result = self.make_jsonrpc_request("/l10n_ro/anaf_lookup", {"vat": vat})
        return result, lookup

    def test_found(self):
        result, _lookup = self._lookup("RO 1234567897", ("found", self._company(anaf_inactive=True)))
        self.assertEqual(result["state"], "found")
        self.assertEqual(result["name"], "FIRMA ANAF SRL")
        self.assertEqual(result["state_id"], self.state_cj.id)
        self.assertEqual(result["company_registry"], "J12/345/2020")
        self.assertTrue(result["vat_payer"])
        self.assertTrue(result["inactive"])
        self.assertFalse(result["radiated"])

    def test_not_found_and_unavailable(self):
        self.assertEqual(self._lookup("1234567897", ("not_found", {}))[0], {"state": "not_found"})
        main._cache.clear()
        self.assertEqual(self._lookup("1234567897", ("unavailable", {}))[0], {"state": "unavailable"})

    def test_cnp_and_invalid_not_sent_to_anaf(self):
        result, lookup = self._lookup("1900101400012")
        self.assertEqual(result, {"state": "cnp"})
        self.assertFalse(lookup.called)
        result, lookup = self._lookup("RO12AB")
        self.assertEqual(result, {"state": "invalid"})
        self.assertFalse(lookup.called)

    def test_cache(self):
        self._lookup("1234567897", ("found", self._company()))
        result, lookup = self._lookup("RO1234567897", ("found", self._company(name="ALTA")))
        self.assertFalse(lookup.called, "a company is looked up once a day")
        self.assertEqual(result["name"], "FIRMA ANAF SRL")

    def test_unavailable_not_cached(self):
        self._lookup("1234567897", ("unavailable", {}))
        result, lookup = self._lookup("1234567897", ("found", self._company()))
        self.assertTrue(lookup.called)
        self.assertEqual(result["state"], "found")

    def test_rate_limit(self):
        with patch.object(main, "RATE_LIMIT", 2):
            for number in ("18547290", "14399840"):
                self.assertEqual(self._lookup(number, ("not_found", {}))[0]["state"], "not_found")
            result, lookup = self._lookup("37024165", ("not_found", {}))
        self.assertEqual(result, {"state": "limited"})
        self.assertFalse(lookup.called)

    def test_prefill_tour(self):
        """On the checkout address form, the company found fills the empty fields and replaces the
        typed ones only on request."""
        website = self.env["website"].get_current_website()
        user = new_test_user(self.env, login="anaf_buyer", groups="base.group_portal", name="Ion Popescu")
        user.partner_id.write({"country_id": self.env.ref("base.ro").id, "email": "ion@example.com"})
        product = self.env["product.product"].create(
            {"name": "Produs", "list_price": 10, "sale_ok": True, "is_published": True}
        )
        cart = self.env["sale.order"].create(
            {
                "partner_id": user.partner_id.id,
                "website_id": website.id,
                "order_line": [(0, 0, {"product_id": product.id, "product_uom_qty": 1})],
            }
        )
        self.authenticate("anaf_buyer", "anaf_buyer")
        self.session["sale_order_id"] = cart.id
        odoo.http.root.session_store.save(self.session)
        with patch.object(AnafPrefill, "_anaf_lookup", return_value=("found", self._company())):
            self.start_tour(
                f"/shop/address?partner_id={user.partner_id.id}&address_type=billing",
                "l10n_ro_website_anaf_prefill_tour",
                login="anaf_buyer",
            )

    def test_anaf_answers(self):
        """The real request: found (with the struck-off state), not found, service down."""
        answer = {
            "found": [
                {
                    "date_generale": {
                        "denumire": "FIRMA RADIATA SRL",
                        "cui": 1234567897,
                        "codPostal": "",
                        "stare_inregistrare": "RADIERE din data 20.07.2016",
                    },
                    "stare_inactiv": {"statusInactivi": False, "dataRadiere": ""},
                    "adresa_domiciliu_fiscal": {
                        "ddenumire_Strada": "STR. A",
                        "dnumar_Strada": "1",
                        "ddetalii_Adresa": "",
                        "ddenumire_Localitate": "MUN. CLUJ-NAPOCA",
                        "ddenumire_Judet": "CLUJ",
                        "dcod_JudetAuto": "CJ",
                    },
                }
            ]
        }

        class Response:
            def __init__(self, payload):
                self.payload = payload

            def raise_for_status(self):
                return None

            def json(self):
                return self.payload

        with patch.object(main.requests, "post", return_value=Response(answer)):
            result = self.make_jsonrpc_request("/l10n_ro/anaf_lookup", {"vat": "RO1234567897"})
        self.assertEqual((result["state"], result["radiated"]), ("found", True))
        main._cache.clear()
        with patch.object(main.requests, "post", return_value=Response({"found": [], "notFound": [1]})):
            self.assertEqual(
                self.make_jsonrpc_request("/l10n_ro/anaf_lookup", {"vat": "18547290"})["state"], "not_found"
            )
        with patch.object(main.requests, "post", side_effect=main.requests.ConnectTimeout("timeout")):
            self.assertEqual(
                self.make_jsonrpc_request("/l10n_ro/anaf_lookup", {"vat": "14399840"})["state"], "unavailable"
            )
