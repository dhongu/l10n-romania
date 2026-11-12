from odoo import fields, models
from odoo.exceptions import UserError


class CashRegisterOperation(models.TransientModel):
    _name = "l10n.ro.cash.register.operation"
    _description = "Cash Register Operation"

    journal_id = fields.Many2one("account.journal", string="Journal", required=True, domain=[("type", "=", "cash")])
    currency_id = fields.Many2one(related="journal_id.currency_id", string="Currency", readonly=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    amount = fields.Monetary(required=True)
    operation = fields.Selection(
        [
            ("in", "Cash In"),
            ("out", "Cash Out"),
        ],
        required=True,
    )
    description = fields.Char()
    partner_id = fields.Many2one("res.partner", string="Partner")
    counterpart_account_id = fields.Many2one("account.account", string="Account", required=True)

    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if not defaults.get("counterpart_account_id"):
            defaults["counterpart_account_id"] = self.env.company.transfer_account_id.id
        return defaults

    def _check_counterpart_account(self):
        """Operatorul nu poate muta numerar între case sau către bancă direct, alegând ca
        cont corespondent un cont de numerar sau de bancă: transferul se face prin contabil."""
        self.ensure_one()
        if (
            self.env["account.journal"]._l10n_ro_is_restricted_cash_operator()
            and self.counterpart_account_id.account_type == "asset_cash"
        ):
            raise UserError(
                self.env._(
                    "As cash register operator you cannot use a cash or bank account (%s) as the "
                    "counterpart account. Ask an accountant to record transfers between cash desks or to the bank.",
                    self.counterpart_account_id.display_name,
                )
            )

    def action_confirm(self):
        # se va genra o nota contabila cu operatia
        self.ensure_one()
        # Operatorul fără drepturi de contabil emite operația doar pe casa lui; nota contabilă
        # se creează apoi cu sudo, în numele lui (create_uid rămâne operatorul).
        self.journal_id._l10n_ro_check_cash_operator()
        self._check_counterpart_account()
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
        move = self.env["account.move"].sudo().create(value)
        move.write({"l10n_ro_cash_document_type": "other"})
        move._post()
