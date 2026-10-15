# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        check_storable_line_source = (
            self.env["ir.config_parameter"].sudo().get_bool("l10n_ro_stock_account.check_storable_line_source")
        )

        if check_storable_line_source:
            for move in self:
                if move.move_type in ["out_invoice", "out_refund", "in_invoice", "in_refund"]:
                    for line in move.invoice_line_ids:
                        if line.product_id.is_storable:
                            if move.move_type in ["out_invoice", "out_refund"] and not line.sale_line_ids:
                                raise UserError(
                                    self.env._(
                                        "Invoice line with storable product '%s' must have a reference to a sales order line.",
                                        line.product_id.display_name,
                                    )
                                )
                            if move.move_type in ["in_invoice", "in_refund"] and not line.purchase_line_id:
                                raise UserError(
                                    self.env._(
                                        "Invoice line with storable product '%s' must have a reference to a purchase order line.",
                                        line.product_id.display_name,
                                    )
                                )
        return super().action_post()
