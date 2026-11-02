# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.l10n_ro_zip import apply_zip_delta, remove_duplicate_streets

# rows of res_zip.sql named in data/res_zip_delta.sql
GONE_ID = 1789  # Bacau, 600057: no longer listed by the post office
UPDATED_ID = 2052  # Bacau, 600001: gets its post office


@tagged("post_install", "-at_install")
class TestResZipDelta(TransactionCase):
    def _count(self):
        self.env.cr.execute("SELECT COUNT(*) FROM res_zip")
        return self.env.cr.fetchone()[0]

    def test_apply_twice(self):
        """The delta is already applied on install: applying it again changes nothing."""
        count = self._count()
        apply_zip_delta(self.env)
        self.assertEqual(self._count(), count)
        self.assertEqual(self.env["res.zip"].browse(UPDATED_ID).office, "Bacau 1 Oficiu")

    def test_gone_row_used_by_partner_kept(self):
        """A row the post office no longer lists stays while a partner uses it."""
        self.env.cr.execute(
            """INSERT INTO res_zip (id, state, city, street_type, street_name, name, sector, office, address)
               VALUES (%s, 'Bacau', 'Bacau', 'Strada', 'Test', '600057', '', '', '')
               ON CONFLICT (id) DO NOTHING""",
            (GONE_ID,),
        )
        zip_code = self.env["res.zip"].browse(GONE_ID)
        partner = self.env["res.partner"].create({"name": "Zip delta partner", "zip_id": zip_code.id})
        self.env.flush_all()
        apply_zip_delta(self.env)
        self.assertTrue(zip_code.exists())
        self.assertEqual(partner.zip_id, zip_code)

    def test_other_row_with_same_id_untouched(self):
        """A row with a delta id but another city (res_zip not from res_zip.sql) is left alone."""
        self.env.cr.execute("UPDATE res_zip SET city = 'Zzother', office = '' WHERE id = %s", (UPDATED_ID,))
        apply_zip_delta(self.env)
        self.env.invalidate_all()
        zip_code = self.env["res.zip"].browse(UPDATED_ID)
        self.assertEqual(zip_code.city, "Zzother")
        self.assertFalse(zip_code.office)

    def test_new_row_gets_links(self):
        """A row the delta inserts gets country, county and city, as on an upgrade (no post_init_hook)."""
        # a street of Buzău the post office lists and res_zip.sql did not have
        domain = [("city", "=", "Buzau"), ("street_name", "=", "Cosmin"), ("name", "=", "120162")]
        row = self.env["res.zip"].search(domain, limit=1)
        self.assertTrue(row, "the delta is applied on install")
        street = (row.street_type, row.street_name)
        self.env.cr.execute("DELETE FROM res_zip WHERE id = %s", (row.id,))
        self.env.invalidate_all()
        apply_zip_delta(self.env)
        new_row = self.env["res.zip"].search(
            domain + [("street_type", "=", street[0]), ("street_name", "=", street[1])]
        )
        self.assertEqual(len(new_row), 1)
        self.assertEqual(new_row.country_id, self.env.ref("base.ro"))
        self.assertEqual(new_row.state_id, self.env.ref("base.RO_BZ"))
        if "l10n_ro_municipality" in self.env["res.city"]._fields:
            # the localities come with l10n_ro_city, when it is installed
            self.assertEqual(new_row.city_id.state_id, new_row.state_id)

    def test_remove_duplicate_streets(self):
        """A copy of a street inserted after res_zip.sql goes, unless a partner uses it."""
        self.env.flush_all()
        self.env.cr.execute(
            "SELECT state, city, street_type, street_name, name, sector, office, address FROM res_zip WHERE id = %s",
            (UPDATED_ID,),
        )
        values = self.env.cr.fetchone()
        copies = []
        for _i in range(2):
            self.env.cr.execute(
                """INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                values,
            )
            copies.append(self.env.cr.fetchone()[0])
        partner = self.env["res.partner"].create({"name": "Zip copy partner", "zip_id": copies[1]})
        self.env.flush_all()
        remove_duplicate_streets(self.env)
        self.env.invalidate_all()
        zips = self.env["res.zip"].browse([UPDATED_ID] + copies).exists()
        self.assertEqual(zips.ids, [UPDATED_ID, copies[1]])
        self.assertEqual(partner.zip_id.id, copies[1])
