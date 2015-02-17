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
from datetime import datetime


class hr_employee_care(models.Model):
    _name = 'hr.employee.care'
    _description = "Employee person in care"

    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    name = fields.Char(
        'Person care name', required=True, help='Person in care name')
    ssnid = fields.Char('SSN No', required=True, help='Social Security Number')
    relation = fields.Selection([('husband', 'Husband'),
                                 ('wife', 'Wife'),
                                 ('child', 'Child'),
                                 ('firstdegree', 'First degree relationship'),
                                 ('secdegree', 'Second degree relationship')],
                                string='Person relation', required=True)


class hr_employee_coinsured(models.Model):
    _name = 'hr.employee.coinsured'
    _description = "Employee co-insured persons"

    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    name = fields.Char(
        'Person care name', required=True, help='Person in care name')
    ssnid = fields.Char('SSN No', required=True, help='Social Security Number')
    relation = fields.Selection([('husband', 'Husband'),
                                 ('wife', 'Wife'),
                                 ('child', 'Child'),
                                 ('firstdegree', 'First degree relationship'),
                                 ('secdegree', 'Second degree relationship')],
                                string='Person relation',
                                required=True)


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.one
    @api.depends('person_care_ids')
    def _number_personcare(self):
        self.person_in_care = len(self.person_care_ids)

    ssnid_init = fields.Char(
        'Initial SSN No', help='Initial Social Security Number')
    first_name_init = fields.Char('Initial Name')
    last_name_init = fields.Char('Initial First Name')
    casang = fields.Selection([('AB', 'Alba'), ('AR', 'Arad'),
                               ('AG', 'Arges'), ('BC', 'Bacau'),
                               ('BH', 'Bihor'), ('BN', 'Bistrita-Nasaud'),
                               ('CS', 'Caras-Severin'), ('BT', 'Botosani'),
                               ('BR', 'Braila'), ('BV', 'Brasov'),
                               ('BZ', 'Buzau'), ('CL', 'Calarasi'),
                               ('CJ', 'Cluj'), ('CT', 'Constanta'),
                               ('CV', 'Covasna'), ('DB', 'Dambovita'),
                               ('DJ', 'Dolj'), ('GL', 'Galati'),
                               ('GR', 'Giurgiu'), ('GJ', 'Gorj'),
                               ('HR', 'Harghita'), ('HD', 'Hunedoara'),
                               ('IL', 'Ialomita'), ('IS', 'Iasi'),
                               ('IF', 'Ilfov'), ('MM', 'Maramures'),
                               ('MH', 'Mehedinti'), ('MS', 'Mures'),
                               ('NT', 'Neamt'), ('OT', 'Olt'),
                               ('PH', 'Prahova'), ('SJ', 'Salaj'),
                               ('SM', 'Satu Mare'), ('SB', 'Sibiu'),
                               ('SV', 'Suceava'), ('TR', 'Teleorman'),
                               ('TM', 'Timis'), ('TL', 'Tulcea'),
                               ('VS', 'Vaslui'), ('VL', 'Valcea'),
                               ('VN', 'Vrancea'), ('_B',
                                                   'CAS Municipiu Bucuresti'),
                               ('_A', 'AOPSNAJ'), ('_T', 'CASMTCT')],
                              string='Insurance', required=True)
    person_care_ids = fields.One2many(
        'hr.employee.care', 'employee_id', 'Person in care')
    person_coinsured_ids = fields.One2many(
        'hr.employee.coinsured', 'employee_id', 'Coinsured Persons')
    person_in_care = fields.Integer(string='No of persons in care',
                                    compute='_number_personcare',
                                    help='Number of persons in care')
    emit_by = fields.Char('Emmited by')
    emit_on = fields.Date('Emmited on')
