from odoo import fields, models
from odoo.exceptions import UserError


class GetPartnerData(models.TransientModel):
    _inherit = "get.partner.data"

    service = fields.Selection(selection_add=[("openapi", "OpenAPI")])

    def do_get_data(self):
        res = super().do_get_data()
        if self.service == "openapi":
            openapi_key = self.env["ir.config_parameter"].sudo().get_param(key="openapi_key", default=False)
            if not openapi_key:
                raise UserError(self.env._("API Key is missing - please contact support service!"))
            if self.partner_id.vat:
                if self.partner_id.vat.isdigit():
                    if not self.partner_id.country_id or (
                        self.partner_id.country_id and self.partner_id.country_id.code != "RO"
                    ):
                        raise UserError(self.env._("You can only use OpenAPI for Romanian partners!"))
                    vat_digit = self.partner_id.vat
                    self.partner_id.vat = ""
                    self.partner_id.vat = "RO" + vat_digit
            else:
                if self.partner_id.name and self.partner_id.name.isdigit():
                    if not self.partner_id.country_id or (
                        self.partner_id.country_id and self.partner_id.country_id.code != "RO"
                    ):
                        raise UserError(self.env._("You can only use OpenAPI for Romanian partners!"))
                    self.partner_id.vat = "RO" + self.partner_id.name
                    self.partner_id.name = self.partner_id.vat
                else:
                    self.partner_id.vat = self.partner_id.name

            self.partner_id.button_get_partner_data_openapi()
        return res
