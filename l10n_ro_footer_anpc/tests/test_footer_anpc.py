# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from lxml import html

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestFooterAnpc(HttpCase):
    def test_homepage_public_footer_has_anpc_sal_link(self):
        response = self.url_open("/")
        self.assertEqual(response.status_code, 200)
        page = html.fromstring(response.content)
        blocks = page.xpath(
            "//footer//div[contains(@class, 'o_footer_copyright')]//div[contains(@class, 'o_footer_anpc')]"
        )
        self.assertEqual(len(blocks), 1, "The ANPC block must be in the copyright row")
        hrefs = blocks[0].xpath(".//a/@href")
        self.assertEqual(hrefs, ["https://reclamatiisal.anpc.ro/"])
        images = blocks[0].xpath(".//img")
        self.assertEqual(len(images), 1, "Only the SAL pictogram is required (Order ANPC 270/2026)")
        self.assertEqual(images[0].get("src"), "/l10n_ro_footer_anpc/static/src/img/anpc_sal.png")
        self.assertEqual((images[0].get("width"), images[0].get("height")), ("250", "50"))
        image = self.url_open(images[0].get("src"))
        self.assertEqual(image.status_code, 200)
        self.assertTrue(image.content.startswith(b"\x89PNG"))
