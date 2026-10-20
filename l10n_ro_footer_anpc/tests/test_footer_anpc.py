# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from lxml import html

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestFooterAnpc(HttpCase):
    def test_homepage_public_footer_has_anpc_links(self):
        response = self.url_open("/")
        self.assertEqual(response.status_code, 200)
        page = html.fromstring(response.content)
        blocks = page.xpath(
            "//footer//div[contains(@class, 'o_footer_copyright')]//div[contains(@class, 'o_footer_anpc')]"
        )
        self.assertEqual(len(blocks), 1, "The ANPC block must be in the copyright row")
        hrefs = blocks[0].xpath(".//a/@href")
        self.assertIn("https://anpc.ro/ce-este-sal/", hrefs)
        self.assertTrue(any(href.startswith("https://ec.europa.eu/consumers/odr/") for href in hrefs))
        srcs = blocks[0].xpath(".//img/@src")
        self.assertEqual(
            srcs,
            [
                "/l10n_ro_footer_anpc/static/src/img/anpc1.svg",
                "/l10n_ro_footer_anpc/static/src/img/anpc2.svg",
            ],
        )
        for src in srcs:
            image = self.url_open(src)
            self.assertEqual(image.status_code, 200)
            self.assertIn(b"<svg", image.content[:200])
