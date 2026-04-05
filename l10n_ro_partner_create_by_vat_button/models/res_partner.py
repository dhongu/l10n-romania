# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


import logging
import re

from odoo import api, fields, models
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
                    missing.append(self.env._("VAT"))
                if not partner.street:
                    missing.append(self.env._("Street"))
                if not partner.city:
                    missing.append(self.env._("City"))
                if not partner.state_id:
                    missing.append(self.env._("State"))
                if not partner.zip:
                    missing.append(self.env._("ZIP"))
                if missing:
                    partner.warning_message = self.env._("Missing: ") + ", ".join(missing)

    @api.constrains("vat", "country_id")
    def _check_vat(self, validation="error"):
        if self.env.context.get("no_vat_validation"):
            return
        partners = self.filtered(lambda p: p.country_id.code != "RO")
        return super(ResPartner, partners)._check_vat(validation)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "name" in vals and vals["name"]:
                name = vals["name"].strip()
                # Pattern 1: Romanian CUI with RO prefix ("RO14431470", "ro 14431470")
                match = re.match(r"^[Rr][Oo]\s*(\d{2,10})$", name)
                if match:
                    vat_number = match.group(1)
                    try:
                        vals["vat"] = "RO" + vat_number
                        error, result = self._get_Anaf(vat_number)
                        if result:
                            vals.update(self._Anaf_to_Odoo(result))
                    except Exception as e:
                        _logger.warning("ANAF Webservice not working. Exception: %s", e)
                else:
                    # Pattern 2: Bare digits — assume Romanian CUI ("14431470")
                    match = re.match(r"^(\d{2,10})$", name)
                    if match:
                        vat_number = match.group(1)
                        try:
                            vals["vat"] = "RO" + vat_number
                            error, result = self._get_Anaf(vat_number)
                            if result:
                                vals.update(self._Anaf_to_Odoo(result))
                        except Exception as e:
                            _logger.warning("ANAF Webservice not working. Exception: %s", e)
                    else:
                        # Pattern 3: EU VAT with country prefix ("DE123456789", "BG 200950556")
                        match = re.match(r"^([A-Za-z]{2})\s*(\d{4,15})$", name)
                        if match:
                            country_code = match.group(1).upper()
                            vat_number = match.group(2)
                            if country_code != "RO":
                                self._create_vies_lookup(vals, country_code, vat_number)

            if vals.get("state_id") and not isinstance(vals["state_id"], int):
                vals["state_id"] = vals["state_id"].id

        res = super().create(vals_list)
        return res

    def _create_vies_lookup(self, vals, country_code, vat_number):
        """Attempt VIES lookup during partner creation. Updates vals dict in-place."""
        try:
            client = self._get_vies_client()
            vies_code = "EL" if country_code == "GR" else country_code
            response = client.service.checkVat(countryCode=vies_code, vatNumber=vat_number)
            if not response.valid and country_code == "GB":
                response = client.service.checkVat(countryCode="XI", vatNumber=vat_number)
            if response.valid:
                vals["vat"] = country_code + vat_number
                if response.name:
                    vals["name"] = response.name
                if response.address:
                    vals["street"] = response.address
                country = self.env["res.country"].search([("code", "=ilike", country_code)], limit=1)
                if not country and country_code == "GR":
                    country = self.env["res.country"].search([("code", "=ilike", "GR")], limit=1)
                if country:
                    vals["country_id"] = country.id
            else:
                _logger.info("VIES: VAT %s%s is not valid", country_code, vat_number)
        except Exception as e:
            _logger.warning("VIES service not available. Exception: %s", e)

    def get_partner_data(self):
        if self.country_id and self.country_id.code != "RO":
            return False
        if self.name and not self.vat:
            name = self.name.strip()
            match = re.match(r"^[Rr][Oo]\s*(\d{2,10})$", name) or re.match(r"^(\d{2,10})$", name)
            if match:
                self.vat = "RO" + match.group(1)
        res = self.with_context(skip_ro_vat_change=False).ro_vat_change()
        return res

    @api.model
    def _get_vies_client(self):
        """Lazy-load zeep Client for VIES SOAP service."""
        try:
            from zeep import Client  # pylint: disable=import-outside-toplevel
        except ImportError as e:
            raise UserError(
                self.env._("The 'zeep' library is required for VIES lookups. Install it with: pip install zeep")
            ) from e
        return Client("http://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl")

    def get_partner_name_from_vies(self):
        client = self._get_vies_client()

        # Determine country_code and vat_number from available data
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
            if self.vat:
                raise UserError(self.env._("Please add the country code to the vat number or country field"))
            if self.name and len(self.name) > 2 and not self.name.isdigit() and not self.name[:2].isdigit():
                vat_number = self.name[2:]
                country_code = self.name[:2]
            else:
                raise UserError(self.env._("Please add the country code to the vat number or country field"))

        try:
            response = client.service.checkVat(countryCode=country_code, vatNumber=vat_number)
        except Exception as e:
            raise UserError(self.env._("VIES service error: %s") % e) from e
        if not response.valid and country_code == "GB":
            try:
                response = client.service.checkVat(countryCode="XI", vatNumber=vat_number)
            except Exception as e:
                raise UserError(self.env._("VIES service error: %s") % e) from e
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
            raise UserError(self.env._("Invalid VAT"))

    @api.onchange("vat", "country_id")
    def ro_vat_change(self):
        skip_ro_vat_change = self.env.context.get("skip_ro_vat_change", True)
        return super(ResPartner, self.with_context(skip_ro_vat_change=skip_ro_vat_change)).ro_vat_change()

    def _fix_vat_number(self, vat, country_id):
        if self.env.context.get("skip_ro_vat_change"):
            return vat
        return super()._fix_vat_number(vat, country_id)

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
                                self.env._("You cannot change the type of contact if there are already invoices on it.")
                            )
                        if "vat" in vals and vals["vat"] != partner.vat:
                            new_vat = vals["vat"] or ""
                            old_vat = partner.vat or ""
                            if old_vat:
                                new_vat_digits = re.sub(r"\D", "", new_vat)
                                old_vat_digits = re.sub(r"\D", "", old_vat)
                                if new_vat_digits != old_vat_digits:
                                    raise UserError(
                                        self.env._("You cannot change VAT if there are already invoices on it.")
                                    )

        return super().write(vals)
