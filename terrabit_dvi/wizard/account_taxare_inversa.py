# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com>
# See README.rst file on addons root folder for license details


from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountInvoiceTaxareInversa(models.TransientModel):
    _name = "account.invoice.taxare.inversa"
    _description = "Taxare inversă intracomunitară (4426=4427)"

    date = fields.Date(default=fields.Date.today)
    tax_id = fields.Many2one(
        "account.tax",
        string="Taxa TVA",
        domain=[("type_tax_use", "=", "purchase")],
        required=True,
    )
    tax_base = fields.Monetary(string="Baza de impozitare (RON)")
    tax_value = fields.Monetary(string="TVA de înregistrat (RON)")
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        active_id = self.env.context.get("active_id")
        if not active_id:
            return defaults
        invoice = self.env["account.move"].browse(active_id)
        defaults["date"] = invoice.invoice_date or fields.Date.today()
        # Căutăm taxa de TVA la cumpărare a companiei ca sugestie implicită
        tax = self.env.company.account_purchase_tax_id
        if tax:
            defaults["tax_id"] = tax.id
        amount_untaxed = abs(invoice.amount_untaxed_signed)
        defaults["tax_base"] = amount_untaxed
        if tax and amount_untaxed:
            tax_vals = tax.compute_all(amount_untaxed)
            defaults["tax_value"] = tax_vals["total_included"] - tax_vals["total_excluded"]
        return defaults

    @api.onchange("tax_id", "tax_base")
    def _onchange_tax(self):
        if self.tax_id and self.tax_base:
            tax_vals = self.tax_id.compute_all(self.tax_base)
            self.tax_value = tax_vals["total_included"] - tax_vals["total_excluded"]

    def _get_account_by_code(self, code_prefix):
        return self.env["account.account"].search(
            [
                ("code", "=like", f"{code_prefix}%"),
                ("company_ids", "in", [self.env.company.id]),
            ],
            limit=1,
        )

    def do_create_taxare_inversa(self):
        active_id = self.env.context.get("active_id")
        invoice = self.env["account.move"].browse(active_id)

        if not self.tax_value or self.tax_value <= 0:
            raise UserError(self.env._("Valoarea TVA trebuie să fie pozitivă."))

        account_4426 = self._get_account_by_code("4426")
        account_4427 = self._get_account_by_code("4427")

        if not account_4426:
            raise UserError(
                self.env._("Contul 4426 (TVA deductibil achiziții IC) nu a fost găsit în planul de conturi.")
            )
        if not account_4427:
            raise UserError(
                self.env._("Contul 4427 (TVA colectată achiziții IC) nu a fost găsit în planul de conturi.")
            )

        journal = self.env["account.journal"].search(
            [("type", "=", "general"), ("company_id", "=", self.env.company.id)],
            limit=1,
        )
        if not journal:
            raise UserError(self.env._("Nu există un jurnal de tip 'General' configurat."))

        # Determinăm tag-urile de taxe pentru raportare D300
        tax_tag_ids_debit = []
        if self.tax_id:
            repartition_tax = self.tax_id.invoice_repartition_line_ids.filtered(
                lambda r: r.repartition_type == "tax"
            )
            if repartition_tax:
                tax_tag_ids_debit = [(6, 0, repartition_tax[0].tag_ids.ids)]

        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "journal_id": journal.id,
                "date": self.date,
                "ref": self.env._("Taxare inversă IC — %s", invoice.name),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": account_4426.id,
                            "name": self.env._("TVA achiziții intracomunitare (taxare inversă)"),
                            "debit": self.tax_value,
                            "credit": 0.0,
                            "tax_line_id": self.tax_id.id if self.tax_id else False,
                            "tax_tag_ids": tax_tag_ids_debit,
                            "tax_base_amount": self.tax_base,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": account_4427.id,
                            "name": self.env._("TVA colectată intracomunitară (taxare inversă)"),
                            "debit": 0.0,
                            "credit": self.tax_value,
                        },
                    ),
                ],
            }
        )
        move.action_post()
        invoice.taxare_inversa_move_id = move

        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": move.id,
            "target": "current",
        }
