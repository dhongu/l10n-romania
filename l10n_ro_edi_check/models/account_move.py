# ©  2024-now Dan Stoica <danila(@)terrabit(.)ro
# See README.rst file on addons root folder for license details

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super().action_post()
        errors = []
        for move in self:
            if move.move_type in ["out_invoice", "out_refund"] and move.commercial_partner_id.is_company:
                country_ro = self.env.ref("base.ro")
                partner = move.commercial_partner_id
                if not partner.country_id:
                    errors += [_("Partenerul %s nu are completata tara") % partner.name]
                elif partner.country_id == country_ro:
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


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    l10n_ro_label_length = fields.Integer(string="Desc. length", compute="_compute_label_length")

    @api.onchange("product_id", "name")
    def _compute_label_length(self):
        for line in self:
            if line.name:
                line.l10n_ro_label_length = len(line.name)
            else:
                line.l10n_ro_label_length = 0

    def _get_computed_price_unit(self):
        """
        Do not change unit price if supplier invoice downloaded from ANAF
        :return: price unit
        """
        self.ensure_one()
        if self.move_id.move_type not in ["in_invoice", "in_refund"] or not self.move_id.l10n_ro_edi_download:
            return super()._get_computed_price_unit()
        else:
            return self.price_unit