# -*- coding: utf-8 -*-
# ©  2016 Forest and Biomass Romania
# See README.rst file on addons root folder for license details

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

"""
class product_product(models.Model):
    _inherit = "product.product"

    d394_id = fields.Many2one('report.394.code', string='D394 codes')
"""


class report_394_code(models.Model):
    _name = "report.394.code"
    _description = "D394 code"

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = "name"
    _order = "parent_left"

    name = fields.Char("D394 Code")
    parent_id = fields.Many2one("report.394.code", "Parent Code", ondelete="restrict")
    child_ids = fields.One2many("report.394.code", "parent_id", string="Child Codes")
    parent_left = fields.Integer("Left Parent", select=True)
    parent_right = fields.Integer("Rigth Parent", select=True)
    description = fields.Char("Description")
    # product_ids = fields.One2many('product.product', 'd394_id', string='Products')

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_("You cannot create recursive codes."))
