# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import SUPERUSER_ID, api

from odoo.addons.l10n_ro_zip import link_localities, link_states


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Giurgiu had the prefix 87 instead of 08 (l10n_ro_city 19.0.1.10.1), and Bucharest had none
    # outside the sectors: the county now comes from the module's own list of prefixes
    link_states(env)
    # the codes that got their county now, the towns added or renamed in l10n_ro_city 19.0.1.10.2,
    # and the names written differently
    link_localities(env)
