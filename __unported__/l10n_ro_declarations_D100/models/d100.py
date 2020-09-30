# -*- coding: utf-8 -*-
# ©  2018 Terrabit
# See README.rst file on addons root folder for license details


from odoo import api, fields, models
from odoo.tools import safe_eval
from odoo import tools


class D100Report(models.TransientModel):
    _name = "l10n_ro.d100_report"
    _inherit = "l10n_ro.d000_report"
    _description = "Declaration 100"
    _code = "D100"

    item_ids = fields.One2many("l10n_ro.d100", "report_id", string="Items")


class D100(models.TransientModel):
    _name = "l10n_ro.d100"
    _description = "Declaration 100"
    _order = "report_id,partner_type"

    report_id = fields.Many2one("l10n_ro.d100_report")
