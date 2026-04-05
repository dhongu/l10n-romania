# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import models
from odoo.exceptions import UserError
from odoo.tools.convert import safe_eval


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        check_storable_line_source = get_param("l10n_ro_stock_account.check_storable_line_source", default="False")
        check_storable_line_source = safe_eval(check_storable_line_source)

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
