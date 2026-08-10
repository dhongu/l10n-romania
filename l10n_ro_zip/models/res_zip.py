# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import api, fields, models
from odoo.fields import Domain


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

    @api.depends("name", "city", "street_type", "street_name")
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
    #         name_domain = [("|", "name", "ilike", name), ("street_name", "ilike", name)]
    #         domain = Domain.AND([name_domain, domain])
    #     return self._search(domain, limit=limit, order=order)

    @api.model
    def _search_display_name(self, operator, value):
        # The standard domain only searches in 'name' (the postal code itself).
        domain = super()._search_display_name(operator, value)

        # Extend the search to the street fields for the most common string
        # operators. "ilike" is the operator used by the autocomplete widget,
        # so it must be included here, otherwise typing a street name in the
        # postal code field returns no result at all.
        # Note: with "=" the ORM optimizes `display_name = value` into a plain
        # `name in [value]` and never calls this method, so that branch is inert
        # on 19.0; it is kept for symmetry with the 18.0 branch.
        if operator in ("ilike", "like", "="):
            name_domain = [
                "|",
                "|",
                ("name", operator, value),
                ("street_name", operator, value),
                ("street_type", operator, value),
            ]
            domain = Domain.OR([domain, name_domain])

        return domain
