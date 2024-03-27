from odoo import fields, models


class GetPartnerData(models.TransientModel):
    _name = "get.partner.data"
    _description = "Get partner data from"

    service = fields.Selection(
        [("anaf", "ANAF"), ("vies", "VIES for non-Romanian partners")],
        default="anaf",
        string="Service",
    )

    def do_get_data(self):
        active_ids = self.env.context.get("active_ids", [])
        active_model = self.env.context.get("active_model", "res.partner")
        partner = self.env[active_model].browse(active_ids)
        if self.service == "anaf":
            partner.get_partner_data()
        if self.service == "vies":
            partner.get_partner_name_from_vies()
        return
