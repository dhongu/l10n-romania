# ©  2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _compute_is_storno(self):
        res = super()._compute_is_storno()
        for move in self:
            if move.reversed_entry_id:
                move.is_storno = not move.reversed_entry_id.is_storno

        return res


# class AccountMoveLine(models.Model):
#     _inherit = "account.move.line"
#
#     storno_line = fields.Boolean()
#
#     @api.onchange("storno_line")
#     def onchange_storno_line(self):
#         if self.move_id.is_storno:
#             self.storno_line = False
#
#         if self.storno_line or self.move_id.is_storno:
#             self.debit = -1 * abs(self.debit)
#             self.credit = -1 * abs(self.credit)
#         else:
#             self.debit = abs(self.debit)
#             self.credit = abs(self.credit)
#
#     # def _compute_balance(self):
#     #     res =  super()._compute_balance()
#     #     for line in self:
#     #         if line.balance:
#     #             if line.account_id.l10n_ro_usage == "activ":
#     #                 if line.balance < 0.0:
#     #                     line.balance = -1 * line.balance
#     #             if line.account_id.l10n_ro_usage == "pasiv":
#     #                 if line.balance > 0.0:
#     #                     line.balance = -1 * line.balance
#     #
#     #
#     #     return res
#
#     def _compute_debit_credit(self):
#         res = super()._compute_debit_credit()
#         for line in self:
#             if line.company_id.account_storno:
#                 if line.storno_line:
#                     line.debit = -line.balance if line.balance > 0.0 else 0.0
#                     line.credit = line.balance if line.balance < 0.0 else 0.0
#         return res
#
#     # def _compute_debit_credit(self):
#     #     res = super()._compute_debit_credit()
#     #     for line in self:
#     #         if line.company_id.account_storno:
#     #             if line.storno_line:
#     #                 line.debit = -line.balance if line.balance > 0.0 else 0.0
#     #                 line.credit = line.balance if line.balance < 0.0 else 0.0
#     #
#     #             # if line.account_id.l10n_ro_usage == "activ" and line.credit:
#     #             #     line.debit = -line.credit
#     #             #     line.credit = 0.0
#     #             # if line.account_id.l10n_ro_usage == "pasiv" and line.debit:
#     #             #     line.credit = -line.debit
#     #             #     line.debit = 0
#     #             if line.credit < 0.0 or line.debit < 0.0:
#     #                 line.storno_line = True
#     #     return res
#
#     def _sanitize_vals(self, vals):
#         if vals.get("storno_line"):
#             return vals
#         return super()._sanitize_vals(vals)
