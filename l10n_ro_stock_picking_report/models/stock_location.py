# ©  2008-2022 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    store_pricelist_id = fields.Many2one("product.pricelist", string="Pricelist")
    user_id = fields.Many2one("res.users", string="Manager")

    is_store = fields.Boolean(string="Is a Store Location", compute="_compute_is_store")

    def _compute_is_store(self):
        self.is_store = False
