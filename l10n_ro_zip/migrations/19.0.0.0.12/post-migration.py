# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import SUPERUSER_ID, api

from odoo.addons.l10n_ro_zip import apply_zip_delta, remove_duplicate_streets


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    apply_zip_delta(env)
    # On a 19.0.0.0.11 database the previous delta matched a few streets differently and
    # inserted the street it missed: this delta puts the older row back on that street, so
    # the inserted row is now a copy of it.
    remove_duplicate_streets(env)
