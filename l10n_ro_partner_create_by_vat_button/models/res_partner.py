# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


import logging

from zeep import Client

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    warning_companies = fields.Text(string="Warning", store=True, compute="_compute_warning_companies")

    @api.depends("vat", "country_id", "street", "city", "state_id")
    def _compute_warning_companies(self):
        for partner in self:
            partner.warning_companies = "Missing:"
            if partner.is_company and partner.country_id and partner.country_id.code == "RO":
                if not partner.vat:
                    partner.warning_companies += " VAT,"
                if not partner.street:
                    partner.warning_companies += " Street,"
                if not partner.city:
                    partner.warning_companies += " City,"
                if not partner.state_id:
                    partner.warning_companies += " State,"
                if partner.warning_companies.endswith(","):
                    partner.warning_companies = partner.warning_companies[:-1] + "!"

    @api.constrains("vat", "country_id")
    def check_vat(self):
        if self.env.context.get("no_vat_validation"):
            return
        partners = self.filtered(lambda p: p.country_id.code != "RO")
        return super(ResPartner, partners).check_vat()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "name" in vals and vals["name"]:
                vat_number = vals["name"].lower().strip()
                if "ro" in vat_number:
                    vat_number = vat_number.replace("ro", "")
                    if vat_number.isdigit():
                        try:
                            vals["vat"] = vals["name"]
                            result = self._get_Anaf(vat_number)
                            if result:
                                res = self._Anaf_to_Odoo(result)
                                vals.update(res)
                        except Exception as e:
                            _logger.info("ANAF Webservice not working. Exception: % s" % e)

            if vals.get("state_id") and not isinstance(vals["state_id"], int):
                vals["state_id"] = vals["state_id"].id

        res = super().create(vals_list)
        return res

    def get_partner_data(self):
        if self.country_id and self.country_id.code != "RO":
            return False
        if self.name and not self.vat:
            self.vat = self.name
        res = self.with_context(skip_ro_vat_change=False).ro_vat_change()

        return res
        # self.onchange_vat_subjected()  # fortare compltare ro

    def get_partner_name_from_vies(self):
        # Create a client for the VIES SOAP service
        client = Client("http://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl")

        # Make a request to the VIES service to check the VAT number
        if not self.vat.isdigit():
            vat_number = self.vat[2:]
            country_code = self.vat[:2]
        elif self.country_id:
            vat_number = self.vat
            country_code = self.country_id.code
        else:
            raise UserError(_("Please add the country code to the vat number or country field"))

        response = client.service.checkVat(countryCode=country_code, vatNumber=vat_number)
        if response.valid:
            self.vat = vat_number
            self.country_id = self.env["res.country"].search([("code", "ilike", country_code)])[0].id
            self.name = response.name
            self.street = response.address
        else:
            raise UserError(_("Invalid VAT"))

    @api.onchange("vat", "country_id")
    def ro_vat_change(self):
        skip_ro_vat_change = self.env.context.get("skip_ro_vat_change", True)
        return super(ResPartner, self.with_context(skip_ro_vat_change=skip_ro_vat_change)).ro_vat_change()
