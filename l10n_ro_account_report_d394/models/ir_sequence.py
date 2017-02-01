# -*- coding: utf-8 -*-
# ©  2016 Forest and Biomass Romania
# See README.rst file on addons root folder for license details

from openerp import models, fields

SEQUENCE_TYPE = [
    ('normal', 'Invoice'),
    ('autoinv1', 'Customer Auto Invoicing'),
    ('autoinv2', 'Supplier  Auto Invoicing')
]


class IRSequence(models.Model):
    _inherit = 'ir.sequence'

    sequence_type = fields.Selection(SEQUENCE_TYPE, default='normal',
                                     string='Sequence Type')
    number_first = fields.Integer('Serie First Number')
    number_last = fields.Integer('Serie Last Number')
    partner_id = fields.Many2one('res.partner', 'Partner')
