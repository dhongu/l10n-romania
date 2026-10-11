# Copyright (C) 2020 NextERP Romania
# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.exceptions import ValidationError


class L10nRoGetPartnerData(models.TransientModel):
    _name = "l10n.ro.get.partner.data"
    _description = "Get partner data from ANAF / VIES"

    partner_id = fields.Many2one("res.partner", string="Partner", readonly=True)
    service = fields.Selection(
        [("anaf", "ANAF"), ("vies", "VIES for non-Romanian partners")],
        default="anaf",
    )
    state = fields.Selection([("get", "get"), ("set", "set")], default="get")
    status_message = fields.Html()

    def default_get(self, field_list):
        res = super().default_get(field_list)
        if self.env.context.get("active_model") == "res.partner":
            partner = self.env["res.partner"].browse(self.env.context.get("active_ids", [])[:1])
            if partner:
                res["partner_id"] = partner.id
        return res

    def _reopen(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
            "views": [(False, "form")],
            "target": "new",
        }

    def do_back(self):
        self.write({"state": "get"})
        return self._reopen()

    def do_get_data(self):
        self.ensure_one()
        if self.partner_id.type == "delivery":
            raise ValidationError(self.env._("You can't use this function on delivery contacts."))
        if self.service == "anaf":
            res = self.partner_id.l10n_ro_get_anaf_data()
            if res and "warning" in res:
                self.status_message = self.env._("Attention! ") + res["warning"]["message"]
            else:
                self.status_message = self.env._("Partner data updated!")
        else:
            self.partner_id.l10n_ro_get_name_from_vies()
            self.status_message = self.env._(
                "Partner data updated! Please check the address fields. VIES does "
                "not return the addresses in a consistent form or complete so it "
                "can not be split automatically."
            )
        if self.partner_id.zip and hasattr(self.partner_id, "onchange_zip"):
            self.partner_id.onchange_zip()
        self.state = "set"
        return self._reopen()
