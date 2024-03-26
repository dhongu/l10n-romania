# Copyright 2024 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import json
import logging
from datetime import datetime
from urllib.request import Request, urlopen

from stdnum.eu.vat import check_vies

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

headers = {"User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)", "Content-Type": "application/json;"}


class ResPartner(models.Model):
    _inherit = "res.partner"

    # @api.model
    # def create(self, vals):
    #     partner = super().create(vals)
    #     if "name" in vals:
    #         name = vals["name"].lower().strip()
    #         if "ro" in name:
    #             name = name.replace("ro", "")
    #     return partner

    @api.model
    def _get_Openapi(self, cod):
        result = {}
        openapi_key = self.env["ir.config_parameter"].sudo().get_param(key="openapi_key", default="False")

        if not openapi_key:
            UserError(_("Setati openapi_key in parametrii de sistem"))
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
                "zip": res["cod_postal"] and res["cod_postal"] or "",
                "l10n_ro_vat_subjected": bool(res["tva"]),
                "state_id": state,
                "radiata": res["radiata"],
                "company_type": "company",
            }

        return result

    def button_get_partner_data_openapi(self):
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
            except BaseException as e:
                raise UserError(_("No VAT number found")) from e

        vat_country, vat_number = self._split_vat(part.vat)

        if part.l10n_ro_vat_subjected:
            self.write({"l10n_ro_vat_subjected": False})
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
                    _logger.warning("OpenAPI interrogation failed:%s", str(e))
                    values = {}

                if values:
                    if not values["l10n_ro_vat_subjected"]:
                        values["vat"] = self.vat.replace("RO", "")
                    radiata = values["radiata"]
                    values.pop("radiata")
                    self.write(values)
                    if radiata:
                        self.active = False

            else:
                try:
                    result = check_vies(part.vat)
                    if result.name and result.name != "---":
                        self.write(
                            {
                                "name": result.name,
                                "is_company": True,
                                "l10n_ro_vat_subjected": True,
                            }
                        )
                    if not part.street and result.address and result.address != "---":
                        self.write({"street": result.address.title()})
                    self.write({"l10n_ro_vat_subjected": result.valid})
                except BaseException as e:
                    self.write({"l10n_ro_vat_subjected": self.vies_vat_check(vat_country, vat_number)})
                    raise UserError(_("No suitable information found for this partner")) from e

    @api.onchange("vat", "country_id")
    def ro_vat_change(self):
        skip_ro_vat_change = self.env.context.get("skip_ro_vat_change", True)
        self = self.with_context(skip_ro_vat_change=skip_ro_vat_change)
        return super(ResPartner, self.with_context(skip_ro_vat_change=skip_ro_vat_change)).ro_vat_change()
