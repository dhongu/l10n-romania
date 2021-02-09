# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import _, fields, models
from odoo.exceptions import UserError


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
