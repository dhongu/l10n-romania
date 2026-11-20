# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.exceptions import UserError

# Conturile de stoc pe care OMFP 1802/2014 (funcțiunea contului 446) le dă în contrapartidă
# pentru taxele vamale ale aprovizionărilor din import.
CUSTOMS_DUTY_STOCK_ACCOUNTS = ("301", "302", "303", "371", "381")


class StockValuationAdjustmentLines(models.Model):
    _inherit = "stock.valuation.adjustment.lines"

    def _create_account_move_line(self, credit_account_id, debit_account_id, remaining_qty):
        """Pe DVI, taxa vamală se înregistrează integral, inclusiv pentru marfa vândută înainte de DVI.

        Core-ul înregistrează doar partea rămasă în stoc (``remaining_qty``); pentru cantitatea deja
        livrată nu creează nicio linie, așa că 446 rămânea creditat sub taxa vamală din declarație
        (#722). Pentru partea vândută se adaugă, în doi pași cu corespondențe din OMFP 1802/2014:

        * ``Dr stoc = Cr 446``: taxa vamală intră în costul de achiziție;
        * ``Dr 60x = Cr stoc``: descărcarea completării de cost pentru cantitatea ieșită, pe contul
          de cheltuieli al categoriei produsului (607 la mărfuri, 601 la materii prime etc.).

        Creditul pe 446 este astfel egal cu taxa vamală din declarație, oricând s-ar valida DVI-ul.
        """
        if self.cost_id.landed_type != "dvi" or not self.quantity:
            return super()._create_account_move_line(credit_account_id, debit_account_id, remaining_qty)

        # remaining_qty poate fi negativ (livrat fără stoc) sau, teoretic, peste cantitatea recepției
        in_stock_qty = min(max(remaining_qty, 0.0), self.quantity)
        lines = super()._create_account_move_line(credit_account_id, debit_account_id, in_stock_qty)

        # diferența până la valoarea liniei, nu proporția rotunjită: cele două părți însumează exact
        # taxa repartizată, fără un ban rămas pe 446
        in_stock_amount = self.currency_id.round(self.additional_landed_cost * in_stock_qty / self.quantity)
        sold_amount = self.currency_id.round(self.additional_landed_cost - in_stock_amount)
        if self.currency_id.is_zero(sold_amount):
            return lines

        stock_account = self.env["account.account"].browse(debit_account_id)
        if not stock_account.code or not stock_account.code.startswith(CUSTOMS_DUTY_STOCK_ACCOUNTS):
            raise UserError(
                self.env._(
                    "Product %(product)s left the stock (fully or partly) before the DVI, and its stock "
                    "account %(account)s cannot take customs duties: under OMFP 1802/2014 (account 446), "
                    "customs duties are added only to accounts 301, 302, 303, 371 or 381. Check the "
                    "product category.",
                    product=self.product_id.display_name,
                    account=stock_account.display_name or "-",
                )
            )
        expense_account = self.product_id.product_tmpl_id.get_product_accounts()["expense"]
        if not expense_account:
            raise UserError(
                self.env._(
                    "Please configure the expense account for product %s: the customs duty of the "
                    "quantity delivered before the DVI is booked on it.",
                    self.product_id.display_name,
                )
            )

        base_line = self._prepare_account_move_line_values()
        base_line["name"] = self.env._("%s (out of stock before the DVI)", self.name)
        pairs = (
            (debit_account_id, credit_account_id),  # Dr stoc = Cr 446
            (expense_account.id, debit_account_id),  # Dr 60x = Cr stoc
        )
        for debit_id, credit_id in pairs:
            debit_line = dict(base_line, account_id=debit_id)
            credit_line = dict(base_line, account_id=credit_id)
            if sold_amount > 0:
                debit_line["debit"] = credit_line["credit"] = sold_amount
            else:
                debit_line["credit"] = credit_line["debit"] = -sold_amount
            lines += [[0, 0, debit_line], [0, 0, credit_line]]
        return lines
