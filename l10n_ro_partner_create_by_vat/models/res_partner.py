# -*- coding: utf-8 -*-
# Copyright  2015 Forest and Biomass Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import requests
from odoo import models, api, fields, _
from odoo.exceptions import Warning

try:
    # For Python 3.0 and later
    from urllib.request import Request, urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import Request, urlopen

import json

from stdnum.eu.vat import check_vies
from lxml import html
import unicodedata

# from string import maketrans

# CEDILLATRANS = maketrans(u'\u015f\u0163\u015e\u0162'.encode('utf8'), u'\u0219\u021b\u0218\u021a'.encode('utf8'))


headers = {
    "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)",
    "Content-Type": "application/json;"
}

ANAF_URL = 'https://webservicesp.anaf.ro/PlatitorTvaRest/api/v5/ws/tva'


def unaccent(text):
    text = text.replace(u'\u015f', u'\u0219')
    text = text.replace(u'\u0163', u'\u021b')
    text = text.replace(u'\u015e', u'\u0218')
    text = text.replace(u'\u0162', u'\u021a')
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)


class ResPartner(models.Model):
    _inherit = "res.partner"

    nrc = fields.Char(string='NRC', help='Registration number at the Registry of Commerce')
    vat_subjected = fields.Boolean('VAT Legal Statement')  # campul asta cred ca trebuie sa fie in modulul de baza de localizare
    split_vat = fields.Boolean('Split VAT')
    vat_on_payment = fields.Boolean('VAT on Payment')

    @api.model
    def create(self, vals):

        partner = super(ResPartner, self).create(vals)
        if 'name' in vals:
            name = vals['name'].lower().strip()
            if 'ro' in name:
                name = name.replace('ro', '')
            if name.isdigit():
                try:
                    partner.button_get_partner_data()
                except:
                    pass

        return partner


    @api.model
    def _get_Anaf(self, cod):
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
               'vat_on_payment': result['statusTvaIncasare'],
               'company_type': 'company'}
        addr = ''
        city = ''
        if result['adresa']:
            result['adresa'] = result['adresa'].replace('MUNICIPIUL', 'MUN.')
            result['adresa'] = result['adresa'].replace(u'ORȘ.', 'ORS.')
            result['adresa'] = result['adresa'].replace(u'ORŞ.', 'ORS.')
            lines = [x for x in result['adresa'].split(",") if x]
            nostreet = True
            # listabr = ['JUD.', 'MUN.', 'ORS.', 'COM.',
            #            'STR.', 'NR.', 'ET.', 'AP.']
            for line in lines:
                if 'STR.' in line or 'CAL.' in line or 'BLD.' in line or 'B-DUL' in line:
                    nostreet = False
                    addr = line
                    break
            if nostreet:
                addr = ''
            # for line in lines:
            #     if not any([x in line for x in listabr]):
            #         addr = line.strip().title()
            for line in lines:
                # line = unaccent(line)  # line.encode('utf8').translate(CEDILLATRANS).decode('utf8')
                if 'JUD.' in line:
                    name = line.replace('JUD.', '').strip().title()
                    state = self.env['res.country.state'].search(
                        [('name', '=', name)])
                    if state:
                        res['state_id'] = state[0].id
                if 'MUN.' in line:
                    city = line.replace('MUN.', ' ').strip().title()
                elif 'ORS.' in line:
                    city = line.replace('ORS.', ' ').strip().title()
                elif 'COM.' in line:
                    sat = line.replace('SAT ', ' ').strip().title().split(" ")
                    city = ''
                    for satname in sat:
                        if '.' not in satname:
                            city += ' ' + satname
                        else:
                            break
                    city = city.strip()
                # if 'STR.' in line:
                #     addr += line.replace('STR.', '').strip().title()
                if 'NR.' in line:
                    addr += ' ' + line.strip().title()
                if 'BL.' in line:
                    addr += ' ' + line.strip().title()
                if 'AP.' in line:
                    addr += ' ' + line.strip().title()
            if city:
                res['city'] = city.replace('-', ' ').title()
        res['street'] = addr.strip()
        res['street2'] = result['adresa']
        return res

    @api.model
    def _get_Openapi(self, cod):

        result = {}
        openapi_key = self.env['ir.config_parameter'].sudo().get_param(key="openapi_key", default=False)

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
            ('is_company', '=', True),
            ('vat', '=', self.vat),
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
                raise Warning(
                    _('Partner vat must be unique per company except on partner with parent/childe relationship. ' +
                      'Partners with same vat and not related, are: %s!') % (
                        ', '.join(x.name for x in same_vat_partners)))


    def _vat_split(self, vat):
        vat = vat.replace(" ", "")
        if vat[:2].isdigit():
            vat_country ='ro'
            vat_number  = vat
        else:
            vat_country, vat_number = vat[:2].lower(), vat[2:]
        return vat_country, vat_number


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
        elif part.name and len(part.name.strip()) > 2 and \
                part.name.strip().upper()[:2] == 'RO' and \
                part.name.strip()[2:].isdigit():
            self.write({'vat': part.name.upper().replace(" ", "")})
        elif  part.name.strip().isdigit():
            self.write({'vat': 'RO'+part.name.upper().replace(" ", "")})

        if not part.vat and part.name:
            try:
                vat_country, vat_number = self._vat_split(part.name.upper().replace(" ", ""))
                valid = self.vies_vat_check(vat_country, vat_number)
                if valid:
                    self.write({'vat': part.name.upper().replace(" ", "")})
            except:
                raise Warning(_("No VAT number found"))


        vat_country, vat_number = self._vat_split(part.vat)

        if part.vat_subjected:
            self.write({'vat_subjected': False})
        if vat_number and vat_country:
            self.write({
                'is_company': True,
                'country_id': self.env['res.country'].search([('code', 'ilike', vat_country)])[0].id
            })
            if vat_country == 'ro':
                try:
                    values = self._get_Openapi(vat_number)
                except:
                    values = {}

                result = self._get_Anaf(vat_number)
                if result:
                    values.update( self._Anaf_to_Odoo(result))

                if values:
                    if not values['vat_subjected']:
                        values['vat'] = self.vat.replace('RO','')
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
