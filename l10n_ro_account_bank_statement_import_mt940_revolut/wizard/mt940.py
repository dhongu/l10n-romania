# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from odoo import models


class MT940Parser(models.AbstractModel):
    _inherit = "l10n.ro.account.bank.statement.import.mt940.parser"
    """Parser for Revolut MT940 bank statement import files."""

    def get_header_regex(self):
        if self.get_mt940_type() == "mt940_ro_revolut":
            # Revolut files start directly with the "{4:" block, without the
            # "{1:...}{2:...}{3:...}" envelope other banks use. Using a regex
            # here (instead of a plain string) forces `pre_process_data` to
            # fall back to extracting every "{4:...}" block on its own, which
            # is what we need since a single Revolut export contains one
            # block per account currency.
            return "^{4:"
        return super().get_header_regex()

    def get_tag_61_regex(self):
        if self.get_mt940_type() == "mt940_ro_revolut":
            return re.compile(
                r"^(?P<date>\d{6})(?P<line_date>\d{0,4})"
                r"(?P<sign>[CD])(?P<amount>\d+,\d{0,2})N(?P<type>.{3})"
                r"(?P<reference>.*)"
            )
        return super().get_tag_61_regex()

    def handle_tag_60F(self, data, result):
        """A single Revolut export has one "{4:...}" block per currency
        wallet (all sharing the same IBAN). Keep track of each block's own
        currency on the statement itself, since `result["currency"]` only
        ever holds the first one encountered in the file."""
        res = super().handle_tag_60F(data, result)
        if self.get_mt940_type() == "mt940_ro_revolut" and result["statement"]:
            result["statement"]["revolut_currency"] = data[7:10]
        return res

    def handle_tag_61(self, data, result):
        """get transaction values"""

        res = super().handle_tag_61(data, result)
        if self.get_mt940_type() == "mt940_ro_revolut":
            transaction = {}
            if result["statement"]["transactions"]:
                transaction = result["statement"]["transactions"][-1]

            transaction["unique_import_id"] = data

        return res

    def handle_tag_86(self, data, result):
        """Parse the Revolut structured tag 86, made of "^NN" subfields:

        - ^20/^21: transaction narrative (^21 continues ^20 when present)
        - ^22: original currency amount / exchange rate for FX transactions
        - ^23: card details for card transactions
        - ^32: counterparty name
        - ^38: counterparty account number (IBAN)
        """
        if self.get_mt940_type() == "mt940_ro_revolut":
            transaction = {}
            if result["statement"]["transactions"]:
                transaction = result["statement"]["transactions"][-1]

            subfields = dict(re.findall(r"\^(\d{2})([^^]*)", data))
            narration = (subfields.get("20", "") + subfields.get("21", "")).strip()
            transaction["payment_ref"] = narration or transaction.get("payment_ref", "/")

            partner_name = subfields.get("32", "").strip()
            if partner_name:
                transaction["partner_name"] = partner_name

            account_number = subfields.get("38", "").strip()
            if account_number:
                transaction["account_number"] = account_number

            return result
        return super().handle_tag_86(data, result)
