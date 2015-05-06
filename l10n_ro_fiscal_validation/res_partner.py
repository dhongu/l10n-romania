# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2014 FOREST AND BIOMASS SERVICES ROMANIA SA (http://www.forbiom.eu).
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

import os
from datetime import date
from subprocess import Popen, PIPE

from zipfile import ZipFile
from StringIO import StringIO
import requests

from openerp import models, fields, api, _
from openerp.exceptions import Warning

ANAF_URL = 'http://static.anaf.ro/static/10/Anaf/TVA_incasare/ultim_%s.zip'


class res_partner_anaf(models.Model):
    _name = "res.partner.anaf"
    _description = "ANAF History about VAT on Payment"
    _order = "vat, operation_date DESC, end_date, start_date"

    vat = fields.Char('VAT', select=True)
    start_date = fields.Date('Start Date', select=True)
    end_date = fields.Date('End Date', select=True)
    publish_date = fields.Date('Publish Date')
    operation_date = fields.Date('Operation Date')
    operation_type = fields.Selection([('I', 'Register'),
                                       ('E', 'Fix error'),
                                       ('D', 'Removal')],
                                      'Operation Type')


class res_partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    @api.one
    @api.depends('vat')
    def _compute_vat(self):
        self.vat_number = self.vat and self.vat[2:].replace(' ', '')

    @api.one
    @api.depends('vat_number')
    def _compute_anaf_history(self):
        history = self.env['res.partner.anaf'].search(
            [('vat', '=', self.vat_number)])
        if history:
            self.anaf_history = [(6, 0, [line.id for line in history])]

    vat_number = fields.Char('VAT', compute='_compute_vat')
    anaf_history = fields.One2many(
        'res.partner.anaf',
        compute='_compute_anaf_history',
        string='ANAF History',
        readonly=True
    )

    # Grab VAT on Payment data from ANAF, update table - SQL injection
    @api.model
    def _download_anaf_data(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        istoric = os.path.join(path, "istoric.txt")
        if os.path.exists(istoric):
            modify = date.fromtimestamp(os.path.getmtime(istoric))
        else:
            modify = date.fromtimestamp(0)
        if bool(date.today() - modify):
            result = requests.get(ANAF_URL % date.today().strftime('%Y%m%d'))
            if result.status_code == requests.codes.ok:
                files = ZipFile(StringIO(result.content))
                files.extractall(path=str(path))

    @api.model
    def _insert_relevant_anaf_data(self, partners):
        vat_numbers = [
            p.vat_number for p in partners if p.vat.lower().startswith('ro')]
        if vat_numbers == []:
            return
        istoric = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'data',
            'istoric.txt')
        vat_regex = '^[0-9]+#(%s)#' % '|'.join(vat_numbers)
        anaf_data = Popen(
            ['egrep', vat_regex, istoric],
            stdout=PIPE
        )
        (process_lines, err) = anaf_data.communicate()
        process_lines = [x.split('#') for x in process_lines.split()]
        lines = self.env['res.partner.anaf'].search([
            ('id', 'in', [int(x[0]) for x in process_lines])])
        line_ids = [l.id for l in lines]
        for line in process_lines:
            if int(line[0]) not in line_ids:
                for k, v in enumerate(line):
                    if k == 0:
                        continue
                    elif v == '':
                        line[k] = 'NULL'
                    else:
                        line[k] = "'%s'" % v
                self._cr.execute("""
INSERT INTO res_partner_anaf
    (id,vat,start_date, end_date, publish_date, operation_date, operation_type)
VALUES
    %s""" % '(' + ','.join(line) + ')')

    @api.multi
    def _check_vat_on_payment(self):
        ctx = dict(self._context)
        vat_on_payment = False
        if self.anaf_history:
            if len(self.anaf_history) > 1 and ctx.get('check_date', False):
                lines = self.env['res.partner.anaf'].search([
                    ('id', 'in', [rec.id for rec in self.anaf_history]),
                    ('start_date', '<=', ctx['check_date']),
                    ('end_date', '>=', ctx['check_date'])
                ])
                if lines and lines[0].operation_type == 'D':
                    vat_on_payment = True
            else:
                if self.anaf_history[0].operation_type == 'I':
                    vat_on_payment = True
        return vat_on_payment

    @api.one
    def check_vat_on_payment(self):
        ctx = dict(self._context)
        ctx.update({'check_date': date.today()})
        self.vat_on_payment = self.with_context(ctx)._check_vat_on_payment()

    @api.multi
    def _check_vat_subjected(self):
        vat_s = vat_number = vat_country = False
        if self.vat:
            vat_country, vat_number = self._split_vat(self.vat)
        if vat_number and vat_country and vat_country.upper() == 'RO':
            res = requests.get(
                'http://openapi.ro/api/companies/' +
                str(vat_number) +
                '.json')
            if res.status_code == 200:
                res = res.json()
                if res['vat'] == '1':
                    vat_s = True
        elif vat_number and vat_country:
            vat_s = self.vies_vat_check(vat_country, vat_number)
        return vat_s

    @api.one
    def check_vat_subjected(self):
        if self.vat_on_payment:
            self.vat_subjected = True
        else:
            self.vat_subjected = self._check_vat_subjected()

    @api.multi
    def update_vat_one(self):
        self.check_vat_on_payment()
        self.check_vat_subjected()

    @api.one
    def button_get_partner_data(self):
        super(res_partner, self).button_get_partner_data()
        self._insert_relevant_anaf_data([self[0]])
        self.check_vat_on_payment()

    @api.multi
    def update_vat_all(self):
        self._download_anaf_data()
        partners = self.search([('vat', '!=', False)])
        self._insert_relevant_anaf_data(partners)
        for partner in partners:
            partner.check_vat_on_payment()
            partner.check_vat_subjected()

    @api.model
    def _update_vat_all(self):
        self.update_vat_all()
