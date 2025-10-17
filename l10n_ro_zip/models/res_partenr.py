from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    zip_id = fields.Many2one('res.zip', string="Postal Code", domain="[('city_id', '=', city_id)]")


    @api.onchange("zip_id")
    def onchange_zip_id(self):
        for partner in self:
            if partner.zip_id:
                partner.zip = partner.zip_id.name
