# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


import logging

from odoo import _, api, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.constrains("vat", "country_id")
    def check_vat(self):
        if self.env.context.get("no_vat_validation"):
            return
        partners = self.filtered(lambda p: p.country_id.code != "RO")
        return super(ResPartner, partners).check_vat()

    @api.model
    def create(self, vals):
        if "name" in vals and vals["name"]:
            vat_number = vals["name"].lower().strip()
            if "ro" in vat_number:
                vat_number = vat_number.replace("ro", "")
                if vat_number.isdigit():
                    try:
                        vals["vat"] = vals["name"]
                        result = self._get_Anaf(vat_number)
                        if result:
                            res = self._Anaf_to_Odoo(result)
                            vals.update(res)
                    except Exception as e:
                        _logger.info("ANAF Webservice not working. Exception: % s" % e)

        if vals.get("state_id") and not isinstance(vals["state_id"], int):
            vals["state_id"] = vals["state_id"].id

        partner = super().create(vals)
        return partner

    def button_get_partner_data(self):
        if self.country_id and self.country_id.code != "RO":
            return False
        if self.name and not self.vat:
            self.vat = self.name
        res = self.with_context(skip_ro_vat_change=False).ro_vat_change()
        if "warning" in res:
            raise ValidationError(_("ANAF Webservice not working.\nPlease try again until it works."))
        # self.onchange_vat_subjected()  # fortare compltare ro

    @api.onchange("vat", "country_id")
    def ro_vat_change(self):
        skip_ro_vat_change = self.env.context.get("skip_ro_vat_change", True)
        return super(ResPartner, self.with_context(skip_ro_vat_change=skip_ro_vat_change)).ro_vat_change()
