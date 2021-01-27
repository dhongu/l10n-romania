# ©  2018 Terrabit
# See README.rst file on addons root folder for license details

from odoo import api, fields, models
from odoo.tools import safe_eval


class Declaration(models.Model):
    _name = "l10n_ro.declaration"
    _description = "Declaration"

    name = fields.Char("Name", required=True)
    code = fields.Selection([], required=True)
    company_id = fields.Many2one("res.company", "Company", required=True, default=lambda self: self.env.user.company_id)

    file_name_xdp = fields.Char()
    data_xdp = fields.Binary(string="XDP file", attachment=True)
