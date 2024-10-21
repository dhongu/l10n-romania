from odoo import _, fields, models
from odoo.exceptions import UserError


class GetPartnerData(models.TransientModel):
    _inherit = "get.partner.data"

    service = fields.Selection(selection_add=[("openapi", "OpenAPI")])

    def do_get_data(self):
        super().do_get_data()
        if self.service == "openapi":
            openapi_key = self.env["ir.config_parameter"].sudo().get_param(key="openapi_key", default=False)
            if not openapi_key:
                raise UserError(_("API Key is missing - please contact support service!"))
            self.partner_id.button_get_partner_data_openapi()

        action = {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Title",
                "message": "message",
                "sticky": True,
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
        return action
