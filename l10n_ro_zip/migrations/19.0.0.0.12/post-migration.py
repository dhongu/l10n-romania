# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import SUPERUSER_ID, api

from odoo.addons.l10n_ro_zip import apply_zip_delta


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    apply_zip_delta(env)
    # On a 19.0.0.0.11 database the previous delta matched a few streets differently and
    # inserted the street it missed: this delta puts the older row back on that street, so
    # it is now there twice. Keep the older row, and never delete one a partner uses.
    cr.execute(
        """
        DELETE FROM res_zip z
         USING res_zip k
         WHERE k.id < z.id
           AND k.name = z.name AND k.state = z.state AND k.city = z.city
           AND COALESCE(k.street_type, '') = COALESCE(z.street_type, '')
           AND COALESCE(k.street_name, '') = COALESCE(z.street_name, '')
           AND NOT EXISTS (SELECT 1 FROM res_partner p WHERE p.zip_id = z.id)
        """
    )
