# ©  2024-now Dan Stoica <danila(@)terrabit(.)ro
# See README.rst file on addons root folder for license details

from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super().action_post()
        errors = []
        for move in self:
            if move.move_type in ["out_invoice", "out_refund"] and move.commercial_partner_id.is_company:
                partner = move.commercial_partner_id
                if not partner.country_id:
                    errors += [_("Partenerul %s nu are completata tara") % partner.name]

                if not partner.street:
                    errors += [_("Partenerul %s nu are completata strada") % partner.name]

                if not partner.city:
                    errors += [_("Partenerul %s nu are completata localitatea") % partner.name]

                state_bucuresti = self.env.ref("base.RO_B")
                if partner.state_id == state_bucuresti and partner.city:
                    if "sector" not in partner.city.lower():
                        errors += [_("localitatea pertenerului %s trebuie sa fie de forma SectorX ") % partner.name]
                if errors:
                    errors_text = "\n".join(errors)
                    raise UserError(errors_text)
        return res
