# Copyright (C) 2026 Terrabit
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.l10n_ro_zip_osm import apply_osm_streets

HUSI = [("city", "=", "Husi"), ("street_name", "!=", False), ("name", "=", "735100")]


@tagged("post_install", "-at_install")
class TestOsmStreets(TransactionCase):
    def _count(self):
        self.env.cr.execute("SELECT COUNT(*) FROM res_zip")
        return self.env.cr.fetchone()[0]

    def test_streets_installed(self):
        """The streets of Huși, a town with a single postal code, come with the module."""
        rows = self.env["res.zip"].search(HUSI)
        self.assertGreater(len(rows), 100)
        self.assertEqual(rows.state_id, self.env.ref("base.RO_VS"))

    def test_apply_twice(self):
        """Applying the file again inserts nothing."""
        count = self._count()
        apply_osm_streets(self.env)
        self.assertEqual(self._count(), count)

    def test_new_row_gets_links(self):
        """A street the file inserts gets country and county, as on an upgrade (no post_init_hook)."""
        row = self.env["res.zip"].search(HUSI, limit=1)
        street = (row.street_type, row.street_name)
        self.env.cr.execute("DELETE FROM res_zip WHERE id = %s", (row.id,))
        self.env.invalidate_all()
        apply_osm_streets(self.env)
        new_row = self.env["res.zip"].search(HUSI + [("street_type", "=", street[0]), ("street_name", "=", street[1])])
        self.assertEqual(len(new_row), 1)
        self.assertEqual(new_row.country_id, self.env.ref("base.ro"))
        self.assertEqual(new_row.state_id, self.env.ref("base.RO_VS"))
        if self.env.ref("l10n_ro_city.RO_161838", raise_if_not_found=False):
            # the localities come with l10n_ro_city, when it is installed
            self.assertEqual(new_row.city_id.zipcode, "735100")
