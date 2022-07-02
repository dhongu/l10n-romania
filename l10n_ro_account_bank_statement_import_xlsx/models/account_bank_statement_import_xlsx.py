# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import base64
import logging
import psycopg2
from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountBankStatementImport(models.TransientModel):
    _inherit = "account.bank.statement.import"

    def _check_xlsx(self, filename):
        return filename and filename.lower().strip().endswith(".xlsx")

    def import_file(self):
        # In case of CSV files, only one file can be imported at a time.

        if not self._check_xlsx(self.filename):
            return super(AccountBankStatementImport, self).import_file()

        ctx = dict(self.env.context)
        import_wizard = self.env["base_import.import"].create(
            {
                "res_model": "account.bank.statement.line",
                'file': base64.b64decode(self.data_file),
                'file_name': self.filename,
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
                "filename": self.filename,
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

        if "payment_ref" in import_fields:
            index_payment_ref = import_fields.index("payment_ref")
            for item in data:
                if not item[index_partner_id] and item[index_payment_ref]:
                    domain = [("name", "=", item[index_payment_ref])]
                    invoice = self.env["sale.order"].search(domain, limit=1)
                    if invoice:
                        item[index_partner_id] = invoice.partner_id.id
                if not item[index_payment_ref]:
                    item[index_payment_ref] = "N/A"

        return data



    @api.multi
    def parse_preview(self, options, count=10):
        if options.get('bank_stmt_import', False):
            self = self.with_context(bank_stmt_import=True)
        return super(AccountBankStmtImportXLSX, self).parse_preview(options, count=count)

    @api.multi
    def do(self, fields, columns, options, dryrun=False):
        if options.get('bank_stmt_import', False):
            self._cr.execute('SAVEPOINT import_bank_stmt')
            vals = {
                'journal_id': self._context.get('journal_id', False),
                'reference': self.file_name
            }
            statement = self.env['account.bank.statement'].create(vals)
            res = super(AccountBankStmtImportXLSX, self.with_context(bank_statement_id=statement.id)).do(fields, columns, options, dryrun=dryrun)

            try:
                if dryrun:
                    self._cr.execute('ROLLBACK TO SAVEPOINT import_bank_stmt')
                else:
                    self._cr.execute('RELEASE SAVEPOINT import_bank_stmt')
                    res['messages'].append({
                        'statement_id': statement.id,
                        'type': 'bank_statement'
                        })
            except psycopg2.InternalError:
                pass
            return res
        else:
            return super(AccountBankStmtImportXLSX, self).do(fields, columns, options, dryrun=dryrun)
