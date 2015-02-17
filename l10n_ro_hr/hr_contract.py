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


class hr_insurance_type (models.Model):
    _name = 'hr.insurance.type'
    _description = "Employee insurance type"

    type = fields.Selection(
        [('1', 'A-B'), ('2', 'C')], 'Type', help='Insurance type')
    code = fields.Char('Code', required=True, help='Insurance code')
    name = fields.Char('Name',  required=True, help='Insurance name')


class hr_contract(models.Model):
    _inherit = 'hr.contract'

    period_type = fields.Boolean(
        'Determined Period', help="The contract period type")
    suspended = fields.Boolean('Is the suspended?')
    sus_date_from = fields.Date('Contract suspended from Date')
    sus_date_to = fields.Date('Contract suspended to Date')
    pensioneer = fields.Boolean(
        'Is he a pensioneer?', help="Is the employee a pensioneer")
    work_norm = fields.Selection([('N', 'cu norma intreaga'),
                                  ('P1', 'cu timp de lucru partial de 1 ora'),
                                  ('P2', 'cu timp de lucru partial de 2 ore'),
                                  ('P3', 'cu timp de lucru partial de 3 ore'),
                                  ('P4', 'cu timp de lucru partial de 4 ore'),
                                  ('P5', 'cu timp de lucru partial de 5 ore'),
                                  ('P6', 'cu timp de lucru partial de 6 ore'),
                                  ('P7', 'cu timp de lucru partial de 7 ore')],
                                 string='Work Norm',
                                 required=True,
                                 help="The type of work depending on worked hours")
    work_hour = fields.Selection([('6', '6 ore'),
                                  ('7', '7 ore'),
                                  ('8', '8 ore')],
                                 string='Hour per day',
                                 required=True,
                                 help="The numbers of hours/day")
    work_type = fields.Selection([('1', 'Conditii normale'),
                                  ('2', 'Conditii deosebite'),
                                  ('3', 'Conditii Speciale')],
                                 string='Work type',
                                 required=True,
                                 help="The work type based on conditions")
    insurance_type = fields.Many2one('hr.insurance.type', string='Insurance type',
                                     required=True, help="Insurance type")
    work_special = fields.Selection([('0', 'Rest'),
                                     ('1',
                                      'art.30 alin.(1) lit.a) din L263/2010'),
                                     ('2',
                                      'art.30 alin.(1) lit.b) din L263/2010 zona I radiatii'),
                                     ('3',
                                      'art.30 alin.(1) lit.b) din L263/2010 zona II radiatii'),
                                     ('4',
                                      'art.30 alin.(1) lit.c) din L263/2010 (Militari)'),
                                     ('5',
                                      'art.30 alin.(1) lit.d) din L263/2010 (Aviatori)'),
                                     (
                                         '6', 'art.30 alin.(1) lit.e) din L263/2010 (cf anexa 2,3 din L263)'),
                                     ('7', 'art.30 alin.(1) lit.f )din L263/2010 (Artisti))])')],
                                    string='Special Conditions', help="Special condition of work")
    sign_date = fields.Date(
        'Date', required=True, help="Date of signing the contract")
