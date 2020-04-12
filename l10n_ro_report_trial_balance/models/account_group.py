# © 2018 Forest and Biomass Romania SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountGroup(models.Model):
    _inherit = 'account.group'

    group_child_ids = fields.One2many(comodel_name='account.group', inverse_name='parent_id', string='Child Groups')
    level = fields.Integer(string='Level', compute='_compute_level', store=True)
    path = fields.Char(compute='_compute_path', store=True)
    account_ids = fields.One2many(comodel_name='account.account', inverse_name='group_id', string="Accounts")
    compute_account_ids = fields.Many2many('account.account', compute='_compute_group_accounts', string="Accounts",
                                           store=True)



    @api.multi
    @api.depends('parent_id', 'parent_id.level')
    def _compute_level(self):
        for group in self:
            if not group.parent_id:
                group.level = 0
            else:
                group.level = group.parent_id.level + 1

    @api.depends('name', 'parent_id.path')
    def _compute_path(self):
        for rec in self:
            if rec.parent_id:
                rec.path = rec.parent_id.path + " / " + rec.code_prefix or '0'
            else:
                rec.path = rec.code_prefix or '0'

    @api.multi
    @api.depends('code_prefix', 'account_ids', 'account_ids.code',
                 'group_child_ids', 'group_child_ids.account_ids.code')
    def _compute_group_accounts(self):
        account_obj = self.env['account.account']
        accounts = account_obj.search([])  # ('company_id', '=', self.company_id.id)  #trebuie sa tina cont si de companie!
        for group in self:
            if group.group_child_ids:
                group_accounts = self.env['account.account']
                for child in group.group_child_ids:
                    group_accounts |= child.compute_account_ids
                gr_acc = group_accounts.ids
            else:
                prefix = group.code_prefix if group.code_prefix else group.name
                account_ids = accounts.filtered(lambda a: a.code.startswith(prefix))
                group.account_ids = account_ids
                gr_acc = account_ids.ids


            group.compute_account_ids = [(6, 0, gr_acc)]
