# Copyright (C) 2024 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    def _l10n_ro_can_use_invoice_line_account(self, account):
        self.ensure_one()
        res = super()._l10n_ro_can_use_invoice_line_account(account)
        if not res:
            return res

        # A dropship stock.move carries both a purchase_line_id and a sale_line_id,
        # so action_post() on either the vendor bill or the customer invoice can end
        # up linking l10n_ro_invoice_line_id to BOTH of its valuation layers (reception
        # and delivery), whichever invoice posts first. Reusing that invoice line's
        # account here would then put the reception (incoming) side on a sale account,
        # or the delivery (outgoing) side on a purchase account.
        move_type = self.l10n_ro_invoice_line_id.move_id.move_type
        if self.l10n_ro_valued_type in ("reception", "reception_return"):
            return move_type in ("in_invoice", "in_refund")
        if self.l10n_ro_valued_type in ("delivery", "delivery_return"):
            return move_type in ("out_invoice", "out_refund")
        return res
