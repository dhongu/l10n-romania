# Copyright  2015 Forest and Biomass Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import json
import unicodedata
from urllib.request import Request, urlopen

from stdnum.eu.vat import check_vies

from odoo import _, api, fields, models
from odoo.exceptions import Warning

headers = {"User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)", "Content-Type": "application/json;"}


def unaccent(text):
    text = text.replace("\u015f", "\u0219")
    text = text.replace("\u0163", "\u021b")
    text = text.replace("\u015e", "\u0218")
    text = text.replace("\u0162", "\u021a")
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

    @api.model
    def create(self, vals):
        partner = super().create(vals)
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
                        "Partner vat must be unique per company except on partner with parent/child relationship. "
                        + "Partners with same vat and not related, are: %s!"
                    )
                    % (", ".join(x.name for x in same_vat_partners))
                )

    def _split_vat(self, vat):
        vat_country, vat_number = super()._split_vat(vat)
        if vat_country.isdigit():
            vat_country = "ro"
            vat_number = vat
        return vat_country, vat_number

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
