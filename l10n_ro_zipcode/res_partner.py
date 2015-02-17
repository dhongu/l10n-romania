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

from openerp import models, fields, api


class res_partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    @api.onchange('zipcode_id')
    def _onchange_zipcode_id(self):
        if self.zipcode_id:
            self.city_id = self.zipcode_id.city_id.id
            self.commune_id = self.zipcode_id.commune_id.id
            self.state_id = self.zipcode_id.state_id.id
            self.zone_id = self.zipcode_id.zone_id.id
            self.country_id = self.zipcode_id.country_id.id
    
    zipcode_id = fields.Many2one('res.country.zipcode', string='ZipcodeID', ondelete='set null', index=True)
    zip = fields.Char(related='zipcode_id.name', string='Zipcode', store=True)
