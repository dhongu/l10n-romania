# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.misc import formatLang


class CashDenomination(models.Model):
    """Bancnotele și monedele numărate la monetarul casieriei.

    Aceeași formă ca `pos.bill` din POS (valoare, ordonare după valoare), dar pe monedă,
    ca registrul unei casierii în valută să numere cupiurile acelei valute.
    """

    _name = "l10n.ro.cash.denomination"
    _description = "Cash Denomination"
    _order = "currency_id, value desc"

    value = fields.Float(required=True, digits=(16, 2), aggregator=None)
    kind = fields.Selection([("banknote", "Banknote"), ("coin", "Coin")], required=True, default="banknote")
    currency_id = fields.Many2one("res.currency", required=True, default=lambda self: self.env.company.currency_id)
    active = fields.Boolean(default=True)

    _positive_value = models.Constraint("CHECK(value > 0)", "The value of a denomination must be positive.")
    _unique_value = models.Constraint(
        "unique(currency_id, value, kind)", "This denomination already exists for the currency."
    )

    @api.depends("value", "currency_id")
    def _compute_display_name(self):
        for denomination in self:
            denomination.display_name = formatLang(self.env, denomination.value, currency_obj=denomination.currency_id)
