# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from lxml import etree

from odoo.tests import TransactionCase, tagged

from ..migration import migrate_legacy_footer_views


@tagged("post_install", "-at_install")
class TestFooterMigration(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.site = cls.env["website"].create({"name": "ANPC migration test"})
        cls.generic = cls.env.ref("l10n_ro_footer_anpc.footer_anpc_data")
        cls.legacy = """<data><xpath expr="//div[hasclass('o_footer_copyright')]/div/div" position="inside">
            <div class="col-sm custom-layout" data-custom="keep">
                <a href="https://anpc.ro/ce-este-sal/" target="_blank"><img src="/l10n_ro_footer_anpc/static/src/img/anpc1.svg"/></a>
                <a href="https://ec.europa.eu/consumers/odr/" target="_blank"><img src="/l10n_ro_footer_anpc/static/src/img/anpc2.svg"/></a>
                <span class="custom-text">Keep this website text</span>
            </div></xpath></data>"""

    def _specific(self, arch=None, active=True):
        return self.generic.with_context(no_cow=True).copy(
            {
                "key": self.generic.key,
                "website_id": self.site.id,
                "arch_db": arch or self.legacy,
                "active": active,
                "arch_updated": True,
            }
        )

    def test_modified_website_copy_and_repeated_upgrade(self):
        view = self._specific()
        before_parent = view.inherit_id
        migrate_legacy_footer_views(self.env)
        root = etree.fromstring(view.arch_db.encode())
        self.assertEqual(root.xpath(".//t/@t-call"), ["l10n_ro_footer_anpc.footer_anpc_sal"])
        self.assertEqual(root.xpath(".//*[@data-custom='keep']/@class"), ["col-sm custom-layout o_footer_anpc"])
        self.assertEqual(root.xpath(".//span/text()"), ["Keep this website text"])
        self.assertNotIn(".svg", view.arch_db)
        first_arch = view.arch_db
        # Replaying the loader/update and migration must not revive old images.
        self.generic._load_records_write({"arch_db": self.generic.arch_db})
        migrate_legacy_footer_views(self.env)
        self.assertEqual(view.arch_db, first_arch)
        self.assertEqual(view.inherit_id, before_parent)
        self.assertTrue(view.active)
        self.assertEqual(view.website_id, self.site)
        rendered = str(self.env["ir.qweb"]._render("l10n_ro_footer_anpc.footer_anpc_sal", {}))
        self.assertIn("anpc_sal.png", rendered)
        self.assertNotIn("anpc2.svg", rendered)
        component = self.env.ref("l10n_ro_footer_anpc.footer_anpc_sal")
        component._load_records_write(
            {
                "arch_db": component.arch_db.replace("anpc_sal.png", "future_sal.png"),
            }
        )
        self.assertEqual(view.arch_db, first_arch)
        updated = str(self.env["ir.qweb"]._render("l10n_ro_footer_anpc.footer_anpc_sal", {}))
        self.assertIn("future_sal.png", updated)

    def test_inactive_copy_stays_inactive(self):
        view = self._specific(active=False)
        migrate_legacy_footer_views(self.env)
        self.assertFalse(view.active)
        self.assertIn("t-call=", view.arch_db)

    def test_custom_badge_content_is_preserved(self):
        view = self._specific(self.legacy.replace("<img src=", "<b>Custom label</b><img src=", 1))
        before = view.arch_db
        migrate_legacy_footer_views(self.env)
        self.assertEqual(view.arch_db, before)

    def test_unrelated_and_current_views_are_preserved(self):
        view = self._specific(self.generic.arch_db)
        unrelated = self.env["ir.ui.view"].create(
            {
                "name": "Other footer",
                "type": "qweb",
                "key": "test.other_footer",
                "arch_db": self.legacy,
                "inherit_id": self.generic.inherit_id.id,
                "website_id": self.site.id,
            }
        )
        before = (view.arch_db, unrelated.arch_db, self.generic.arch_db)
        migrate_legacy_footer_views(self.env)
        self.assertEqual((view.arch_db, unrelated.arch_db, self.generic.arch_db), before)
