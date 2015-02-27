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


class res_company_caen(models.Model):
    _name = "res.company.caen"
    _description = "CAEN codes for Romanian Companies"

    code = fields.Char('CAEN code', required=True, help='CAEN code')
    name = fields.Char('CAEN name', required=True, help='CAEN name')
    trisc = fields.Float('Accident Coefficient', required=True, digits=(0,4))


class res_company(models.Model):
    _inherit = "res.company"

    codcaen = fields.Many2one(
        'res.company.caen', 'CAEN code', help="Company CAEN code.")
    coefacc = fields.Float(
        string='Accident Coefficient', related='codcaen.trisc', digits=(0,4))
