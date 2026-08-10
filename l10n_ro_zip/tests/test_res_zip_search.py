from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestResZipSearch(TransactionCase):
    """The module ships ~52.000 real zip codes, so the fixtures below use street
    names that cannot collide with them: a search must return our records only.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # res_zip.sql inserts rows with explicit ids, so the sequence lags behind
        cls.env.cr.execute("SELECT setval('res_zip_id_seq', (SELECT MAX(id) FROM res_zip))")
        cls.zip_1 = cls.env["res.zip"].create(
            {
                "name": "123456",
                "city": "Bucharest",
                "street_name": "Zzlibertatii Test",
                "street_type": "Bulevardul",
            }
        )
        cls.zip_2 = cls.env["res.zip"].create(
            {
                "name": "654321",
                "city": "Cluj",
                "street_name": "Zzunirii Test",
                "street_type": "Strada",
            }
        )
        # spelled surname first, the way the postal nomenclature does it
        cls.zip_3 = cls.env["res.zip"].create(
            {
                "name": "111222",
                "city": "Iasi",
                "street_name": "Zzbalcescu Nicolae",
                "street_type": "Strada",
            }
        )

    def test_search_street_name_ilike(self):
        """The autocomplete widget searches with ilike, so the street must be found."""
        zips = self.env["res.zip"].search([("display_name", "ilike", "Zzlibertatii")])
        self.assertIn(self.zip_1, zips, "Should find zip_1 by street name with ilike")
        self.assertNotIn(self.zip_2, zips)

    def test_name_search_street_name(self):
        """name_search is what the postal code field on the partner actually calls."""
        results = self.env["res.zip"].name_search("Zzlibertatii Test")
        self.assertEqual([res[0] for res in results], [self.zip_1.id])

    def test_name_search_partial_street_name(self):
        """A partial street name must be enough, as the user types."""
        results = self.env["res.zip"].name_search("zzlibert")
        self.assertIn(self.zip_1.id, [res[0] for res in results])

    def test_search_postal_code_still_works(self):
        """Extending the domain must not break the search on the postal code."""
        zips = self.env["res.zip"].search([("display_name", "ilike", "654321")])
        self.assertIn(self.zip_2, zips)

    def test_search_display_name_equal(self):
        """The '=' operator is extended to the street fields as well."""
        zips = self.env["res.zip"].search([("display_name", "=", "Zzlibertatii Test")])
        self.assertIn(self.zip_1, zips, "Should find zip_1 by street name with =")

    def test_name_search_reversed_word_order(self):
        """The nomenclature spells "Zzbalcescu Nicolae", users type it reversed."""
        results = self.env["res.zip"].name_search("Nicolae Zzbalcescu")
        self.assertEqual([res[0] for res in results], [self.zip_3.id])

    def test_name_search_words_with_street_type(self):
        """Typing the street type along with the name must keep working."""
        results = self.env["res.zip"].name_search("Bulevardul Zzlibertatii")
        self.assertIn(self.zip_1.id, [res[0] for res in results])

    def test_name_search_words_must_all_match(self):
        """Every word has to match: an extra unrelated word excludes the record."""
        results = self.env["res.zip"].name_search("Nicolae Zzbalcescu Zzunirii")
        self.assertNotIn(self.zip_3.id, [res[0] for res in results])
