# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, models

PRECOMMIT_KEY = "l10n_ro_zip.link_localities"


class ResCity(models.Model):
    _inherit = "res.city"

    @api.model_create_multi
    def create(self, vals_list):
        cities = super().create(vals_list)
        # The localities can come after the postal codes: l10n_ro_city installed in the same run
        # (the module does not depend on it) or later. Link the codes once, before the commit.
        precommit = self.env.cr.precommit
        if not precommit.data.get(PRECOMMIT_KEY) and cities.filtered(lambda c: c.country_id.code == "RO"):
            precommit.data[PRECOMMIT_KEY] = True
            precommit.add(self._link_zip_localities)
        return cities

    def _link_zip_localities(self):
        from odoo.addons.l10n_ro_zip import link_localities  # noqa: PLC0415 (the package imports the models)

        self.env.flush_all()
        link_localities(self.env)
        self.env["res.zip"].invalidate_model(["city_id", "state_id"])
