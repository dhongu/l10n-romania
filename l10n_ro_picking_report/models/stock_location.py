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
        # the location type comes from l10n_ro_stock_account_store, when installed
        if "l10n_ro_merchandise_type" not in self._fields:
            self.is_store = False
            return
        for location in self:
            location.is_store = location.usage == "internal" and location.l10n_ro_merchandise_type == "store"
