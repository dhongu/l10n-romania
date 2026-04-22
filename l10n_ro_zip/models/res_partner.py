from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    zip_id = fields.Many2one("res.zip", string="Postal Code", domain="[('city_id', '=', city_id)]")

    @api.onchange("zip_id")
    def onchange_zip_id(self):
        for partner in self:
            if partner.zip_id:
                partner.zip = partner.zip_id.name
                if partner.zip_id.city_id:
                    partner.city_id = partner.zip_id.city_id
                if partner.zip_id.state_id:
                    partner.state_id = partner.zip_id.state_id
                if partner.zip_id.country_id:
                    partner.country_id = partner.zip_id.country_id
