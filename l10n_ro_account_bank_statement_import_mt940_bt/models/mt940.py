# Copyright (C) 2016 Forest and Biomass Romania
# Copyright (C) 2022 NextERP Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from odoo import models


class MT940Parser(models.AbstractModel):
    _inherit = "l10n.ro.account.bank.statement.import.mt940.parser"
    """Parser for ing MT940 bank statement import files."""

    def get_tag_61_regex(self):
        if self.get_mt940_type() == "mt940_ro_bt":
            return re.compile(
                r"^(?P<date>\d{6})(?P<line_date>\d{0,4})"
                r"(?P<sign>[CD])(?P<amount>\d+,\d{2})[NF](?P<type>.{3})"
                r"(?P<reference>\w{1,50})"
            )
        return super().get_tag_61_regex()

    def get_tag_86_regex(self):
        if self.get_mt940_type() == "mt940_ro_bt":
            return re.compile(
                r"^(?P<desc>.*?)\s+"
                r"C\.I\.F\.:?(?P<cif>\d{5,})\s+.*?"  # CIF + orice altceva
                r"(?P<partner_name>[A-Z][A-Z0-9\s\.\-&]{3,})\s+"
                r"(?P<account_number>[A-Z]{2}\d{2}[A-Z0-9]{10,30})"
            )
        return super().get_tag_86_regex()

    def get_header_lines(self):
        if self.get_mt940_type() == "mt940_ro_bt":
            return 1
        return super().get_header_lines()

    def get_header_regex(self):
        if self.get_mt940_type() == "mt940_ro_bt":
            return "^{1:"
        return super().get_header_regex()

    def handle_tag_25(self, data, result):
        if self.get_mt940_type() == "mt940_ro_bt":
            result["account_number"] = data.replace(".", "").strip()
            return result
        return super().handle_tag_25(data, result)

    def handle_tag_28(self, data, result):
        if result["statement"] and self.get_mt940_type() == "mt940_ro_bt":
            result["statement"]["name"] = data.replace(".", "").strip()
            return result
        return super().handle_tag_28(data, result)

    def handle_tag_61(self, data, result):
        """get transaction values"""

        res = super().handle_tag_61(data, result)
        if self.get_mt940_type() == "mt940_ro_bt":
            transaction = {}
            if result["statement"]["transactions"]:
                transaction = result["statement"]["transactions"][-1]

            transaction["unique_import_id"] = data

        return res

    def handle_tag_86(self, data, result):
        """Parse 86 tag containing reference data."""
        if self.get_mt940_type() == "mt940_ro_bt":
            transaction = {}
            if result["statement"]["transactions"]:
                transaction = result["statement"]["transactions"][-1]

            tag_86_regex = self.get_tag_86_regex()
            re_86 = tag_86_regex.match(data)
            if re_86:
                parsed_data = re_86.groupdict()
                transaction["partner_name"] = parsed_data["partner_name"]
                transaction["account_number"] = parsed_data["account_number"]
                cif = parsed_data.get("cif", "").strip()
                domain = [("vat", "like", cif), ("is_company", "=", True)]
                partner = self.env["res.partner"].search(domain, limit=1)
                if partner:
                    transaction["partner_name"] = partner.name
                    transaction["partner_id"] = partner.id
            if not transaction.get("payment_ref", ""):
                transaction["payment_ref"] = data

        return super().handle_tag_86(data, result)
