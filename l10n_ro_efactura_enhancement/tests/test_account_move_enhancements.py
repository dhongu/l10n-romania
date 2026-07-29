# ©  2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
import logging
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)

# Câmpurile de partener pe care le citește logica testată aici (check_partner și
# _get_suggested_invoice_edi_format). Bazele reale de dezvoltare au adesea valori
# implicite pe res.partner — ir.default, setate din UI cu "Set Default" pe câmp,
# de exemplu Țară = România — iar default_get le aplică oricărui create() care
# omite câmpul. Un partener „fără țară" ar primi tăcut RO și testul ar verifica
# exact cazul opus celui descris. Testele își scriu deci explicit toate aceste
# câmpuri, ca să nu depindă de starea bazei pe care rulează.
PARTNER_BLANK_VALS = {
    "country_id": False,
    "state_id": False,
    "city": False,
    "street": False,
    "vat": False,
}


def partner_vals(**kwargs):
    """Valori de partener complet explicite, imune la ir.default din baza gazdă."""
    vals = dict(PARTNER_BLANK_VALS)
    vals.update(kwargs)
    return vals


@tagged("post_install", "-at_install")
class TestCheckPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create({"name": "Test Product"})

    def _make_partner(self, **kwargs):
        vals = partner_vals(
            name="Test Partner",
            country_id=self.env.ref("base.ro").id,
            state_id=self.env.ref("base.RO_B").id,
            city="Bucuresti",
            street="Str. Test 1",
        )
        vals.update(kwargs)
        return self.env["res.partner"].create(vals)

    def _create_invoice(self, partner):
        return self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [(0, 0, {"product_id": self.product.id, "quantity": 1, "price_unit": 100})],
            }
        )

    def test_check_partner_no_country_raises(self):
        """check_partner ridică UserError dacă partenerul nu are țară."""
        partner = self.env["res.partner"].create(partner_vals(name="No Country Partner"))
        self.assertFalse(partner.country_id, "Partenerul de test trebuie să rămână fără țară")
        invoice = self._create_invoice(partner)
        with self.assertRaises(UserError):
            invoice.action_post()

    def test_check_partner_ro_no_state_raises(self):
        """check_partner ridică UserError pentru partener RO fără județ."""
        partner = self._make_partner(state_id=False)
        invoice = self._create_invoice(partner)
        with self.assertRaises(UserError):
            invoice.action_post()

    def test_check_partner_ro_no_city_raises(self):
        """check_partner ridică UserError pentru partener RO fără oraș."""
        partner = self._make_partner(city=False)
        invoice = self._create_invoice(partner)
        with self.assertRaises(UserError):
            invoice.action_post()

    def test_check_partner_ro_no_street_raises(self):
        """check_partner ridică UserError pentru partener RO fără stradă."""
        partner = self._make_partner(street=False)
        invoice = self._create_invoice(partner)
        with self.assertRaises(UserError):
            invoice.action_post()

    def test_check_partner_ro_complete_ok(self):
        """action_post reușește pentru partener RO cu toate câmpurile completate."""
        partner = self._make_partner()
        invoice = self._create_invoice(partner)
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")

    def test_check_partner_non_ro_no_state_ok(self):
        """check_partner nu ridică eroare pentru partener non-RO fără județ."""
        partner = self.env["res.partner"].create(
            partner_vals(
                name="Non RO Partner",
                country_id=self.env.ref("base.de").id,
                city="Berlin",
                street="Str. Test 1",
            )
        )
        self.assertFalse(partner.state_id, "Partenerul non-RO de test trebuie să rămână fără județ")
        invoice = self._create_invoice(partner)
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")

    def test_check_partner_not_called_for_vendor_bill(self):
        """check_partner nu este apelat pentru facturi de furnizor (in_invoice)."""
        partner = self.env["res.partner"].create(partner_vals(name="Vendor No Country"))
        invoice = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": partner.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [(0, 0, {"product_id": self.product.id, "quantity": 1, "price_unit": 100})],
            }
        )
        # check_partner nu trebuie apelat pentru in_invoice
        with patch.object(type(invoice), "check_partner") as mock_check:
            try:
                invoice.action_post()
            except Exception as e:
                _logger.warning("action_post raised exception: %s", e)
            mock_check.assert_not_called()


@tagged("post_install", "-at_install")
class TestAccountMoveLineLabelLength(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            partner_vals(
                name="Test Partner",
                country_id=cls.env.ref("base.ro").id,
                state_id=cls.env.ref("base.RO_B").id,
                city="Bucuresti",
                street="Str. Test 1",
            )
        )
        cls.product = cls.env["product.product"].create({"name": "Produs Test"})

    def _create_invoice_line(self, name=None, product=None):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id if product else False,
                            "name": name or "Descriere linie",
                            "quantity": 1,
                            "price_unit": 50,
                        },
                    )
                ],
            }
        )
        return invoice.invoice_line_ids[0]

    def test_label_length_with_name(self):
        """l10n_ro_label_length calculează corect lungimea numelui liniei."""
        line = self._create_invoice_line(name="Descriere de test")
        line._compute_label_length()
        self.assertEqual(line.l10n_ro_label_length, len("Descriere de test"))

    def test_label_length_without_name(self):
        """l10n_ro_label_length este 0 când linia nu are nume."""
        line = self._create_invoice_line(name=" ")
        line.name = False
        line._compute_label_length()
        self.assertEqual(line.l10n_ro_label_length, 0)

    def test_product_length_with_product(self):
        """l10n_ro_product_length calculează corect lungimea numelui produsului."""
        line = self._create_invoice_line(product=self.product)
        line._compute_label_length()
        self.assertEqual(line.l10n_ro_product_length, len(self.product.display_name))

    def test_product_length_without_product(self):
        """l10n_ro_product_length este 0 când linia nu are produs."""
        line = self._create_invoice_line(name="Fara produs")
        line.product_id = False
        line._compute_label_length()
        self.assertEqual(line.l10n_ro_product_length, 0)


@tagged("post_install", "-at_install")
class TestResPartnerEdiFormat(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_ro = cls.env["res.partner"].create(
            partner_vals(name="Partner RO", country_id=cls.env.ref("base.ro").id)
        )
        cls.partner_de = cls.env["res.partner"].create(
            partner_vals(name="Partner DE", country_id=cls.env.ref("base.de").id)
        )
        cls.partner_no_country = cls.env["res.partner"].create(partner_vals(name="Partner Fara Tara"))

    def test_suggested_edi_format_ro(self):
        """Partenerul RO sugerează formatul ciusro."""
        self.assertEqual(self.partner_ro.country_code, "RO")
        result = self.partner_ro._get_suggested_invoice_edi_format()
        self.assertEqual(result, "ciusro")

    def test_suggested_edi_format_non_ro(self):
        """Partenerul non-RO returnează formatul standard (nu ciusro)."""
        self.assertEqual(self.partner_de.country_code, "DE")
        result = self.partner_de._get_suggested_invoice_edi_format()
        self.assertNotEqual(result, "ciusro")

    def test_suggested_edi_format_no_country(self):
        """Partenerul fără țară returnează formatul standard."""
        self.assertFalse(self.partner_no_country.country_id, "Partenerul de test trebuie să rămână fără țară")
        result = self.partner_no_country._get_suggested_invoice_edi_format()
        self.assertNotEqual(result, "ciusro")


@tagged("post_install", "-at_install")
class TestGetDescription(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model = cls.env["account.edi.xml.ubl_ro"]
        cls.product = cls.env["product.product"].create({"name": "Produs Test"})
        cls.partner = cls.env["res.partner"].create(
            partner_vals(
                name="Partner Test",
                country_id=cls.env.ref("base.ro").id,
                state_id=cls.env.ref("base.RO_B").id,
                city="Bucuresti",
                street="Str. Test 1",
            )
        )

    def _make_line(self, name, product=None):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id if product else False,
                            "name": name,
                            "quantity": 1,
                            "price_unit": 10,
                        },
                    )
                ],
            }
        )
        return invoice.invoice_line_ids[0]

    def test_get_description_name_only(self):
        """get_description returnează numele liniei când nu există produs."""
        line = self._make_line("Serviciu consultanta", product=None)
        result = self.model.get_description(line)
        self.assertEqual(result, "Serviciu consultanta")

    def test_get_description_name_equals_product(self):
        """get_description returnează gol când linia = produsul (fără descriere proprie)."""
        line = self._make_line(self.product.display_name, product=self.product)
        result = self.model.get_description(line)
        self.assertEqual(result, "")

    def test_get_description_name_equals_product_with_code(self):
        """get_description returnează gol și când display_name include codul intern."""
        product = self.env["product.product"].create({"name": "Produs Cod", "default_code": "COD123"})
        line = self._make_line(product.display_name, product=product)
        result = self.model.get_description(line)
        self.assertEqual(result, "")

    def test_get_description_name_contains_product(self):
        """get_description elimină prefixul produsului din descrierea liniei."""
        name = self.product.display_name + " - detalii suplimentare"
        line = self._make_line(name, product=self.product)
        result = self.model.get_description(line)
        self.assertEqual(result, "- detalii suplimentare")

    def test_get_description_no_name_with_product(self):
        """get_description returnează gol când linia nu are nume (fără descriere în XML)."""
        line = self._make_line("x", product=self.product)
        line.name = False
        result = self.model.get_description(line)
        self.assertEqual(result, "")

    def test_get_description_no_name_no_product(self):
        """get_description returnează string gol când nu există nici nume nici produs."""
        line = self._make_line("x")
        line.name = False
        result = self.model.get_description(line)
        self.assertEqual(result, "")
