# -*- coding: utf-8 -*-
# ©  2015 Forest and Biomass Services Romania
# See README.rst file on addons root folder for license details

from . import models
from odoo import api, SUPERUSER_ID, _, tools
import psycopg2


def _create_unaccent(cr, registry):
    """Setting journal and property field (if needed)"""

    # env = api.Environment(cr, SUPERUSER_ID, {})
    # env.cr.execute("CREATE EXTENSION  IF NOT EXISTS unaccent;")
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        if tools.config['unaccent']:
            try:
                with cr.savepoint():
                    cr.execute("CREATE EXTENSION IF NOT EXISTS  unaccent")
            except psycopg2.Error:
                pass