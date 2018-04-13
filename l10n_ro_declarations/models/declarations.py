# -*- coding: utf-8 -*-
# ©  2018 Terrabit
# See README.rst file on addons root folder for license details

from odoo import api, fields, models
from odoo.tools import safe_eval


class Declaration(models.Model):
    _name = "l10n_ro.declaration"
    _description = "Declaration"

    name = fields.Char('Name', required=True)
    code = fields.Selection([('D100', 'D100'), ('D300', 'D300'), ('D394', 'D394')])
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)

    data_xdp = fields.Binary(string='XDP file')


