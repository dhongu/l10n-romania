# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


import logging
import re

from zeep import Client

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    warning_message = fields.Text(string="Warning", compute="_compute_warning_message")

    @api.depends("vat", "country_id", "street", "city", "state_id")
    def _compute_warning_message(self):
        for partner in self:
            partner.warning_message = False
            if partner.country_id and partner.country_id.code == "RO":
                missing = []
                if not partner.vat and partner.is_company:
                    missing.append(_("VAT"))
                if not partner.street:
                    missing.append(_("Street"))
                if not partner.city:
                    missing.append(_("City"))
                if not partner.state_id:
                    missing.append(_("State"))
                if not partner.zip:
                    missing.append(_("ZIP"))
                if missing:
                    partner.warning_message = _("Missing: ") + ", ".join(missing)

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
                            error, result = self._get_Anaf(vat_number)
                            if result:
                                res = self._Anaf_to_Odoo(result)
                                vals.update(res)
                        except Exception as e:
                            _logger.info(f"ANAF Webservice not working. Exception: {e}")

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
        if self.vat and not self.vat.isdigit():
            vat_number = self.vat[2:]
            country_code = self.vat[:2]
        elif self.country_id:
            vat_number = self.vat
            if self.country_id.code == "GR":
                country_code = "EL"
            else:
                country_code = self.country_id.code
        else:
            raise UserError(_("Please add the country code to the vat number or country field"))

        response = client.service.checkVat(countryCode=country_code, vatNumber=vat_number)
        if not response.valid and country_code == "GB":
            # Businesses in Northern Ireland are required to use XI as the country code but the country code is still GB
            response = client.service.checkVat(countryCode="XI", vatNumber=vat_number)
        if response.valid:
            self.vat = vat_number
            possible_country = self.env["res.country"].search([("code", "ilike", country_code)])
            if possible_country:
                self.country_id = possible_country[0].id
            else:
                if country_code == "EL":
                    self.country_id = self.env["res.country"].search([("code", "ilike", "GR")])[0].id
                if country_code == "XI":
                    self.country_id = self.env["res.country"].search([("code", "ilike", "GB")])[0].id
            self.name = response.name
            self.street = response.address
        else:
            raise UserError(_("Invalid VAT"))

    @api.onchange("vat", "country_id")
    def ro_vat_change(self):
        skip_ro_vat_change = self.env.context.get("skip_ro_vat_change", True)
        return super(ResPartner, self.with_context(skip_ro_vat_change=skip_ro_vat_change)).ro_vat_change()

    def write(self, vals):
        if "is_company" in vals or "vat" in vals:
            lock_with_invoice = self.env.company.partner_lock_with_invoice
            if lock_with_invoice:
                for partner in self:
                    # we check if there are invoices for this partner
                    invoice_count = self.env["account.move"].search_count(
                        [
                            ("partner_id", "child_of", partner.commercial_partner_id.id),
                            ("move_type", "in", ["out_invoice", "out_refund", "in_invoice", "in_refund"]),
                        ]
                    )
                    if invoice_count > 0:
                        if "is_company" in vals and vals["is_company"] != partner.is_company:
                            raise UserError(
                                _("You cannot change the type of contact if there are already invoices on it.")
                            )
                        if "vat" in vals and vals["vat"] != partner.vat:
                            new_vat = vals["vat"] or ""
                            old_vat = partner.vat or ""
                            if old_vat:
                                new_vat_digits = re.sub(r"\D", "", new_vat)
                                old_vat_digits = re.sub(r"\D", "", old_vat)
                                if new_vat_digits != old_vat_digits:
                                    raise UserError(_("You cannot change VAT if there are already invoices on it."))

        return super().write(vals)

    # @api.model_create_multi
    # def create(self, vals_list):
    #     res = super(ResPartner, self).create(vals_list)
    #
    #     for partner in res:
    #         if partner.name and not partner.vat and partner.is_company:
    #             vat_number = self.vat[2:]
    #             country_code = self.vat[:2]
    #             if vat_number.isdigit() and country_code == "RO":
    #                 try:
    #                     result = self._get_Anaf(vat_number)
    #                     if result:
    #                         res = self._Anaf_to_Odoo(result)
    #                         partner.write(res)
    #                 except Exception as e:
    #                     _logger.info(f"ANAF Webservice not working. Exception: {e}")
    #
    #     return res
