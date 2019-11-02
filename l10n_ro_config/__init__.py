# -*- coding: utf-8 -*-
# ©  2015 Forest and Biomass Services Romania
# See README.rst file on addons root folder for license details

from . import models
from odoo import api, SUPERUSER_ID, _, tools



def _create_unaccent(cr, registry):
    """Setting journal and property field (if needed)"""

    env = api.Environment(cr, SUPERUSER_ID, {})
    env.cr.execute("CREATE EXTENSION  IF NOT EXISTS unaccent;")