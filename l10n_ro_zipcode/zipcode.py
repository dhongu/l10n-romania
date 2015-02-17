# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2014 FOREST AND BIOMASS SERVICES ROMANIA SA
#    (http://www.forbiom.eu).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _


class res_country_zipcode(models.Model):
    _name = 'res.country.zipcode'
    _description = 'Country Zipcodes'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('name', '=', name)] + args, limit=limit)
        if not recs:
            recs = self.search(
                [('city_id.name', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search(
                [('commune_id.name', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search(
                [('state_id.name', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search(
                [('zone_id.name', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search(
                [('country_id.name', operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.onchange('city_id')
    def _onchange_city_id(self):
        if self.city_id:
            self.state_id = self.city_id.state_id.id
            self.zone_id = self.city_id.zone_id.id
            self.country_id = self.city_id.country_id.id

    @api.onchange('commune_id')
    def _onchange_commune_id(self):
        if self.commune_id:
            self.state_id = self.commune_id.state_id.id
            self.zone_id = self.commune_id.zone_id.id
            self.country_id = self.commune_id.country_id.id

    @api.onchange('state_id')
    def _onchange_state_id(self):
        if self.state_id:
            self.commune_id = False
            self.zone_id = self.state_id.zone_id.id
            self.country_id = self.state_id.country_id.id

    @api.onchange('zone_id')
    def _onchange_zone_id(self):
        if self.zone_id:
            self.commune_id = False
            self.state_id = False
            self.country_id = self.zone_id.country_id.id

    name = fields.Char('Name', required=True, index=True)
    area = fields.Char('Area')
    city_id = fields.Many2one('res.country.city', string='City', required=True)
    commune_id = fields.Many2one(
        'res.country.commune', string='City/Commune', required=True)
    state_id = fields.Many2one(
        'res.country.state', string='State', required=True)
    zone_id = fields.Many2one('res.country.zone', string="Zone", required=True)
    country_id = fields.Many2one(
        'res.country', string="Country", required=True)
