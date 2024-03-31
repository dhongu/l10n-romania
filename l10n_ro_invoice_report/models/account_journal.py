# ©  2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    operating_unit_id = fields.Many2one("res.partner", string="Operating Unit",
                                        domain="[('parent_id','=',env.company.partner_id)]")
