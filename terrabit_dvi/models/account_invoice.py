# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com>
# See README.rst file on addons root folder for license details


from odoo import fields, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.move"

    dvi_id = fields.Many2one("stock.landed.cost", string="DVI")
    taxare_inversa_move_id = fields.Many2one(
        "account.move",
        string="Taxare inversă IC",
        readonly=True,
        copy=False,
    )

    def _is_intracom_supplier(self):
        """True dacă furnizorul este dintr-o țară UE (alta decât țara companiei)."""
        europe = self.env.ref("base.europe", raise_if_not_found=False)
        if not europe or not self.commercial_partner_id.country_id:
            return False
        return (
            self.commercial_partner_id.country_id in europe.country_ids
            and self.commercial_partner_id.country_id != self.env.company.country_id
        )

    def button_dvi(self):
        if not self.commercial_partner_id.country_id:
            raise UserError(self.env._("The partner has no country set."))

        if self._is_intracom_supplier():
            # Furnizor UE → taxare inversă intracomunitară
            if self.taxare_inversa_move_id:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "account.move",
                    "view_mode": "form",
                    "res_id": self.taxare_inversa_move_id.id,
                    "target": "current",
                }
            action = self.env.ref("terrabit_dvi.action_account_invoice_taxare_inversa")
            action = action.sudo().read()[0]
            return action
        else:
            # Furnizor non-UE → DVI (taxe vamale)
            if self.dvi_id:
                action = self.env.ref("stock_landed_costs.action_stock_landed_cost")
                action = action.sudo().read()[0]
                action["views"] = [(False, "form")]
                action["res_id"] = self.dvi_id.id
            else:
                action = self.env.ref("terrabit_dvi.action_account_invoice_dvi")
                action = action.sudo().read()[0]
            return action
