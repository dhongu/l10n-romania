# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import SUPERUSER_ID, api
from odoo.tools import SQL

from odoo.addons.l10n_ro_zip import link_cities


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Giurgiu had the prefix 87 instead of 08 (l10n_ro_city 19.0.1.10.1): its rows have no county
    cr.execute(
        SQL(
            """
            UPDATE res_zip z SET state_id = s.id
              FROM res_country_state s
             WHERE z.state_id IS NULL
               AND COALESCE(s.l10n_ro_prefix_zip, '') != ''
               AND SUBSTRING(z.name, 1, 2) = s.l10n_ro_prefix_zip
            """
        )
    )
    cr.execute(SQL("CREATE EXTENSION IF NOT EXISTS unaccent"))
    # the towns added or renamed in l10n_ro_city 19.0.1.10.2, and the names written differently
    link_cities(env)
