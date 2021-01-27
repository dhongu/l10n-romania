# Copyright  2015 Forest and Biomass Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import json
import unicodedata
from urllib.request import Request, urlopen

import requests
from lxml import html
from stdnum.eu.vat import check_vies

from odoo import _, api, fields, models
from odoo.exceptions import Warning

# from string import maketrans

# CEDILLATRANS = maketrans(u'\u015f\u0163\u015e\u0162'.encode('utf8'), u'\u0219\u021b\u0218\u021a'.encode('utf8'))


headers = {"User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)", "Content-Type": "application/json;"}

ANAF_URL = "https://webservicesp.anaf.ro/PlatitorTvaRest/api/v4/ws/tva"


def unaccent(text):
    text = text.replace(u"\u015f", u"\u0219")
    text = text.replace(u"\u0163", u"\u021b")
    text = text.replace(u"\u015e", u"\u0218")
    text = text.replace(u"\u0162", u"\u021a")
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore")
    text = text.decode("utf-8")
    return str(text)


class ResPartner(models.Model):
    _inherit = "res.partner"

    nrc = fields.Char(string="NRC", help="Registration number at the Registry of Commerce")
    vat_subjected = fields.Boolean(
        "VAT Legal Statement"
    )  # campul asta cred ca trebuie sa fie in modulul de baza de localizare
    split_vat = fields.Boolean("Split VAT")
    vat_on_payment = fields.Boolean("VAT on Payment")

    @api.constrains("vat", "country_id")
    def check_vat(self):
        partners = self
        for partner in partners:
            if not partner.vat_subjected or not partner.is_company:
                partners -= partner
        return super(ResPartner, partners).check_vat()

    @api.onchange("vat")
    def onchange_vat(self):
        if self.country_id.code == "RO" and self.vat:
            self.vat_subjected = self.vat[:2].lower() == "ro"

    @api.onchange("vat_subjected")
    def onchange_vat_subjected(self):
        if self.country_id.code == "RO" and self.vat:
            if self.vat_subjected:
                if self.vat[:2].lower() != "ro":
                    self.vat = "RO" + self.vat
            else:
                if self.vat[:2].lower() == "ro":
                    self.vat = self.vat[2:]

    @api.onchange("vat_on_payment")
    def onchange_vat_on_payment(self):
        if self.vat_on_payment:
            self.property_account_position_id = self.company_id.property_vat_on_payment_position_id
        elif self.property_account_position_id == self.company_id.property_vat_on_payment_position_id:
            self.property_account_position_id = False

    # todo: de facut conversie la multi
    @api.model
    def create(self, vals):
        partner = super(ResPartner, self).create(vals)
        if "name" in vals:
            name = vals["name"].lower().strip()
            if "ro" in name:
                name = name.replace("ro", "")
            if name.isdigit():
                try:
                    partner.button_get_partner_data()
                except:
                    pass

        return partner

    @api.model
    def _get_Anaf(self, cod):
        res = requests.post(
            ANAF_URL, json=[{"cui": cod, "data": fields.Date.today().strftime("%Y-%m-%d")}], headers=headers
        )
        if res.status_code == 200:
            res = res.json()
        if res["found"] and res["found"][0]:
            result = res["found"][0]
            if result["data_sfarsit_ScpTVA"] and result["data_sfarsit_ScpTVA"] != " ":
                res = requests.post(
                    ANAF_URL, json=[{"cui": cod, "data": result["data_sfarsit_ScpTVA"]}], headers=headers
                )
                if res.status_code == 200:
                    res = res.json()
        if res["found"] and res["found"][0]:
            result = res["found"][0]
        # Check if the partner was deactived
        if res["notfound"] and res["notfound"][0]:
            result = res["notfound"][0]
            if result["data_sfarsit_ScpTVA"] and result["data_sfarsit_ScpTVA"] != " ":
                res = requests.post(
                    ANAF_URL, json=[{"cui": cod, "data": result["data_sfarsit_ScpTVA"]}], headers=headers
                )
                if res.status_code == 200:
                    res = res.json()
                    if res["found"] and res["found"][0]:
                        result = res["found"][0]
                    if res["notfound"] and res["notfound"][0]:
                        result = res["notfound"][0]
        return result

    @api.model
    def _Anaf_to_Odoo(self, result):
        res = {
            "name": result["denumire"],
            "vat_subjected": result["scpTVA"],
            "split_vat": result["statusSplitTVA"],
            "vat_on_payment": result["statusTvaIncasare"],
            "company_type": "company",
        }

        if result["statusTvaIncasare"]:
            res["property_account_position_id"] = self.company_id.property_vat_on_payment_position_id.id

        addr = ""
        city = ""
        if result["adresa"]:
            result["adresa"] = result["adresa"].replace("MUNICIPIUL", "MUN.")
            result["adresa"] = result["adresa"].replace(u"ORȘ.", "ORS.")
            result["adresa"] = result["adresa"].replace(u"ORŞ.", "ORS.")
            lines = [x for x in result["adresa"].split(",") if x]
            nostreet = True
            # listabr = ['JUD.', 'MUN.', 'ORS.', 'COM.',
            #            'STR.', 'NR.', 'ET.', 'AP.']
            for line in lines:
                if "STR." in line or "CAL." in line or "BLD." in line or "B-DUL" in line:
                    nostreet = False
                    addr = line
                    break
            if nostreet:
                addr = ""
            # for line in lines:
            #     if not any([x in line for x in listabr]):
            #         addr = line.strip().title()
            for line in lines:
                # line = unaccent(line)  # line.encode('utf8').translate(CEDILLATRANS).decode('utf8')
                if "JUD." in line:
                    name = line.replace("JUD.", "").strip().title()
                    state = self.env["res.country.state"].search([("name", "=", name)])
                    if state:
                        res["state_id"] = state[0].id
                if "MUN." in line:
                    city = line.replace("MUN.", " ").strip().title()
                elif "ORS." in line:
                    city = line.replace("ORS.", " ").strip().title()
                elif "COM." in line:
                    sat = line.replace("SAT ", " ").strip().title().split(" ")
                    city = ""
                    for satname in sat:
                        if "." not in satname:
                            city += " " + satname
                        else:
                            break
                    city = city.strip()
                # if 'STR.' in line:
                #     addr += line.replace('STR.', '').strip().title()
                if "NR." in line:
                    addr += " " + line.strip().title()
                if "BL." in line:
                    addr += " " + line.strip().title()
                if "AP." in line:
                    addr += " " + line.strip().title()
            if city:
                res["city"] = city.replace("-", " ").title()
        res["street"] = addr.strip()
        # res['street2'] = result['adresa']
        if "adresa" in result:
            self.message_post(body=result["adresa"])
        return res

    @api.model
    def _get_Openapi(self, cod):

        result = {}
        openapi_key = self.env["ir.config_parameter"].sudo().get_param(key="openapi_key", default=False)

        if not openapi_key:
            print("Setati openapi_key in parametrii de sistem")
        headers = {
            "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)",
            "Content-Type": "application/json;",
            "x-api-key": openapi_key,
        }

        request = Request("https://api.openapi.ro/api/companies/%s" % cod, headers=headers)
        response = urlopen(request)
        status_code = response.getcode()

        if status_code == 200:

            res = json.loads(response.read())
            state = False
            if res["judet"]:
                state = self.env["res.country.state"].search([("name", "=", res["judet"].title())])
                if state:
                    state = state[0].id

            result = {
                "name": res["denumire"],
                "nrc": res["numar_reg_com"] or "",
                "street": res["adresa"],
                "phone": res["telefon"] and res["telefon"] or "",
                "fax": res["fax"] and res["fax"] or "",
                "zip": res["cod_postal"] and res["cod_postal"] or "",
                "vat_subjected": bool(res["tva"]),
                "state_id": state,
                "company_type": "company",
            }

        return result

    # @api.one
    # @api.constrains('vat')
    # def check_vat(self):
    #     if not self.vat_subjected or not self.is_company:
    #         return True
    #     return super(ResPartner, self).check_vat()
    #
    # def check_vat_ro(self, vat):
    #     self.check_vat_unique()
    #     # date_anaf = self._get_Anaf(vat)
    #     # if not date_anaf:
    #     #     return  False
    #     return True

    @api.constrains("is_company", "vat", "parent_id", "company_id")
    def check_vat_unique(self):
        if self.env.context.get("tracking_disable", False):
            return True

        for partner in self:
            if not partner.vat or not partner.is_company or partner.parent_id:
                continue

            same_vat_partners = self.search(
                [
                    ("is_company", "=", True),
                    ("parent_id", "=", False),
                    ("vat", "=", partner.vat),
                    ("company_id", "=", partner.company_id.id),
                    ("id", "!=", partner.id),
                ]
            )

            if same_vat_partners:
                raise Warning(
                    _(
                        "Partner vat must be unique per company except on partner with parent/childe relationship. "
                        + "Partners with same vat and not related, are: %s!"
                    )
                    % (", ".join(x.name for x in same_vat_partners))
                )

    def _split_vat(self, vat):
        vat_country, vat_number = super(ResPartner, self)._split_vat(vat)
        if vat_country.isdigit():
            vat_country = "ro"
            vat_number = vat
        return vat_country, vat_number

    @api.multi
    def button_get_partner_data(self):
        def _check_vat_ro(vat):
            return bool(
                len(part.name.strip()) > 2 and part.name.strip().upper()[:2] == "RO" and part.name.strip()[2:].isdigit()
            )

        part = self[0]

        vat = part.vat
        if vat:
            self.write({"vat": part.vat.upper().replace(" ", "")})
        elif (
            part.name
            and len(part.name.strip()) > 2
            and part.name.strip().upper()[:2] == "RO"
            and part.name.strip()[2:].isdigit()
        ):
            self.write({"vat": part.name.upper().replace(" ", "")})
        elif part.name.strip().isdigit():
            self.write({"vat": "RO" + part.name.upper().replace(" ", "")})

        if not part.vat and part.name:
            try:
                vat_country, vat_number = self._split_vat(part.name.upper().replace(" ", ""))
                valid = self.vies_vat_check(vat_country, vat_number)
                if valid:
                    self.write({"vat": part.name.upper().replace(" ", "")})
            except:
                raise Warning(_("No VAT number found"))

        vat_country, vat_number = self._split_vat(part.vat)

        if part.vat_subjected:
            self.write({"vat_subjected": False})
        if vat_number and vat_country:
            self.write(
                {
                    "is_company": True,
                    "country_id": self.env["res.country"].search([("code", "ilike", vat_country)])[0].id,
                }
            )
            if vat_country == "ro":
                try:
                    values = self._get_Openapi(vat_number)
                except Exception as e:
                    print(str(e))
                    values = {}

                result = self._get_Anaf(vat_number)
                if result:
                    values.update(self._Anaf_to_Odoo(result))

                if values:
                    if not values["vat_subjected"]:
                        values["vat"] = self.vat.replace("RO", "")
                    self.write(values)

            else:
                try:
                    result = check_vies(part.vat)
                    if result.name and result.name != "---":
                        self.write(
                            {
                                "name": result.name,  # .upper(),  # unicode(result.name).upper(),
                                "is_company": True,
                                "vat_subjected": True,
                            }
                        )
                    if not part.street and result.address and result.address != "---":
                        self.write({"street": result.address.title()})  # unicode(result.address).title()})
                    self.write({"vat_subjected": result.valid})
                except:
                    self.write({"vat_subjected": self.vies_vat_check(vat_country, vat_number)})
