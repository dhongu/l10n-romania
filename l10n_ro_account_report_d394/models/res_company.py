# -*- coding: utf-8 -*-
# ©  2016 Forest and Biomass Romania
# See README.rst file on addons root folder for license details

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    anaf_cross_opt = fields.Boolean('ANAF Crosschecking')
    is_fiscal_repr = fields.Boolean('Is Fiscal representative')
    fiscal_repr_id = fields.Many2one('res.partner', 'Fiscal representative')
