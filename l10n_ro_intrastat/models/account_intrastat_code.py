# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api




class AccountIntrastatCode(models.Model):
    '''
    Codes used for the intrastat reporting.

    The list of commodity codes is available on:
    https://www.cbs.nl/en-gb/deelnemers%20enquetes/overzicht/bedrijven/onderzoek/lopend/international-trade-in-goods/idep-code-lists
    '''
    _name = 'account.intrastat.code'
    _description = 'Intrastat Code'
    _translate = False

    name = fields.Char(string='Name')
    code = fields.Char(string='Code', required=True)

    description = fields.Char(string='Description')
    suppl_unit_code = fields.Char('SupplUnitCode')


    @api.multi
    def name_get(self):
        result = []
        for r in self:
            text = r.name or r.description
            result.append((r.id, text and '%s %s' % (r.code, text) or r.code))
        return result

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        domain = args + ['|', '|', ('code', operator, name), ('name', operator, name), ('description', operator, name)]
        return super(AccountIntrastatCode, self).search(domain, limit=limit).name_get()

    _sql_constraints = [
        ('intrastat_region_code_unique', 'UNIQUE (code )', 'The code must be unique.'),
    ]
