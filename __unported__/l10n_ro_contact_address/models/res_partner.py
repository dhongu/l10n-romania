# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2016 FOREST AND BIOMASS SERVICES ROMANIA SA
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

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('add_street', 'add_number', 'add_block', 'add_staircase', 'add_flat')
    def _get_street(self):
        new_street = ''
        if self.add_street:
            new_street += 'Str. ' + self.add_street + ' '
        if self.add_number:
            new_street += 'Nr. ' + self.add_number + ' '
        if self.add_block:
            new_street += 'Bl. ' + self.add_block + ' '
        if self.add_staircase:
            new_street += 'Sc. ' + self.add_staircase + ' '
        if self.add_flat:
            new_street += 'Ap. ' + self.add_flat + ' '
        self.street = new_street.strip()

    add_street = fields.Char('Street name')
    add_number = fields.Char('Street number')
    add_block = fields.Char('Block number')
    add_staircase = fields.Char('Staircase number')
    add_flat = fields.Char('Flat number')




