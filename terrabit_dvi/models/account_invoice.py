# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.move"

    dvi_id = fields.Many2one("stock.landed.cost", string="DVI")

    def button_dvi(self):
        europe = self.env.ref("base.europe")
        if not self.commercial_partner_id.country_id:
            raise UserError(_("The partner has no country set."))
        if self.commercial_partner_id.country_id in europe.country_ids:
            raise UserError(_("The partner is in UE."))

        if self.dvi_id:
            # afisare DVI
            action = self.env.ref("stock_landed_costs.action_stock_landed_cost")
            action = action.sudo().read()[0]
            action["views"] = [(False, "form")]
            action["res_id"] = self.dvi_id.id
        else:
            # generare dvi
            action = self.env.ref("terrabit_dvi.action_account_invoice_dvi")
            action = action.sudo().read()[0]

        return action
