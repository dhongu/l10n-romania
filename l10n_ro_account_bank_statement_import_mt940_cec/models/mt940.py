# Copyright (C) 2022 Terrabit
# Copyright (C) 2022 NextERP Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import re

from odoo import models

_logger = logging.getLogger(__name__)


class MT940Parser(models.AbstractModel):
    _inherit = "l10n.ro.account.bank.statement.import.mt940.parser"

    def get_header_lines(self):
        if self.get_mt940_type() == "mt940_ro_cec":
            return 1
        return super().get_header_lines()

    def get_header_regex(self):
        if self.get_mt940_type() == "mt940_ro_cec":
            return ":20:"
        return super().get_header_regex()

    def get_subfield_split_text(self):
        if self.get_mt940_type() == "mt940_ro_cec":
            return "-"
        return super().get_subfield_split_text()

    def get_codewords(self):
        if self.get_mt940_type() == "mt940_ro_cec":
            return ["Referinta", "Platitor", "Beneficiar", "Detalii", "CODFISC"]
        return super().get_codewords()

    def get_tag_61_regex(self):
        if self.get_mt940_type() == "mt940_ro_cec":
            return re.compile(
                r"(?P<date>\d{6})(?P<line_date>\d{0,4})(?P<sign>[CD])"
                + r"(?P<amount>\d+,\d{2})N(?P<type>.{3})"
                + r".*//(?P<reference>\w{1,16}).*(?P<partner_name>.*)"
            )
        return super().get_tag_61_regex()

    def get_counterpart(self, transaction, subfield):
        """Get counterpart from transaction.

        Counterpart is often stored in subfield of tag 86. The subfield
        can be 31, 32, 33"""
        if self.get_mt940_type() == "mt940_ro_cec":
            if not subfield:
                return  # subfield is empty
            if len(subfield) >= 1 and subfield[0]:
                transaction.update({"account_number": subfield[0]})
            if len(subfield) >= 2 and subfield[1]:
                transaction.update({"partner_name": subfield[1]})
            if len(subfield) >= 3 and subfield[2]:
                # Holds the partner VAT number
                pass
            return transaction
        return super().get_counterpart(transaction, subfield)

    def handle_tag_28(self, data, result):
        if self.get_mt940_type() == "mt940_ro_cec":
            result["statement"]["name"] = data.replace(".", "").strip()
            return result
        return super().handle_tag_28(data, result)

    def handle_tag_86(self, data, result):
        if self.get_mt940_type() == "mt940_ro_cec":
            transaction = {}
            if result["statement"]["transactions"]:
                transaction = result["statement"]["transactions"][-1]

            if not transaction.get("name", False):
                transaction["payment_ref"] = data
                transaction["narration"] = data

                regec_p = r".*Platitor\s(?P<platitor>.*)"
                regec_p_iban = r".*Iban\sPlatitor\s(?P<iban_p>\w{24})"
                regec_b = r".*Beneficiar\s(?P<beneficiar>.*)"
                regec_b_iban = r".*Iban\sBeneficiar\s(?P<iban_b>\w{24})"

                regec_cfp = r".*CUI\/CNP\sPlatitor\s(?P<codfis_p>\w+)ORDONATOR"
                regec_cfb = r".*CUI\/CNP\sBeneficiar\s(?P<codfis_b>\w+)ORDONATOR"

                tag_86_regex_v1 = re.compile(",".join([regec_b, regec_b_iban, regec_cfb]))
                tag_86_regex_v2 = re.compile(",".join([regec_p, regec_p_iban, regec_cfp]))
                tag_86_regex_v3 = re.compile(",".join([regec_b, regec_cfb]))
                tag_86_regex_v4 = re.compile(",".join([regec_p, regec_cfp]))
                tag_86_regex_v5 = re.compile(regec_b)
                tag_86_regex_v6 = re.compile(regec_p)

                re_86 = tag_86_regex_v1.match(data)
                if not re_86:
                    re_86 = tag_86_regex_v2.match(data)
                if not re_86:
                    re_86 = tag_86_regex_v3.match(data)
                if not re_86:
                    re_86 = tag_86_regex_v4.match(data)
                if not re_86:
                    re_86 = tag_86_regex_v5.match(data)
                if not re_86:
                    re_86 = tag_86_regex_v6.match(data)

                if re_86:
                    parsed_data = re_86.groupdict()
                    if transaction["amount"] > 0:
                        transaction["partner_name"] = parsed_data.get("platitor", "").strip()
                        transaction["account_number"] = parsed_data.get("iban_p")
                        vat = parsed_data.get("codfis_p")

                    else:
                        transaction["partner_name"] = parsed_data.get("beneficiar", "").strip()
                        transaction["account_number"] = parsed_data.get("iban_b")
                        vat = parsed_data.get("codfis_b")
                    if vat:
                        domain = [
                            ("vat", "ilike", vat),
                            ("is_company", "=", True),
                        ]
                        partner = self.env["res.partner"].search(domain, limit=1)
                        if partner:
                            transaction["partner_name"] = partner.name
                            transaction["partner_id"] = partner.id
                    if parsed_data.get("detalii"):
                        transaction["payment_ref"] = parsed_data.get("detalii")

                    transaction["ref"] = parsed_data.get("ref")
            return result
        return super().handle_tag_86(data, result)
