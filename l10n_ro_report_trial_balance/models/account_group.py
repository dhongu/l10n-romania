# © 2018 Forest and Biomass Romania SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountGroup(models.Model):
    _inherit = 'account.group'

    group_child_ids = fields.One2many(comodel_name='account.group', inverse_name='parent_id', string='Child Groups')
    level = fields.Integer(string='Level', compute='_compute_level', store=True)
    # path = fields.Char(compute='_compute_path', store=True)
    account_ids = fields.One2many(comodel_name='account.account', inverse_name='group_id', string="Accounts")
    compute_account_ids = fields.Many2many('account.account', compute='_compute_group_accounts',
                                           string="Compute Accounts" )

    parent_path = fields.Char(index=True, compute='_compute_path', store=True)


    @api.multi
    @api.depends('parent_id', 'parent_id.level')
    def _compute_level(self):
        for group in self:
            if not group.parent_id:
                group.level = 0
            else:
                group.level = group.parent_id.level + 1

    @api.depends('parent_id')
    def _compute_path(self):
        for rec in self:
            if rec.parent_id:
                rec.parent_path =  rec.parent_id.parent_path + "/" + str(rec.id)
            else:
                rec.parent_path = str(rec.id)

    @api.multi
    @api.depends('account_ids', 'group_child_ids', 'parent_id')
    def _compute_group_accounts(self):
        account_obj = self.env['account.account']
        #accounts = account_obj.search([])
        for group in self:
            accounts = group.get_accounts()
            gr_acc = accounts.ids
            # if group.group_child_ids:
            #     group_accounts = self.env['account.account']
            #     for child in group.group_child_ids:
            #         group_accounts |= child.compute_account_ids
            #     gr_acc = group_accounts.ids
            # else:
            #     prefix = group.code_prefix if group.code_prefix else group.name
            #     account_ids = accounts.filtered(lambda a: a.code.startswith(prefix))
            #     # group.account_ids = account_ids
            #     gr_acc = account_ids.ids

            group.compute_account_ids = [(6, 0, gr_acc)]


    def get_accounts(self):
        accounts = self.env['account.account']
        for group in self:
            if group.group_child_ids:
                accounts |= group.group_child_ids.get_accounts()
            else:
                accounts |= group.account_ids
        return  accounts

