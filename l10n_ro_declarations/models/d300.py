# -*- coding: utf-8 -*-
# ©  2018 Terrabit
# See README.rst file on addons root folder for license details


from odoo import api, fields, models
from odoo.tools import safe_eval
from odoo import tools


class D300Report(models.TransientModel):
    _name = "l10n_ro.d300_report"
    _description = "Declaration 300"
    _inherit = "l10n_ro.d000_report"
    _code = 'D300'


