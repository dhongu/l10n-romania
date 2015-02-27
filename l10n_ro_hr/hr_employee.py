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
from openerp.exceptions import ValidationError
from stdnum.ro.cnp import get_birth_date, is_valid as validate_cnp
from datetime import timedelta, date

# luat de pe wikipedia:
# http://ro.wikipedia.org/wiki/Cod_numeric_personal#JJ
pob = {
    '01': u'Alba',
    '02': u'Arad',
    '03': u'Argeș',
    '04': u'Bacău',
    '05': u'Bihor',
    '06': u'Bistrița-Năsăud',
    '07': u'Botoșani',
    '08': u'Brașov',
    '09': u'Brăila',
    '10': u'Buzău',
    '11': u'Caraș-Severin',
    '12': u'Cluj',
    '13': u'Constanța',
    '14': u'Covasna',
    '15': u'Dâmbovița',
    '16': u'Dolj',
    '17': u'Galați',
    '18': u'Gorj',
    '19': u'Harghita',
    '20': u'Hunedoara',
    '21': u'Ialomița',
    '22': u'Iași',
    '23': u'Ilfov',
    '24': u'Maramureș',
    '25': u'Mehedinți',
    '26': u'Mureș',
    '27': u'Neamț',
    '28': u'Olt',
    '29': u'Prahova',
    '30': u'Satu Mare',
    '31': u'Sălaj',
    '32': u'Sibiu',
    '33': u'Suceava',
    '34': u'Teleorman',
    '35': u'Timiș',
    '36': u'Tulcea',
    '37': u'Vaslui',
    '38': u'Vâlcea',
    '39': u'Vrancea',
    '40': u'București',
    '41': u'București S.1',
    '42': u'București S.2',
    '43': u'București S.3',
    '44': u'București S.4',
    '45': u'București S.5',
    '46': u'București S.6',
    '51': u'Călărași',
    '52': u'Giurgiu',
}


class hr_employee_related(models.Model):
    _name = 'hr.employee.related'
    _description = "Employee person in care or are coinsured"

    @api.one
    @api.onchange('ssnid')
    @api.constrains('ssnid')
    def _validate_ssnid(self):
        if self.ssnid and not validate_cnp(self.ssnid):
            raise ValidationError('Invalid SSN number')

    @api.one
    @api.depends('name')
    def _first_name(self):
        try:
            self.first_name = ' '.join(self.name.split()[:-1])
        except:
            self.first_name = ''

    @api.one
    @api.depends('name')
    def _last_name(self):
        try:
            self.last_name = self.name.split()[-1]
        except:
            self.first_name = ''

    @api.one
    @api.constrains('relation', 'relation_type')
    def _validate_relation(self):
        if self.relation_type and self.relation:
            if self.relation_type in (
                    'coinsured', 'both') and not self.relation in (
                    'husband', 'wife', 'parent'):
                raise ValidationError(_("Just parents and husband/wife"))

    first_name = fields.Char('First Name', compute='_first_name', store=False)
    last_name = fields.Char('Last Name', compute='_last_name', store=False)

    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    name = fields.Char('Name', required=True, help='Related person name')
    ssnid = fields.Char('SSN No', required=True, help='Social Security Number')
    relation = fields.Selection([('husband', 'Husband'),
                                 ('wife', 'Wife'),
                                 ('parent', 'Parent'),
                                 ('child', 'Child'),
                                 ('firstdegree', 'First degree relationship'),
                                 ('secdegree', 'Second degree relationship')],
                                string='Relation', required=True)
    relation_type = fields.Selection([('in_care', 'In Care'),
                                      ('coinsured', 'Coinsured'),
                                      ('both', 'Both')],
                                     string='Relation type', required=True,
                                     select=True)


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.one
    @api.depends('person_related')
    def _number_personcare(self):
        self.person_in_care = self.person_related.search_count([
            ('relation_type', 'in', ('in_care', 'both')),
            ('employee_id', '=', self.id),
        ])

    @api.one
    @api.depends('name')
    def _first_name(self):
        try:
            self.first_name = ' '.join(self.name.split()[:-1])
        except:
            self.first_name = ''

    @api.one
    @api.depends('name')
    def _last_name(self):
        try:
            self.last_name = self.name.split()[-1]
        except:
            self.first_name = ''

    @api.one
    @api.onchange('ssnid')
    @api.constrains('ssnid')
    def _ssnid_birthday_gender(self):
        if self.ssnid and self.country_id and 'RO' in self.country_id.code.upper():
            if not validate_cnp(self.ssnid):
                raise ValidationError('Invalid SSN number')
            gender = bp = None
            if self.ssnid[7:9] in pob.keys():
                bp = pob[self.ssnid[7:9]]
            try:
                bday = get_birth_date(self.ssnid)
            except:
                bday = None
            if self.ssnid[0] in '1357':
                gender = 'male'
            elif self.ssnid[0] in '2468':
                gender = 'female'
            self.write({
                'gender': gender,
                'birthday': bday,
                'place_of_birth': bp
            })

    def _medic_exam_expires(self):
        return fields.Date.to_string(date.today() - timedelta(days = 370))

    @api.multi
    def _return_medic_exam_expiring(self):
        return self.search([
            ('active', '=', True),
            ('medic_exam', '>=', self._medic_exam_expires()),
        ])
        
    first_name = fields.Char('First Name', compute='_first_name', store=False)
    last_name = fields.Char('Last Name', compute='_last_name', store=False)
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
    person_related = fields.One2many(
        'hr.employee.related', 'employee_id', 'Related Persons')
    person_in_care = fields.Integer(string='No of persons in care',
                                    compute='_number_personcare',
                                    help='Number of persons in care')
    emit_by = fields.Char('Emmited by')
    emit_on = fields.Date('Emmited on')
    expires_on = fields.Date('Expires on')

    # override fields declared in hr_contract
    medic_exam = fields.Date('Medical Examination Date', index = True)
