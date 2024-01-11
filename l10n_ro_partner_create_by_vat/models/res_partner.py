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

CEDILLATRANS = bytes.maketrans(
    "\u015f\u0163\u015e\u0162\u00e2\u00c2\u00ee\u00ce\u0103\u0102".encode("utf8"),
    "\u0219\u021b\u0218\u021a\u00e2\u00c2\u00ee\u00ce\u0103\u0102".encode("utf8"))

AnafFiled_OdooField_Overwrite = [
    ("vat", "vat", "over_all_the_time"),
    ("nrc", "nrRegCom", "over_all_the_time"),
    ("street", "street", "over_all_the_time"),
    ("street2", "street2", "over_all_the_time"),
    ("city", "city", "over_all_the_time"),
    ("city_id", "city_id", "over_all_the_time"),
    ("state_id", "state_id", "over_all_the_time"),
    ("zip", "codPostal", "over_all_the_time"),
    ("phone", "telefon", "write_if_empty")
]

headers = {
    "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)",
    "Content-Type": "application/json;"
}

ANAF_URL = "https://webservicesp.anaf.ro/PlatitorTvaRest/api/v8/ws/tva"


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
    def _get_Anaf(self, cod, data=False):
        """
                Function to retrieve data from ANAF for one vat number
                at certain date

                :param str cod:  vat number without country code or a list of codes
                :param date data: date of the interogation
                :return dict result: cost of the body's operation
                {
                "cui": "-- codul fiscal --",
                "data": "-- data pentru care se efectueaza cautarea --",
                "denumire": "-- denumire --",
                "adresa": "-- adresa --",
                "nrRegCom": "-- numar de inmatriculare la Registrul Comertului --",
                "telefon": "-- Telefon --",
                "fax": "-- Fax --",
                "codPostal": "-- Codul Postal --",
                "act": "-- Act autorizare --",
                "stare_inregistrare": "-- Stare Societate --",
                "scpTVA": " -- true -pentru platitor in scopuri de tva / false in cazul in
                               care nu e platitor  in scopuri de TVA la data cautata  --",
                "data_inceput_ScpTVA": " -- Data înregistrării în scopuri de TVA anterioară --",
                "data_sfarsit_ScpTVA": " -- Data anulării înregistrării în scopuri de TVA --",
                "data_anul_imp_ScpTVA": "-- Data operarii anularii înregistrării în scopuri de TVA --",
                "mesaj_ScpTVA": "-- MESAJ:(ne)platitor de TVA la data cautata --",
                "dataInceputTvaInc": " -- Data de la care aplică sistemul TVA la încasare -- ",
                "dataSfarsitTvaInc": " -- Data până la care aplică sistemul TVA la încasare --",
                "dataActualizareTvaInc": "-- Data actualizarii --",
                "dataPublicareTvaInc": "-- Data publicarii --""
                "tipActTvaInc": " --Tip actualizare --",
                "statusTvaIncasare": " -- true -pentru platitor TVA la incasare/ false in
                                       cazul in care nu e platitor de TVA la incasare la
                                       data cautata --",
                "dataInactivare": " --     -- ",
                "dataReactivare": " --     -- ",
                "dataPublicare": " --     -- ",
                "dataRadiere": " -- Data radiere -- ",
                "statusInactivi": " -- true -pentru inactiv / false in cazul in care nu este
                                       inactiv la data cautata -- ",
                "dataInceputSplitTVA": "--     --",
                "dataAnulareSplitTVA": "--     --",
                "statusSplitTVA": "-- true -aplica plata defalcata a Tva / false - nu aplica
                                     plata defalcata a Tva la data cautata  --",
                "iban": "-- contul IBAN --",
                "statusRO_e_Factura": "-- true - figureaza in Registrul RO e-Factura / false
                                     - nu figureaza in Registrul RO e-Factura la data cautata  --",
                "sdenumire_Strada": "-- Denumire strada sediu --",
                "snumar_Strada": "-- Numar strada sediu --",
                "sdenumire_Localitate": "-- Denumire localitate sediu --",
                "scod_Localitate": "-- Cod localitate sediu --",
                "sdenumire_Judet": "-- Denumire judet sediu --",
                "scod_Judet": "-- Cod judet sediu --",
                "stara": "-- Denumire tara sediu -- ",
                "sdetalii_Adresa": "-- Detalii adresa sediu --",
                "scod_Postal": "-- Cod postal sediu --",
                "ddenumire_Strada":  -- Denumire strada domiciliu fiscal --",
                "dnumar_Strada": "-- Numar strada domiciliu fiscal --",
                "ddenumire_Localitate": "-- Denumire localitate domiciliu fiscal --",
                "dcod_Localitate": "-- Cod localitate domiciliu fiscal --",
                "ddenumire_Judet": "-- Denumire judet domiciliu fiscal --",
                "dcod_Judet": "-- Cod judet domiciliu fiscal --",
                "dtara": "-- Denumire tara domiciliu fiscal --",
                "ddetalii_Adresa": "-- Detalii adresa domiciliu fiscal --",
                "dcod_Postal": "-- Cod postal domiciliu fiscal --",
                "data_inregistrare": "-- Data inregistrare -- ",
                "cod_CAEN": "-- Cod CAEN --",
                                  }
                """

        anaf_error = ""
        if "anaf_data" in self.env.context and isinstance(cod, str):
            test_data = self.env.context.get("anaf_data")
            result = test_data.get(cod, {})
            anaf_error = result.get("error", "")
            if result:
                return anaf_error, test_data[cod]

        get_param = self.env["ir.config_parameter"].sudo().get_param
        anaf_url = get_param("l10n_ro_partner_create_by_vat.anaf_url", ANAF_URL)
        if not data:
            data = fields.Date.today()
        if type(cod) in [list, tuple]:
            json_data = [{"cui": x, "data": data} for x in cod]
        else:
            json_data = [{"cui": cod, "data": data}]
        try:
            res = requests.post(anaf_url, json=json_data, headers=headers, timeout=30)
        except Exception as ex:
            return _("ANAF Webservice not working. Exception=%s.") % ex, {}

        result = {}

        if (
                res.status_code == 200
                and res.headers.get("content-type") == "application/json"
        ):
            resjson = res.json()
            if type(cod) in [list, tuple]:
                result = resjson
            else:
                if resjson.get("found") and resjson["found"][0]:
                    result = resjson["found"][0]
                if not result or not result.get("date_generale"):
                    anaf_error = _("Anaf didn't find any company with VAT=%s !") % cod
        else:
            anaf_error = _(
                "Anaf request error: \nresponse=%(response)s "
                "\nreason=%(reason)s \ntext=%(text)s",
                response=res,
                reason=res.reason,
                text=res.text,
            )
        return anaf_error, result

    @api.model
    def _Anaf_to_Odoo(self, result):
        # From ANAf API v7 the structure changed with the following fields:
        odoo_result = result.get("date_generale", {})
        odoo_result.update(result.get("inregistrare_scop_Tva", {}))
        odoo_result.update(result.get("inregistrare_RTVAI", {}))
        odoo_result.update(result.get("stare_inactiv", {}))
        odoo_result.update(result.get("inregistrare_SplitTVA", {}))
        odoo_result.update(result.get("adresa_sediu_social", {}))
        odoo_result.update(result.get("adresa_domiciliu_fiscal", {}))
        if not odoo_result.get("denumire"):
            return {}
        res = {
            "name": odoo_result["denumire"].upper(),
            "vat_subjected": odoo_result.get("scpTVA"),
            "company_type": "company"}

        odoo_result = self.get_result_address(odoo_result)
        odoo_result["vat"] = "%s%s" % (
            odoo_result.get("scpTVA", False) and "RO" or "",
            odoo_result.get("cui"),
        )
        if "city_id" in self._fields and odoo_result["state_id"] and odoo_result["city"]:
            domain = [
                ("state_id", "=", odoo_result["state_id"].id),
                ("name", "=ilike", odoo_result["city"])]
            odoo_result["city_id"] = self.env["res.city"].search(domain, limit=1).id

        if odoo_result["state_id"] == self.env.ref("l10n_ro.RO_B").id:
            if odoo_result.get("codPostal") and odoo_result["codPostal"][0] != "0":
                odoo_result["codPostal"] = "0" + odoo_result["codPostal"]

        for field in AnafFiled_OdooField_Overwrite:
            if field[1] not in odoo_result:
                continue
            anaf_value = odoo_result.get(field[1], "")
            if type(self._fields[field[0]]) in [fields.Date, fields.Datetime]:
                if not anaf_value.strip():
                    anaf_value = False
            if field[2] == "over_all_the_time":
                res[field[0]] = anaf_value
            elif field[2] == "write_if_empty&add_date" and anaf_value:
                if not getattr(self, field[0], None):  # we are only writing if is not already a value
                    res[field[0]] = ("UTC %s:" % fields.datetime.now()) + anaf_value
            elif field[2] == "write_if_empty" and anaf_value:
                if not getattr(self, field[0], None):
                    res[field[0]] = anaf_value
        return res

    def get_result_address(self, result):
        # Take address from domiciliu fiscal
        def get_city(text):
            city = text.replace(".", "").upper()
            remove_str = ["MUNICIPIUL", "MUN", "ORȘ", "JUD"]
            if "SECTOR" in city and "MUN" in city:
                city = city.split("MUN")[0]
            for tag in remove_str:
                city = city.replace(tag, "")
            return city.strip().title()

        if result.get("adresa"):
            for tag in [
                "ddenumire_Strada",
                "dnumar_Strada",
                "ddetalii_Adresa",
                "ddenumire_Localitate",
                "ddenumire_Judet",
            ]:
                result[tag] = (
                    result[tag]
                    .encode("utf8")
                    .translate(CEDILLATRANS)
                    .decode("utf8")
                    .strip()
                )
            result["street"] = result.get("ddenumire_Strada")
            if result.get("dnumar_Strada"):
                result["street"] += " Nr. " + result.get("dnumar_Strada")
            result["street"] = result["street"].strip().title()
            result["street2"] = result.get("ddetalii_Adresa", " ").strip().title()
            result["city"] = get_city(result.get("ddenumire_Localitate"))
            state_code = result.get('dcod_JudetAuto')
            if state_code:
                state = self.env["res.country.state"].search([
                    ('code', '=', state_code),
                    ('country_id', '=', self.env.ref('base.ro').id)])
                result["state_id"] = state[0].id if state else None
        return result

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
            vat_country = 'ro'
            vat_number = vat
        else:
            vat_country, vat_number = vat[:2].lower(), vat[2:]
        return vat_country, vat_number

    @api.multi
    def button_get_partner_data(self):
        for partner in self:
            vat = partner.vat
            if vat:
                self.write({'vat': partner.vat.upper().replace(' ', '')})
            elif partner.name and len(partner.name.strip()) > 2 and \
                    partner.name.strip().upper()[:2] == 'RO' and \
                    partner.name.strip()[2:].isdigit():
                self.write({'vat': partner.name.upper().replace(' ', '')})
            elif partner.name.strip().isdigit():
                self.write({'vat': 'RO' + partner.name.upper().replace(' ', '')})

            if not partner.vat and partner.name:
                try:
                    vat_country, vat_number = self._vat_split(partner.name.upper().replace(" ", ""))
                    valid = self.vies_vat_check(vat_country, vat_number)
                    if valid:
                        self.write({'vat': partner.name.upper().replace(' ', '')})
                except:
                    raise Warning(_('No VAT number found'))

            vat_country, vat_number = self._vat_split(partner.vat)

            if partner.vat_subjected:
                self.write({'vat_subjected': False})
            if vat_number and vat_country:
                self.write({
                    'is_company': True,
                    'country_id': self.env['res.country'].search([('code', 'ilike', vat_country)])[0].id})
                if vat_country == 'ro':
                    try:
                        values = self._get_Openapi(vat_number)
                    except:
                        values = {}

                    anaf_error, result = self._get_Anaf(vat_number)
                    if result:
                        values.update(self._Anaf_to_Odoo(result))

                    if values:
                        if not values['vat_subjected']:
                            values['vat'] = self.vat.replace('RO', '')
                        self.write(values)

                else:
                    try:
                        result = check_vies(partner.vat)
                        if result.name and result.name != '---':
                            self.write({
                                'name': result.name.upper(),  # unicode(result.name).upper(),
                                'is_company': True,
                                'vat_subjected': True
                            })
                        if (not partner.street and result.address and result.address != '---'):
                            self.write({'street': result.address.title()})  # unicode(result.address).title()})
                        self.write({'vat_subjected': result.valid})
                    except:
                        self.write({'vat_subjected': self.vies_vat_check(vat_country, vat_number)})
