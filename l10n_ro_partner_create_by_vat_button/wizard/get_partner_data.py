from odoo import _, fields, models
from odoo.exceptions import UserError


class GetPartnerData(models.TransientModel):
    _name = "get.partner.data"
    _description = "Get partner data from"

    service = fields.Selection([("anaf", "ANAF"), ("openapi", "OpenAPI"), ("vies", "VIES for non-Romanian partners")],
                               default="anaf", string="Service")

    def do_get_data(self):
        active_ids = self.env.context.get("active_ids", [])
        active_model = self.env.context.get("active_model", "res.partner")
        partner = self.env[active_model].browse(active_ids)
        if self.service == "anaf":
            partner.button_get_partner_data()
        if self.service == "openapi":
            openapi_key = self.env["ir.config_parameter"].sudo().get_param(key="openapi_key", default=False)
            if not openapi_key:
                raise UserError(_("API Key is missing - please contact support service!"))
            partner.button_get_partner_data_openapi()
        if self.service == "vies":
            partner.get_partner_name_from_vies()
        return
