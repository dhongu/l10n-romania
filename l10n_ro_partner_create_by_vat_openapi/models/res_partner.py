# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import json
import logging
from urllib.request import Request, urlopen

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _get_Openapi(self, cod):

        result = {}
        openapi_key = self.env["ir.config_parameter"].sudo().get_param(key="openapi_key", default=False)

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
                "fax": res["fax"] and res["fax"] or "",
                "zip": res["cod_postal"] and res["cod_postal"] or "",
                "vat_subjected": bool(res["tva"]),
                "state_id": state,
                "company_type": "company",
            }

        return result

    def button_get_partner_data(self):

        vat_country, vat_number = self._split_vat(self.vat)
        if vat_number and vat_country:
            if vat_country == "ro":
                try:
                    values = self._get_Openapi(vat_number)
                except Exception as e:
                    _logger.error(str(e))
                    # UserError(str(e))
                    values = {}
                if values:
                    if not values["vat_subjected"]:
                        values["vat"] = self.vat.replace("RO", "")
                    self.write(values)

        super(ResPartner, self).button_get_partner_data()
