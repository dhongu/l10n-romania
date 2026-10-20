# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from lxml import html

from odoo.tests import HttpCase, tagged

IMG_PATH = "/l10n_ro_website_legal_guarantee/static/src/img/"


@tagged("post_install", "-at_install")
class TestLegalGuarantee(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref("base.default_website")
        cls.product = cls.env["product.template"].create(
            {
                "name": "Legal guarantee test product",
                "type": "consu",
                "list_price": 100.0,
                "sale_ok": True,
                "website_published": True,
            }
        )

    def _get_page(self, url):
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
        return html.fromstring(response.content)

    def test_page_shows_official_notice(self):
        page = self._get_page("/garantie")
        images = page.xpath("//div[@id='wrap']//figure[contains(@class, 'o_legal_guarantee_notice')]//img")
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0].get("src"), IMG_PATH + "legal_guarantee_notice_en.svg")
        hrefs = page.xpath("//div[@id='wrap']//figure[contains(@class, 'o_legal_guarantee_notice')]//a/@href")
        self.assertIn("https://europa.eu/youreurope/guarantees", hrefs)
        self.assertIn(IMG_PATH + "legal_guarantee_notice_en.pdf", hrefs)
        for url in (images[0].get("src"), IMG_PATH + "legal_guarantee_notice_en.pdf"):
            self.assertEqual(self.url_open(url).status_code, 200)

    def test_notice_in_romanian(self):
        self.env["res.lang"]._activate_lang("ro_RO")
        notice = self.website.with_context(lang="ro_RO")._get_legal_guarantee_notice()
        self.assertEqual(notice["image_url"], IMG_PATH + "legal_guarantee_notice_ro.png")
        self.assertEqual(notice["pdf_url"], IMG_PATH + "legal_guarantee_notice_ro.pdf")
        self.assertEqual(notice["link_text"], "europa.eu/youreurope/garanții")
        self.assertEqual(notice["link_url"], "https://europa.eu/youreurope/garan%C8%9Bii")
        self.assertEqual(self.url_open(notice["image_url"]).status_code, 200)

    def test_footer_link(self):
        xpath = "//footer//div[contains(@class, 'o_footer_legal_guarantee')]//a/@href"
        hrefs = self._get_page("/").xpath(xpath)
        self.assertEqual(len(hrefs), 1)
        self.assertTrue(hrefs[0].endswith("/garantie"))
        self.website.legal_guarantee_footer = False
        self.assertFalse(self._get_page("/").xpath(xpath))

    def test_product_page_link_and_modal(self):
        page = self._get_page(self.product.website_url)
        links = page.xpath("//a[contains(@class, 'o_legal_guarantee_link')]")
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0].get("data-bs-target"), "#o_legal_guarantee_modal")
        self.assertEqual(len(page.xpath("/html/body/div[@id='o_legal_guarantee_modal']//img")), 1)
        self.website.legal_guarantee_product = False
        page = self._get_page(self.product.website_url)
        self.assertFalse(page.xpath("//a[contains(@class, 'o_legal_guarantee_link')]"))
