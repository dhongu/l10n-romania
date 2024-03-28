from odoo import fields, models,api


class GetPartnerData(models.TransientModel):
    _name = "get.partner.data"
    _description = "Get partner data from"

    service = fields.Selection(
        [("anaf", "ANAF"), ("vies", "VIES for non-Romanian partners")],
        default="anaf",
        string="Service",
    )

    def default_get(self, fields):
        res = super(GetPartnerData, self).default_get(fields)
        active_ids = self.env.context.get("active_ids", [])
        active_model = self.env.context.get("active_model", "res.partner")
        partner = self.env[active_model].browse(active_ids)
        if partner:
            res['partner_id'] = partner.id
        return res

    partner_id = fields.Many2one('res.partner', string='Partner')

    def do_get_data(self):
        if self.service == "anaf":
            self.partner_id.get_partner_data()
        if self.service == "vies":
            self.partner_id.get_partner_name_from_vies()
        return
