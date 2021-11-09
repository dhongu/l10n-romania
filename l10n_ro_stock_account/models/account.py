# ©  2008-2018 Fekete Mihai <mihai.fekete@forbiom.eu>
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import _, api, fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    @api.multi
    @api.constrains("internal_type", "reconcile")
    def _check_reconcile(self):
        accounts = self.env["account.account"]
        for account in self:
            if (
                account != account.company_id.property_stock_picking_payable_account_id
                and account != account.company_id.property_stock_picking_receivable_account_id
            ):
                accounts |= account

        super(AccountAccount, accounts)._check_reconcile()


class account_move_line(models.Model):
    _inherit = "account.move.line"

    stock_picking_id = fields.Many2one(
        "stock.picking", string="Stock Picking", help="This account move line has been generated by this stock picking"
    )
    stock_move_id = fields.Many2one(
        "stock.move", string="Stock Move", help="This account move line has been generated by this stock move"
    )
    stock_inventory_id = fields.Many2one(
        "stock.inventory", string="Stock Inventory", help="This account move line has been generated by this inventory"
    )
    stock_location_id = fields.Many2one("stock.location", string="Location")  # locatia de stoc aferenta miscarii
    stock_location_dest_id = fields.Many2one(
        "stock.location", string="Location"
    )  # locatie folosita doar pentru notele contabile aferente transferului de stoc
