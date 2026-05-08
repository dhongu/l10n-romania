# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import api, fields, models
from odoo.osv import expression


class ResZip(models.Model):
    _name = "res.zip"
    _description = "Zip Code"

    name = fields.Char(string="Postal Code", required=True)
    city = fields.Char(string="City Name", required=True)
    city_id = fields.Many2one(
        "res.city",
        string="City",
    )
    state = fields.Char(string="State Name")
    state_id = fields.Many2one("res.country.state", string="State")
    country_id = fields.Many2one("res.country", string="Country")
    street_type = fields.Char(string="Street Type")
    street_name = fields.Char(string="Street Name")
    sector = fields.Char(string="Sector")
    office = fields.Char(string="Office")
    address = fields.Char(string="Address")

    def _compute_display_name(self):
        for zip_code in self:
            if not zip_code.street_name:
                zip_code.display_name = f"{zip_code.city} ({zip_code.name})"
            else:
                zip_code.display_name = f"{zip_code.street_type} {zip_code.street_name} ({zip_code.name})"

    # @api.model
    # def _name_search(self, name, domain=None, operator="ilike", limit=None, order=None):
    #     # OVERRIDE
    #     domain = domain or []
    #     if operator != "ilike" or (name or "").strip():
    #         name_domain = ["|", ("name", "ilike", name), ("street_name", "ilike", name)]
    #         domain = expression.AND([name_domain, domain])
    #     return self._search(domain, limit=limit, order=order)

    @api.model
    def _search_display_name(self, operator, value):
        domain = super()._search_display_name(operator, value)
        if operator == "ilike" :
            name_domain = [
                "|",
                "|",
                ("name", "ilike", value),
                ("street_name", "ilike", value),
                ("street_type", "ilike", value),
            ]
            domain = expression.OR([domain, name_domain])
        return domain
