# -*- coding: utf-8 -*-
# Copyright  2015 Forest and Biomass Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import requests
from odoo import models, api, fields, _
from odoo.exceptions import Warning



try:
    # For Python 3.0 and later
    from urllib.request import Request,urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import Request, urlopen

import json

from stdnum.eu.vat import check_vies
from lxml import html
import unicodedata

#from string import maketrans

#CEDILLATRANS = maketrans(u'\u015f\u0163\u015e\u0162'.encode('utf8'), u'\u0219\u021b\u0218\u021a'.encode('utf8'))



headers = {
    "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)",
    "Content-Type": "application/json;"
}


def unaccent( text):
    text = text.replace(u'\u015f',u'\u0219')   # ş cu ș
    text = text.replace(u'\u0163', u'\u021b')  # ţ cu ț
    text = text.replace(u'\u015e', u'\u0218')  # Ş cu Ș
    text = text.replace(u'\u0162', u'\u021a')  # Ţ cu Ț
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)


class ResPartner(models.Model):
    _inherit = "res.partner"

    vat_subjected = fields.Boolean()

    @api.model
    def _get_Mfinante(self, cod):
        headers = {
            "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)",
            "Content-Type": "multipart/form-data;"
        }
        params = {'cod': cod}
        res = requests.get(
            'http://www.mfinante.ro/infocodfiscal.html',
            params=params,
            headers=headers
        )
        res.raise_for_status()

        htm = html.fromstring(res.text)
        # sunt 2 tabele primul e important
        table = htm.xpath("//div[@id='main']//center/table")[0]
        result = dict()
        for tr in table.iterchildren():
            key = ' '.join([x.strip() for x in tr.getchildren()[ 0].text_content().split('\n') if x.strip() != ''])
            val = ' '.join([x.strip() for x in tr.getchildren()[ 1].text_content().split('\n') if x.strip() != ''])
            result[key] = unaccent(val)
            #result[key] = val.encode('utf8') .translate(CEDILLATRANS).decode('utf8')
        return result

    @api.model
    def _Mfinante_to_Odoo(self, result):
        nrc_key = 'Numar de inmatriculare la Registrul Comertului:'
        tva_key = 'Taxa pe valoarea adaugata (data luarii in evidenta):'
        name = nrc = adresa = tel = fax = False
        zip1 = vat_s = state = False
        if 'Denumire platitor:' in result.keys():
            name = result['Denumire platitor:'].upper()
        if 'Adresa:' in result.keys():
            adresa = result['Adresa:'].title() or ''
        if nrc_key in result.keys():
            nrc = result[nrc_key].replace(' ', '')
            if nrc == '-/-/-':
                nrc = ''
        if 'Codul postal:' in result.keys():
            zip1 = result['Codul postal:'] or ''
        if 'Judetul:' in result.keys():
            jud = result['Judetul:'].title() or ''
            if jud.lower().startswith('municip'):
                jud = ' '.join(jud.split(' ')[1:])
            if jud != '':
                state = self.env['res.country.state'].search([('name', 'ilike', jud)])
                if state:
                    state = state[0].id
        if 'Telefon:' in result.keys():
            tel = result['Telefon:'].replace('.', '') or ''
        if 'Fax:' in result.keys():
            fax = result['Fax:'].replace('.', '') or ''
        if tva_key in result.keys():
            vat_s = bool(result[tva_key] != 'NU')

        values = {
            'name': name or '',
            'nrc': nrc or '',
            'street': adresa or '',
            'phone': tel or '',
            'fax': fax or '',
            'zip': zip1 or '',
            'vat_subjected': vat_s or False,
            'state_id': state,
        }

        return values

    @api.model
    def _get_Anaf(self, cod):
        addr = 'https://webservicesp.anaf.ro:/PlatitorTvaRest/api/v1/ws/tva'
        res = requests.post(
            addr,
            json=[{'cui': cod, 'data': fields.Date.today()}],
            headers=headers)
        if res.status_code == 200:
            res = res.json()
        if res['found'] and res['found'][0]:
            result = res['found'][0]
            if result['data_sfarsit'] and result['data_sfarsit'] != ' ':
                res = requests.post(
                    addr,
                    json=[{'cui': cod, 'data': result['data_sfarsit']}],
                    headers=headers)
                if res.status_code == 200:
                    res = res.json()
        if res['found'] and res['found'][0]:
            result = res['found'][0]
        # Check if the partner was deactived
        if res['notfound'] and res['notfound'][0]:
            result = res['notfound'][0]
            if result['data_sfarsit'] and result['data_sfarsit'] != ' ':
                res = requests.post(
                    addr,
                    json=[{'cui': cod, 'data': result['data_sfarsit']}],
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
        res = {'name': result['denumire'].upper(),
               'vat_subjected': result['tva'],
               'company_type': 'company'}
        addr = ''
        addr2 = ''
        if result['adresa']:
            result['adresa'] = result['adresa'].replace('MUNICIPIUL','MUN.')
            lines = [x for x in result['adresa'].split(",") if x]
            nostreet = True
            listabr = ['JUD.', 'MUN.', 'ORS.', 'COM.', 'STR.']
            for line in lines:
                if 'STR.' in line:
                    nostreet = False
                    break
            if nostreet:
                addr = 'Principala'

            for line in lines:
                line = unaccent(line) #line.encode('utf8').translate(CEDILLATRANS).decode('utf8')
                if 'JUD.' in line:
                    state = self.env['res.country.state'].search(
                        [('name', '=', line.replace('JUD.', '').strip().title())], limit=1)
                    if state:
                        res['state_id'] = state.id
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

            if city:
                res['city'] = city.replace('-', ' ').title()

            for line in lines:
                if not any([x in line for x in listabr]):
                    addr2 += ' ' + line.strip().title()

        res['street'] = addr.strip()
        res['street2'] = addr2.strip()
        return res

    @api.model
    def _get_Openapi(self, cod):

        result = {}
        openapi_key = self.env['ir.config_parameter'].get_param(key="openapi_key", default=False)
        if openapi_key:
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
        else:
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
                raise Warning(
                    _('Partner vat must be unique per company except on partner with parent/childe relationship. ' +
                      'Partners with same vat and not related, are: %s!') % (
                        ', '.join(x.name for x in same_vat_partners)))

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
                    '''
                    result = self._get_Mfinante(vat_number)
                    if result:
                        values = self._Mfinante_to_Odoo(result)
                        self.write(values)
                    '''
                    result = self._get_Anaf(vat_number)
                    if result:
                        values = self._Anaf_to_Odoo(result)
                except Exception as e:
                    print ( str(e) )
                    values = self._get_Openapi(vat_number)

                if values:
                    self.write(values)

            else:
                try:
                    result = check_vies(part.vat)
                    if result.name and result.name != '---':
                        self.write({
                            'name': result.name.upper(), #unicode(result.name).upper(),
                            'is_company': True,
                            'vat_subjected': True
                        })
                    if (not part.street and result.address and result.address != '---'):
                        self.write({'street': result.address.title()})      # unicode(result.address).title()})
                    self.write({'vat_subjected': result.valid})
                except:
                    self.write({
                        'vat_subjected': self.vies_vat_check(vat_country, vat_number)
                    })