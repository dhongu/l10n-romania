# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import HttpCase, tagged

BROWSER_UA = "Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0 Safari/537.36"


@tagged("post_install", "-at_install")
class TestNearestLang(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].get_current_website()
        cls.lang_en = cls.env.ref("base.lang_en")
        cls.lang_ro = cls.env.ref("base.lang_ro")
        cls.website.default_lang_id = cls.lang_en

    def _get_home(self):
        self.opener.cookies.clear()
        return self.url_open("/", headers={"User-Agent": BROWSER_UA}, allow_redirects=False)

    def test_ro_not_website_language(self):
        """Without Romanian among the website languages, the page loads in the default language."""
        self.website.language_ids = self.lang_en
        response = self._get_home()
        self.assertEqual(response.status_code, 200)
        self.assertIn('lang="en-US"', response.text)
        self.assertEqual(response.cookies.get("frontend_lang"), "en_US")

    def test_ro_website_language(self):
        """With Romanian active on the website, a visitor from Romania is sent to /ro."""
        self.env["res.lang"]._activate_lang("ro_RO")
        self.website.language_ids = self.lang_en | self.lang_ro
        response = self._get_home()
        self.assertIn(response.status_code, (302, 303))
        self.assertIn("/ro", response.headers["Location"])
        self.assertEqual(response.cookies.get("frontend_lang"), "ro_RO")
