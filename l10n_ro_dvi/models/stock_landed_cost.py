# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

from collections import defaultdict

from odoo.tools.float_utils import float_is_zero


class LandedCost(models.Model):
    _inherit = "stock.landed.cost"

    landed_type = fields.Selection(
        [("standard", "Standard"), ("dvi", "DVI")], default="standard"
    )

    tax_value = fields.Float("VAT paid at customs")
    tax_id = fields.Many2one("account.tax")  # TVA platit in Vama

    def button_validate(self):
        res = super(LandedCost, self).button_validate()
        get_param = self.env["ir.config_parameter"].sudo().get_param

        product_id = get_param("dvi.custom_duty_product_id")

        custom_duty_product = (
            self.env["product.product"].browse(int(product_id)).exists()
        )

        if not custom_duty_product:
            wizard = self.env['account.invoice.dvi'].create({})
            vals = wizard._prepare_custom_duty_product()
            custom_duty_product = self.env["product.product"].create(vals)
            set_param = self.env["ir.config_parameter"].sudo().set_param
            set_param("dvi.custom_duty_product_id", custom_duty_product.id)

        for cost in self.filtered(lambda c: c.tax_value and c.tax_id):

            accounts_data = custom_duty_product.product_tmpl_id.get_product_accounts()
            tax_values = cost.tax_id.compute_all(1)
            aml = [
                {
                    "name": _("VAT paid at customs"),
                    "debit": cost.tax_value,
                    "credit": 0.0,
                    "account_id": tax_values["taxes"][0]["account_id"],
                    "move_id": cost.account_move_id.id,
                },
                {
                    "name": _("VAT paid at customs"),
                    "debit": 0.0,
                    "credit": cost.tax_value,
                    "account_id": accounts_data["expense"].id,
                    "move_id": cost.account_move_id.id,
                },
            ]
            self.env["account.move.line"].create(aml)
        return res

    def _check_sum(self):
        res = super(LandedCost, self)._check_sum()
        if not res:
            # prec_digits = self.env.company.currency_id.decimal_places
            for landed_cost in self:
                total_amount = sum(landed_cost.valuation_adjustment_lines.mapped('additional_landed_cost'))
                if abs(total_amount - landed_cost.amount_total) > 1:
                    return False

            res = True

                # val_to_cost_lines = defaultdict(lambda: 0.0)
                # for val_line in landed_cost.valuation_adjustment_lines:
                #     val_to_cost_lines[val_line.cost_line_id] += val_line.additional_landed_cost
                # if any(not tools.float_is_zero(cost_line.price_unit - val_amount, precision_digits=prec_digits)
                #        for cost_line, val_amount in val_to_cost_lines.items()):
                #     return False
        return res
