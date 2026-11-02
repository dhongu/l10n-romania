# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.l10n_ro_zip import link_cities, link_sectors, link_states


@tagged("post_install", "-at_install")
class TestResZipLinkCities(TransactionCase):
    """The links work with the localities of l10n_ro_city and without it: a locality the test needs
    and the database does not have is created."""

    def _city(self, xmlid, name, state, zipcode=False):
        city = xmlid and self.env.ref(xmlid, raise_if_not_found=False)
        if city:
            return city
        return self.env["res.city"].create(
            {"name": name, "country_id": state.country_id.id, "state_id": state.id, "zipcode": zipcode}
        )

    def _relink(self, domain):
        """Unlink the rows from their city, as on a database installed before, and link again."""
        rows = self.env["res.zip"].search(domain)
        self.assertTrue(rows, f"no res.zip for {domain}")
        rows.city_id = False
        self.env.flush_all()
        link_cities(self.env)
        self.env.invalidate_all()
        return rows

    def test_hyphen(self):
        """The post office writes "Popesti-Leordeni" and "Miercurea-Ciuc", the list Miercurea Ciuc."""
        city = self._city("l10n_ro_city.RO_179542", "Popești Leordeni", self.env.ref("base.RO_IF"), "077160")
        rows = self._relink([("city", "=", "Popesti-Leordeni")])
        self.assertEqual(rows.city_id, city)
        city = self._city("l10n_ro_city.RO_83339", "Miercurea Ciuc", self.env.ref("base.RO_HR"))
        rows = self._relink([("city", "=", "Miercurea-Ciuc"), ("name", "=", "530100")])
        self.assertEqual(rows.city_id, city)

    def test_village_with_commune(self):
        """ "Lunca (Vidra)" is the village Lunca of the commune Vidra, Alba."""
        if "l10n_ro_municipality" not in self.env["res.city"]._fields:
            self.skipTest("the communes of the villages come with l10n_ro_city")
        rows = self._relink([("city", "=", "Lunca (Vidra)"), ("state_id", "=", self.env.ref("base.RO_AB").id)])
        self.assertEqual(rows.city_id.name, "Lunca")
        self.assertEqual(rows.city_id.l10n_ro_municipality, "Vidra")

    def test_broken_s_comma(self):
        """The old res_zip.sql has "ª" for "Ș"; of the two Ștefănești of Argeș, the postal code decides."""
        state = self.env.ref("base.RO_AG")
        rows = self.env["res.zip"].search([("city", "=", "ªtefanesti"), ("state_id", "=", state.id)])
        self.assertTrue(rows)
        if not self.env["res.city"].search_count([("name", "=", "Ștefănești"), ("state_id", "=", state.id)]):
            for zipcode in (rows[0].name, "117000"):
                self._city("", "Ștefănești", state, zipcode)
        rows = self._relink([("id", "in", rows.ids)])
        self.assertEqual(rows.city_id.name, "Ștefănești")
        self.assertEqual(rows.city_id.zipcode, rows.name)

    def test_new_town(self):
        """Breaza, Prahova, added to l10n_ro_city as a town (19.0.1.10.2): its rows get linked on update."""
        city = self._city("l10n_ro_city.RO_131103", "Breaza", self.env.ref("base.RO_PH"), "105400")
        rows = self._relink([("city", "=", "Breaza"), ("state_id", "=", city.state_id.id)])
        self.assertEqual(rows.city_id, city)

    def test_states_from_prefix(self):
        """The county comes from the first two digits of the code, without l10n_ro_city:
        Giurgiu is 08 (87 in l10n_ro_city before 19.0.1.10.1), Bucharest 01 to 06."""
        rows = self.env["res.zip"].search([("name", "in", ("080051", "010011", "061344"))])
        self.assertEqual(len(rows), 3)
        rows.state_id = False
        self.env.flush_all()
        link_states(self.env)
        self.env.invalidate_all()
        by_code = {row.name: row.state_id for row in rows}
        self.assertEqual(by_code["080051"], self.env.ref("base.RO_GR"))
        self.assertEqual(by_code["010011"], self.env.ref("base.RO_B"))
        self.assertEqual(by_code["061344"], self.env.ref("base.RO_B"))

    def test_sector(self):
        """A row of Bucharest goes to the locality of its sector, found by name."""
        sector = self._city("l10n_ro_city.RO_179169", "Sector3", self.env.ref("base.RO_B"))
        rows = self.env["res.zip"].search([("sector", "=", "3")], limit=5)
        self.assertTrue(rows)
        rows.city_id = False
        self.env.flush_all()
        link_sectors(self.env)
        self.env.invalidate_all()
        self.assertEqual(rows.city_id, sector)
        self.assertEqual(rows.state_id, self.env.ref("base.RO_B"))

    def test_link_on_city_create(self):
        """A Romanian locality created after the postal codes (l10n_ro_city installed in the same run or
        later) gets its codes before the commit."""
        state = self.env.ref("base.RO_PH")
        rows = self.env["res.zip"].search([("city", "=", "Breaza"), ("state_id", "=", state.id)])
        self.assertTrue(rows)
        self.env["res.city"].search([("name", "=", "Breaza"), ("state_id", "=", state.id)]).unlink()
        self.env.flush_all()
        self.assertFalse(rows.city_id)
        city = self.env["res.city"].create(
            {"name": "Breaza", "country_id": state.country_id.id, "state_id": state.id, "zipcode": "105400"}
        )
        self.env.cr.precommit.run()
        self.assertEqual(rows.city_id, city)
