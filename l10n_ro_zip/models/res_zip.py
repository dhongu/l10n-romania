# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import api, fields, models
from odoo.osv import expression


class ResZip(models.Model):
    _name = "res.zip"
    _description = "Zip Code"

    name = fields.Char(string="Postal Code", required=True)
    city = fields.Char(string="City", required=True)
    city_id = fields.Many2one(
        "res.city",
        string="City",
    )
    state = fields.Char(string="State")
    state_id = fields.Many2one("res.country.state", string="State")
    country_id = fields.Many2one("res.country", string="Country")
    street_type = fields.Char(string="Street Type")
    street_name = fields.Char(string="Street Name")
    sector = fields.Char(string="Sector")
    office = fields.Char(string="Office")
    address = fields.Char(string="Address")

    def _compute_display_name(self):
        for zip in self:
            if not zip.street_name:
                zip.display_name = f"{zip.city} ({zip.name})"
            else:
                zip.display_name = f"{zip.street_type} {zip.street_name} ({zip.name})"

    @api.model
    def _name_search(self, name, domain=None, operator="ilike", limit=None, order=None):
        # OVERRIDE
        domain = domain or []
        if operator != "ilike" or (name or "").strip():
            name_domain = ["|", ("name", "ilike", name), ("street_name", "ilike", name)]
            domain = expression.AND([name_domain, domain])
        return self._search(domain, limit=limit, order=order)
