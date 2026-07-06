# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models

from odoo.addons.base.models.res_bank import sanitize_account_number


class AccountBankStatementImport(models.TransientModel):
    _inherit = "account.statement.import"

    def _is_revolut(self):
        if self._context.get("journal_id"):
            journal = self.env["account.journal"].browse(self._context["journal_id"])
            bank_bic = journal.bank_account_id.bank_bic or ""
            return bank_bic.startswith("REVO")
        return self._context.get("type") == "mt940_ro_revolut"

    def _parse_file(self, data_file):
        if self._is_revolut():
            parser = self.env["l10n.ro.account.bank.statement.import.mt940.parser"]
            parser = parser.with_context(type="mt940_ro_revolut")
            data = parser.parse(data_file)
            if data:
                return self._split_by_currency(data)
        return super()._parse_file(data_file)

    def _split_by_currency(self, data):
        """A single Revolut export bundles one "{4:...}" block per currency
        wallet under the same IBAN. Group them by their own currency instead
        of the parser's single (first-seen) one, so each wallet is matched
        against its own (currency-specific) bank journal.

        Odoo doesn't allow registering the same account number twice on a
        partner (see the `unique(sanitized_acc_number, partner_id)` SQL
        constraint on `res.partner.bank`), so a single Revolut IBAN can only
        ever be linked to one journal/currency. Wallets for which no such
        journal exists are dropped instead of making the whole import fail.
        """
        default_currency, account_number, statements = data
        grouped = {}
        for st_vals in statements:
            currency = st_vals.pop("revolut_currency", None) or default_currency
            grouped.setdefault(currency, []).append(st_vals)
        return [
            (currency, account_number, stmts)
            for currency, stmts in grouped.items()
            if self._revolut_journal_exists(account_number, currency)
        ]

    def _revolut_journal_exists(self, account_number, currency_code):
        currency = self.env["res.currency"].search([("name", "=ilike", currency_code)], limit=1)
        if not currency:
            return False
        sanitized = sanitize_account_number(account_number)
        journal = self.env["account.journal"].search(
            [
                ("type", "=", "bank"),
                ("bank_account_id.sanitized_acc_number", "ilike", sanitized),
            ],
            limit=1,
        )
        if not journal:
            return False
        journal_currency = journal.currency_id or self.env.company.currency_id
        return journal_currency == currency
