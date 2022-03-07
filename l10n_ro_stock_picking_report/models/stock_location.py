# Copyright (C) 2016 Forest and Biomass Romania
# Copyright (C) 2018 Dorin Hongu <dhongu(@)gmail(.)com
# Copyright (C) 2019 NextERP Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"


    store_pricelist_id = fields.Many2one("product.pricelist", string="Pricelist")

