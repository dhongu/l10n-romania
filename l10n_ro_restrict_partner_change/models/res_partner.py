# ©  2025-now Terrabit
# See README.rst file on addons root folder for license details


from odoo import _, api, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.onchange("name", "is_company", "vat")
    def check_invoices(self):
        for partner in self:
            if self.env.user.has_group("l10n_ro_restrict_partner_change.group_change_partner"):
                return
            elif not partner.invoice_ids:
                return
            else:
                for invoice in partner.invoice_ids:
                    if invoice.l10n_ro_edi_document_ids:
                        can_change_group = self.env.ref("l10n_ro_restrict_partner_change.group_change_partner")
                        users_in_group = can_change_group.users.mapped("name")
                        if users_in_group:
                            users = ", ".join(users_in_group)
                        else:
                            users = _("Niciun utilizator")
                        raise UserError(
                            "Acest partener are facturi trimise in SPV. Rugati un utilizator cu drepturi sa modifice acest partener\n"
                            + users
                            + " pot modifica acest partener"
                        )
