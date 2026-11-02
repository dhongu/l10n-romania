# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tools.misc import file_path

from odoo.addons.l10n_ro_zip import link_localities

_logger = logging.getLogger(__name__)


def apply_osm_streets(env):
    """Insert the streets of data/res_zip_osm.sql (made by l10n_ro_zip/tools/build_delta.py).
    A street already present is skipped: the file can be applied more than once."""
    with open(file_path("l10n_ro_zip_osm/data/res_zip_osm.sql"), encoding="utf-8") as sql_file:
        # the file is also run with psql: its BEGIN/COMMIT would end Odoo's transaction
        sql_script = "".join(line for line in sql_file if line.strip() not in ("BEGIN;", "COMMIT;"))
    env.cr.execute(sql_script)


def post_init_hook(env):
    _logger.info("Applying the streets of small towns from OpenStreetMap")
    apply_osm_streets(env)
    link_localities(env)
