# Copyright (C) 2018 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Account(models.Model):
    _inherit = "account.account"

    external_code = fields.Char(compute="_compute_external_code", store=True)

    @api.depends("code")
    def _compute_external_code(self):
        for account in self:
            account.external_code = account.internal_to_external()

    def external_code_to_internal(self, code):
        account_id = False
        if "." in code:
            odoo_code, analytic = code.split(".")
            odoo_code = (odoo_code + "00000")[:4] + analytic.zfill(2)
        else:
            odoo_code = (code + "00000")[:6]
        account = self.env["account.account"].search([("code", "=", odoo_code)])
        if len(account) == 1:
            account_id = account.id
        return account_id

    def internal_to_external(self):
        cont = self.code[:4]
        while cont[-1] == "0":
            cont = cont[:-1]
        analitic = int(self.code[4:])
        if analitic:
            cont += "." + str(analitic)
        return cont

    def name_get(self):
        result = []
        for account in self:
            name = account.external_code + " " + account.name
            result.append((account.id, name))
        return result
