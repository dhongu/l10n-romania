from odoo import _, fields, models
from odoo.exceptions import ValidationError


class GetPartnerData(models.TransientModel):
    _name = "get.partner.data"
    _description = "Get partner data from"

    service = fields.Selection(
        [("anaf", "ANAF"), ("vies", "VIES for non-Romanian partners")],
        default="anaf",
        string="Service",
    )
    state = fields.Selection(selection=[("get", "get"), ("set", "set")], default="get")
    status_message = fields.Char()

    def default_get(self, fields):
        res = super().default_get(fields)
        active_ids = self.env.context.get("active_ids", [])
        active_model = self.env.context.get("active_model", "res.partner")
        partner = self.env[active_model].browse(active_ids)
        if partner:
            res["partner_id"] = partner.id
        return res

    partner_id = fields.Many2one("res.partner", string="Partner")

    def do_back(self):
        self.write({"state": "get"})
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "views": [(False, "form")],
            "target": "new",
        }

    def do_get_data(self):
        if self.partner_id.type == "delivery":
            raise ValidationError(_("You can't use this function on delivery contacts."))
        if self.service == "anaf":
            res = self.partner_id.get_partner_data()
            if "warning" in res:
                self.status_message = _("Attention! ") + res["warning"]["message"]
            else:
                self.status_message = _("Partner data updated!")
        if self.service == "vies":
            self.partner_id.get_partner_name_from_vies()
            self.status_message = _("Partner data updated!")
        if self.partner_id.zip and hasattr(self.partner_id, "onchange_zip"):
            self.partner_id.onchange_zip()

        self.state = "set"
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "views": [(False, "form")],
            "target": "new",
        }
