# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.l10n_ro_zip import link_cities


@tagged("post_install", "-at_install")
class TestResZipLinkCities(TransactionCase):
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
        rows = self._relink([("city", "=", "Popesti-Leordeni")])
        self.assertEqual(rows.city_id, self.env.ref("l10n_ro_city.RO_179542"))
        rows = self._relink([("city", "=", "Miercurea-Ciuc"), ("name", "=", "530100")])
        self.assertEqual(rows.city_id, self.env.ref("l10n_ro_city.RO_83339"))

    def test_village_with_commune(self):
        """ "Lunca (Vidra)" is the village Lunca of the commune Vidra, Alba."""
        rows = self._relink([("city", "=", "Lunca (Vidra)"), ("state_id", "=", self.env.ref("base.RO_AB").id)])
        self.assertEqual(rows.city_id.name, "Lunca")
        self.assertEqual(rows.city_id.l10n_ro_municipality, "Vidra")

    def test_broken_s_comma(self):
        """The old res_zip.sql has "ª" for "Ș"; of the two Ștefănești of Argeș, the postal code decides."""
        rows = self._relink([("city", "=", "ªtefanesti"), ("state_id", "=", self.env.ref("base.RO_AG").id)])
        self.assertEqual(rows.city_id.name, "Ștefănești")
        self.assertEqual(rows.city_id.zipcode, rows.name)

    def test_new_town(self):
        """Breaza, Prahova, added to l10n_ro_city as a town."""
        rows = self._relink([("city", "=", "Breaza"), ("state_id", "=", self.env.ref("base.RO_PH").id)])
        self.assertEqual(rows.city_id, self.env.ref("l10n_ro_city.RO_131103"))
