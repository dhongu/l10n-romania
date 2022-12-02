# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import base64
import logging

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountBankStatementImport(models.TransientModel):
    _inherit = "account.bank.statement.import"

    def _check_xlsx(self, filename):
        return filename and filename.lower().strip().endswith(".xlsx")

    def import_file(self):
        # In case of XLSX files, only one file can be imported at a time.
        if len(self.attachment_ids) > 1:
            xlsx = [bool(self._check_xlsx(att.name)) for att in self.attachment_ids]
            if True in xlsx and False in xlsx:
                raise UserError(_("Mixing xlsx files with other file types is not allowed."))
            if xlsx.count(True) > 1:
                raise UserError(_("Only one xlsx file can be selected."))
            return super(AccountBankStatementImport, self).import_file()

        if not self._check_xlsx(self.attachment_ids.name):
            return super(AccountBankStatementImport, self).import_file()
        ctx = dict(self.env.context)
        import_wizard = self.env["base_import.import"].create(
            {
                "res_model": "account.bank.statement.line",
                "file": base64.b64decode(self.attachment_ids.datas),
                "file_name": self.attachment_ids.name,
                "file_type": "xlsx",
            }
        )
        ctx["wizard_id"] = import_wizard.id
        return {
            "type": "ir.actions.client",
            "tag": "import_bank_stmt",
            "params": {
                "model": "account.bank.statement.line",
                "context": ctx,
                "filename": self.attachment_ids.name,
            },
        }


class AccountBankStmtImportXLSX(models.TransientModel):
    _inherit = "base_import.import"

    def _parse_import_data(self, data, import_fields, options):
        data = super(AccountBankStmtImportXLSX, self)._parse_import_data(data, import_fields, options)
        statement_id = self._context.get("bank_statement_id", False)
        if not statement_id:
            return data

        if "partner_id" not in import_fields:
            import_fields += ["partner_id/.id"]
            for item in data:
                item += [False]

        index_partner_id = import_fields.index("partner_id/.id")

        if "partner_name" in import_fields:
            index_partner_name = import_fields.index("partner_name")
            for item in data:
                domain = [("name", "ilike", item[index_partner_name])]
                partner = self.env["res.partner"].search(domain, limit=1)
                if partner:
                    item[index_partner_id] = partner.id

        search_fields = ["name", "ref", "payment_ref"]
        for search_field in search_fields:
            if search_field in import_fields:
                index_field = import_fields.index(search_field)
                for item in data:
                    if not item[index_partner_id] and item[index_field]:
                        domain = [("name", "=", item[index_field])]
                        sale_order = self.env["sale.order"].search(domain, limit=1)
                        if sale_order:
                            item[index_partner_id] = sale_order.partner_id.id

                    if not item[index_partner_id] and item[index_field]:
                        domain = [("move_type", "=", "out_invoice"), ("name", "=", item[index_field])]
                        invoice = self.env["account.move"].search(domain, limit=1)
                        if invoice:
                            item[index_partner_id] = invoice.partner_id.id

                    if not item[index_partner_id] and item[index_field]:
                        domain = [("move_type", "=", "out_invoice"), ("ref", "=", item[index_field])]
                        invoice = self.env["account.move"].search(domain, limit=1)
                        if invoice:
                            item[index_partner_id] = invoice.partner_id.id
                            item[index_field] = invoice.name

                    if not item[index_field] and search_field == "index_payment_ref":
                        item[index_field] = "N/A"

        return data
