from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestResZipSearch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.zip_1 = cls.env["res.zip"].create(
            {
                "name": "123456",
                "city": "Bucharest",
                "street_name": "Libertatii",
                "street_type": "Bulevardul",
            }
        )
        cls.zip_2 = cls.env["res.zip"].create(
            {
                "name": "654321",
                "city": "Cluj",
                "street_name": "Unirii",
                "street_type": "Strada",
            }
        )

    def test_search_display_name_ilike(self):
        """Test searching with ilike (common search from UI)"""
        # Search by street name using ilike
        # Current implementation has: if operator != "ilike":
        # So for "ilike", it should NOT include street_name in the search if the bug exists
        zips = self.env["res.zip"].search([("display_name", "ilike", "Libertatii")])
        self.assertIn(self.zip_1, zips, "Should find zip_1 by street name with ilike")

    def test_search_display_name_equal(self):
        """Test searching with equal operator"""
        # For != "ilike" (e.g. "="), it should include the extra fields
        zips = self.env["res.zip"].search([("display_name", "=", "Libertatii")])
        self.assertIn(self.zip_1, zips, "Should find zip_1 by street name with =")
