# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestResZipDisplayName(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # res_zip.sql inserts rows with explicit ids, so the sequence lags behind
        cls.env.cr.execute("SELECT setval('res_zip_id_seq', (SELECT MAX(id) FROM res_zip))")
        cls.state = cls.env["res.country.state"].search(
            [("country_id.code", "=", "RO"), ("code", "=", "B")], limit=1
        ) or cls.env["res.country.state"].create(
            {"name": "Bucuresti", "code": "B", "country_id": cls.env.ref("base.ro").id}
        )
        cls.zip_street = cls.env["res.zip"].create(
            {
                "name": "919191",
                "city": "Bucuresti",
                "street_type": "Strada",
                "street_name": "Zzdisplay Test",
                "sector": "1",
                "state_id": cls.state.id,
            }
        )
        cls.zip_city = cls.env["res.zip"].create(
            {
                "name": "929292",
                "city": "Zzorasul Test",
                "state_id": cls.state.id,
            }
        )

    def test_display_name_plain_unchanged(self):
        self.assertEqual(self.zip_street.display_name, "Strada Zzdisplay Test (919191)")
        self.assertEqual(self.zip_city.display_name, "Zzorasul Test (929292)")

    def test_display_name_formatted(self):
        zip_street = self.zip_street.with_context(formatted_display_name=True)
        self.assertEqual(zip_street.display_name, "Strada Zzdisplay Test\t--919191 · Bucuresti, Sector 1, B--")
        zip_city = self.zip_city.with_context(formatted_display_name=True)
        self.assertEqual(zip_city.display_name, "Zzorasul Test\t--929292 · B--")

    def test_display_name_formatted_skips_empty_parts(self):
        self.zip_street.write({"sector": False, "state_id": False})
        zip_street = self.zip_street.with_context(formatted_display_name=True)
        self.assertEqual(zip_street.display_name, "Strada Zzdisplay Test\t--919191 · Bucuresti--")
        self.zip_city.state_id = False
        zip_city = self.zip_city.with_context(formatted_display_name=True)
        self.assertEqual(zip_city.display_name, "Zzorasul Test\t--929292--")
