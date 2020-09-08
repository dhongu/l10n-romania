# -*- encoding: utf-8 -*-
##############################################################################
#
#     Romanian accounting localization for OpenERP V7
#        @author -  Fekete Mihai, Tatár Attila <atta@nvm.ro>
#     Copyright (C) 2011-2013 TOTAL PC SYSTEMS (http://www.www.erpsystems.ro).
#     Copyright (C) 2013 Tatár Attila
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

import datetime
import time

from string import maketrans
import json
import requests
from urllib2 import Request, urlopen
from stdnum.eu.vat import check_vies
from lxml import html

from openerp import models, fields, api, _
from openerp.exceptions import Warning
import unicodedata
import logging

_logger = logging.getLogger(__name__)


CEDILLATRANS = maketrans(u'\u015f\u0163\u015e\u0162'.encode(
    'utf8'), u'\u0219\u021b\u0218\u021a'.encode('utf8'))

headers = {
    "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)",
    "Content-Type": "application/json;"
}

ANAF_URL = 'https://webservicesp.anaf.ro/PlatitorTvaRest/api/v4/ws/tva'


def unaccent(text):
    text = text.replace(u'\u015f', u'\u0219')
    text = text.replace(u'\u0163', u'\u021b')
    text = text.replace(u'\u015e', u'\u0218')
    text = text.replace(u'\u0162', u'\u021a')
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)




class res_partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    name = fields.Char('Name', required=True, select=True, default=' ')
    split_vat = fields.Boolean('Split TVA')
    vat_on_payment = fields.Boolean('VAT on Payment')

    @api.model
    def _get_Anaf(self, cod):
        result = {}
        res = requests.post(ANAF_URL, json=[{'cui': cod, 'data': fields.Date.today()}], headers=headers)
        if res.status_code == 200:
            res = res.json()
        if res['found'] and res['found'][0]:
            result = res['found'][0]
            if result['data_sfarsit_ScpTVA'] and result['data_sfarsit_ScpTVA'] != ' ':
                res = requests.post(ANAF_URL, json=[{'cui': cod, 'data': result['data_sfarsit_ScpTVA']}],
                                    headers=headers)
                if res.status_code == 200:
                    res = res.json()
        if res['found'] and res['found'][0]:
            result = res['found'][0]
        # Check if the partner was deactived
        if res['notfound'] and res['notfound'][0]:
            result = res['notfound'][0]
            if result['data_sfarsit_ScpTVA'] and result['data_sfarsit_ScpTVA'] != ' ':
                res = requests.post(ANAF_URL, json=[{'cui': cod, 'data': result['data_sfarsit_ScpTVA']}],
                                    headers=headers)
                if res.status_code == 200:
                    res = res.json()
                    if res['found'] and res['found'][0]:
                        result = res['found'][0]
                    if res['notfound'] and res['notfound'][0]:
                        result = res['notfound'][0]
        return result

    @api.model
    def _Anaf_to_Odoo(self, result):
        res = {'name': result['denumire'],
               'vat_subjected': result['scpTVA'],
               'split_vat': result['statusSplitTVA'],
               'vat_on_payment': result['statusTvaIncasare']}
        addr = ''
        if result['adresa']:
            result['adresa'] = result['adresa'].replace('MUNICIPIUL', 'MUN.')
            result['adresa'] = result['adresa'].replace(u'ORŞ.', 'ORS.')
            lines = [x for x in result['adresa'].split(",") if x]
            nostreet = True
            listabr = ['JUD.', 'MUN.', 'ORS.', 'COM.',
                       'STR.', 'NR.', 'ET.', 'AP.']
            for line in lines:
                if 'STR.' in line:
                    nostreet = False
                    break
            if nostreet:
                addr = 'Principala'
            city = ''
            try:
                for line in lines:
                    if not any([x in line for x in listabr]):
                        addr = line.strip().title()
                for line in lines:
                    line = unaccent(line)  # line.encode('utf8').translate(CEDILLATRANS).decode('utf8')
                    if 'JUD.' in line:
                        state = self.env['res.country.state'].search(
                            [('name', '=', line.replace('JUD.', '').strip().title())])
                        if state:
                            res['state_id'] = state[0].id
                    if 'MUN.' in line:
                        city = line.replace('MUN.', '').strip().title()
                    elif 'ORS.' in line:
                        city = line.replace('ORS.', '').strip().title()
                    elif 'COM.' in line:
                        sat = line.replace('SAT ', '').strip().title().split(" ")
                        city = ''
                        for satname in sat:
                            if '.' not in satname:
                                city += ' ' + satname
                            else:
                                break
                        city = city.strip()
                    if 'STR.' in line:
                        addr += line.replace('STR.', '').strip().title()
                    if 'NR.' in line:
                        addr += ' ' + line.replace('NR.', '').strip().title()
                    if 'AP.' in line:
                        addr += '/' + line.replace('AP.', '').strip().title()
            except:
                pass
            if city:
                res['city'] = city.replace('-', ' ').title()
        res['street'] = addr.strip()
        return res

    @api.model
    def _get_Openapi(self, cod):
        result = {}
        openapi_key = self.env['ir.config_parameter'].get_param(key="openapi_key", default=False)
        if openapi_key:
            try:
                headers = {
                    "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)",
                    "Content-Type": "application/json;",
                    'x-api-key': openapi_key
                }

                request = Request('https://api.openapi.ro/api/companies/%s' % cod, headers=headers)
                response = urlopen(request)
                status_code = response.getcode()

                if status_code == 200:

                    res = json.loads(response.read())
                    state = False
                    if res['judet']:
                        state = self.env['res.country.state'].search([('name', '=', res['judet'].title())])
                        if state:
                            state = state[0].id

                    result = {
                        'name': res['denumire'],
                        'nrc': res['numar_reg_com'] or '',
                        'street': res['adresa'].title(),

                        'phone': res['telefon'] and res['telefon'] or '',
                        'fax': res['fax'] and res['fax'] or '',
                        'zip': res['cod_postal'] and res['cod_postal'] or '',
                        'vat_subjected': bool(res['tva']),
                        'state_id': state,
                        'company_type': 'company'
                    }
            except Exception as e:
                _logger.error("Error apel api.openapi.ro %s " % str(e))
        else:
            try:
                res = requests.get('http://legacy.openapi.ro/api/companies/%s.json' % cod)
                if res.status_code == 200:
                    res = res.json()
                    state = False
                    if res['state']:
                        state = self.env['res.country.state'].search([('name', '=', res['state'].title())])
                        if state:
                            state = state[0].id

                    result = {
                        'name': res['name'],
                        'nrc': res['registration_id'] and res['registration_id'].upper() or '',
                        'street': res['address'].title(),
                        'city': res['city'].title(),
                        'phone': res['phone'] and res['phone'] or '',
                        'fax': res['fax'] and res['fax'] or '',
                        'zip': res['zip'] and res['zip'] or '',
                        'vat_subjected': bool(res['vat'] == '1'),
                        'state_id': state,
                        'company_type': 'company'
                    }
            except Exception as e:
                _logger.error("Error apel legacy.openapi.ro %s " % str(e))

        return result



    @api.one
    @api.constrains('is_company', 'vat', 'parent_id', 'company_id')
    def check_vat_unique(self):
        if not self.vat:
            return True

        if not self.is_company:
            return True

        # get first parent
        parent = self
        while parent.parent_id:
            parent = parent.parent_id

        same_vat_partners = self.search([
            ('is_company','=', True),
            ('vat', '=', self.vat),
            ('vat', '!=', False),
            ('company_id', '=', self.company_id.id),
            ])

        if same_vat_partners:
            related_partners = self.search([
                ('id', 'child_of', parent.id),
                ('company_id', '=', self.company_id.id),
                ])
            same_vat_partners = self.search([
                ('id', 'in', same_vat_partners.ids),
                ('id', 'not in', related_partners.ids),
                ('company_id', '=', self.company_id.id),
                ])
            if same_vat_partners:
                raise Warning(_(
                    'Partner vat must be unique per company except on partner with parent/childe relationship. Partners with same vat and not related, are: %s!') % (', '.join(x.name for x in same_vat_partners)))

    @api.multi
    def button_get_partner_data(self):
        def _check_vat_ro(vat):
            return bool(len(part.name.strip()) > 2 and
                        part.name.strip().upper()[:2] == 'RO' and
                        part.name.strip()[2:].isdigit())

        part = self[0]

        vat = part.vat
        if vat:
            self.write({'vat': part.vat.upper().replace(" ", "")})
        elif part.name and len(part.name.strip()) > 2 and part.name.strip().upper()[:2] == 'RO' and part.name.strip()[
                                                                                                    2:].isdigit():
            self.write({'vat': part.name.upper().replace(" ", "")})
        if not part.vat and part.name:
            try:
                vat_country, vat_number = self._split_vat(part.name.upper().replace(" ", ""))
                valid = self.vies_vat_check(vat_country, vat_number)
                if valid:
                    self.write({'vat': part.name.upper().replace(" ", "")})
            except:
                raise Warning(_("No VAT number found"))

        vat_country, vat_number = self._split_vat(part.vat)

        if part.vat_subjected:
            self.write({'vat_subjected': False})
        if vat_number and vat_country:
            self.write({
                'is_company': True,
                'country_id': self.env['res.country'].search([('code', 'ilike', vat_country)])[0].id
            })
            if vat_country == 'ro':
                values = {}
                try:
                    result = self._get_Anaf(vat_number)
                    if result:
                        values = self._Anaf_to_Odoo(result)
                except Exception as e:
                    _logger.error("Error anaf %s " % str(e))
                    values = self._get_Openapi(vat_number)

                if values:
                    self.write(values)

            else:
                try:
                    result = check_vies(part.vat)
                    if result.name and result.name != '---':
                        self.write({
                            'name': result.name.upper(),  # unicode(result.name).upper(),
                            'is_company': True,
                            'vat_subjected': True
                        })
                    if (not part.street and result.address and result.address != '---'):
                        self.write({'street': result.address.title()})  # unicode(result.address).title()})
                    self.write({'vat_subjected': result.valid})
                except:
                    self.write({
                        'vat_subjected': self.vies_vat_check(vat_country, vat_number)
                    })
