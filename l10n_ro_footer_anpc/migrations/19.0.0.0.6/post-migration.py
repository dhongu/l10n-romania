# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import SUPERUSER_ID, api

from odoo.addons.l10n_ro_footer_anpc.migration import migrate_legacy_footer_views


def migrate(cr, version):
    migrate_legacy_footer_views(api.Environment(cr, SUPERUSER_ID, {}))
