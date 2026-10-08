# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError


class CashRegisterCountLine(models.Model):
    """Un rând al monetarului: câte bucăți dintr-o cupiură s-au numărat în casă."""

    _name = "l10n.ro.cash.register.count.line"
    _description = "Cash Register Count Line"
    _order = "register_id, kind, value desc"

    register_id = fields.Many2one("l10n.ro.cash.register", required=True, ondelete="cascade", index=True)
    denomination_id = fields.Many2one("l10n.ro.cash.denomination", required=True, ondelete="restrict")
    value = fields.Float(related="denomination_id.value", store=True)
    kind = fields.Selection(related="denomination_id.kind", store=True)
    currency_id = fields.Many2one(related="register_id.currency_id")
    quantity = fields.Integer()
    amount = fields.Monetary(compute="_compute_amount", store=True)

    _unique_denomination = models.Constraint(
        "unique(register_id, denomination_id)", "A denomination is counted only once per cash register."
    )
    _positive_quantity = models.Constraint("CHECK(quantity >= 0)", "The counted quantity cannot be negative.")

    @api.depends("quantity", "value")
    def _compute_amount(self):
        for line in self:
            line.amount = line.quantity * line.value

    def _check_register_open(self, registers):
        # Monetarul unei zile închise este documentul semnat la închidere: nu se mai modifică.
        if registers.filtered(lambda r: r.state == "closed"):
            raise UserError(self.env._("The cash count of a closed day cannot be changed; reopen the day first."))

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        self._check_register_open(lines.register_id)
        return lines

    def write(self, vals):
        self._check_register_open(self.register_id)
        res = super().write(vals)
        self._check_register_open(self.register_id)
        return res

    def unlink(self):
        self._check_register_open(self.register_id)
        return super().unlink()
