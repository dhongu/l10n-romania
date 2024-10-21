from odoo import fields, models


class CashRegisterOperation(models.TransientModel):
    _name = "l10n.ro.cash.register.operation"
    _description = "Cash Register Operation"

    journal_id = fields.Many2one("account.journal", string="Journal", required=True, domain=[("type", "=", "cash")])
    currency_id = fields.Many2one(related="journal_id.currency_id", string="Currency", readonly=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    amount = fields.Monetary(string="Amount", required=True)
    operation = fields.Selection(
        [
            ("in", "Cash In"),
            ("out", "Cash Out"),
        ],
        string="Operation",
        required=True,
    )
    description = fields.Char(string="Description")
    partner_id = fields.Many2one("res.partner", string="Partner")
    counterpart_account_id = fields.Many2one("account.account", string="Account", required=True)

    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults["counterpart_account_id"] = self.env.company.transfer_account_id.id
        return defaults

    def action_confirm(self):
        # se va genra o nota contabila cu operatia
        self.ensure_one()
        value = {
            "journal_id": self.journal_id.id,
            "date": self.date,
            "ref": self.description,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "partner_id": self.partner_id.id,
                        "account_id": self.journal_id.default_account_id.id,
                        "name": self.description,
                        "debit" if self.operation == "in" else "credit": self.amount,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "partner_id": self.partner_id.id,
                        "account_id": self.counterpart_account_id.id,
                        "name": self.description,
                        "credit" if self.operation == "in" else "debit": self.amount,
                    },
                ),
            ],
        }
        move = self.env["account.move"].create(value)
        move._post()
