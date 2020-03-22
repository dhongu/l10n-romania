# -*- coding: utf-8 -*-
# ©  2015-2017 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details




from odoo import api, models, fields, _
from odoo.exceptions import UserError



class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    production_id = fields.Many2one('mrp.production')


class MrpProduction(models.Model):
    _inherit = 'mrp.production'


    acc_move_line_ids = fields.One2many('account.move.line', 'production_id', string='Account move lines')



    @api.multi
    def post_inventory(self):

        res = super(MrpProduction, self).post_inventory()
        for production in self:
            acc_move_line_ids = self.env['account.move.line']
            for move in production.move_raw_ids:
                acc_move_line_ids |= move.account_move_ids.line_ids
            for move in production.move_finished_ids:
                acc_move_line_ids |= move.account_move_ids.line_ids
            if acc_move_line_ids:
                acc_move_line_ids.write({'production_id': production.id})
        return res
