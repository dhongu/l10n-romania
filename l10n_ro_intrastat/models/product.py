# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    intrastat_id = fields.Many2one("account.intrastat.code", string="Commodity Code")
    country_id = fields.Many2one("res.country", string="Country Of Origin")


class Product(models.Model):
    _inherit = "product.product"

    @api.multi
    def search_intrastat_code(self):
        self.ensure_one()
        return self.intrastat_id or self.categ_id.search_intrastat_code()

    def get_intrastat_recursively(self):
        """ Recursively search in product to find an intrastat code id """
        return self.intrastat_id.id or self.categ_id.get_intrastat_recursively()


class ProductCategory(models.Model):
    _inherit = "product.category"

    intrastat_id = fields.Many2one("account.intrastat.code", string="Commodity Code")

    @api.multi
    def search_intrastat_code(self):
        self.ensure_one()
        return self.intrastat_id or (self.parent_id and self.parent_id.search_intrastat_code())

    def get_intrastat_recursively(self):
        """ Recursively search in categories to find an intrastat code id
        """
        if self.intrastat_id:
            res = self.intrastat_id.id
        elif self.parent_id:
            res = self.parent_id.get_intrastat_recursively()
        else:
            res = None
        return res
