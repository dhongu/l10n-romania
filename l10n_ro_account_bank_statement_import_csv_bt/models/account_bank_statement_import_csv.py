# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


import csv
import logging
from io import StringIO

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountBankStatementImport(models.TransientModel):
    _inherit = "account.bank.statement.import"

    def _check_csv(self, file):
        try:
            data_file = file.decode("utf-8")
            data_file = data_file.split("\n")
            cont = data_file[6]
            data_file = "\n".join(data_file[16:])
            data_file = StringIO(data_file)
            dict = csv.DictReader(data_file, delimiter=",", quotechar='"')
            res = {"csv": dict, "cont": cont.split(",")[1]}
        except BaseException:
            return False
        return res

    def _parse_file(self, data_file):

        csv = self._check_csv(data_file)

        if not csv:
            return super(AccountBankStatementImport, self)._parse_file(data_file)

        try:
            account_num, currency = csv["cont"].split(" ")
            all_statements = {}
            statement = {
                "name": "",
                "balance_start": "",
                "balance_end_real": "",
                "transactions": [],
            }
            all_statements[currency, account_num] = [statement]
            for line in csv["csv"]:
                if line.get("Data tranzactie", False):
                    debit = line.get("Debit") or "0"
                    debit = float(debit.replace(",", ""))
                    credit = line.get("Credit") or "0"
                    credit = float(credit.replace(",", ""))
                    detalii = line["Descriere"].split(";")
                    partner_name = ""
                    for item in detalii:
                        if item:
                            partner = self.env["res.partner"].name_search(item, limit=1)
                            if partner:
                                partner_name = partner[0][1]
                    vals_line = {
                        "date": line["Data tranzactie"],
                        "name": line["Descriere"],
                        "ref": line["Referinta tranzactiei"],
                        "amount": debit + credit,
                        "partner_name": partner_name,
                    }

                    statement["transactions"] += [vals_line]

        except Exception as e:
            raise UserError(
                _(
                    "The following problem occurred during import."
                    " The file might not be valid.\n\n %s" % str(e)
                )
            )
        return currency, account_num, all_statements[currency, account_num]
