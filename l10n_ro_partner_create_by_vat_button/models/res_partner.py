# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    def check_vat(self):
        partners = self.filtered(lambda p: not p.vat_subjected)
        return super(ResPartner, partners).check_vat()

    @api.model
    def create(self, vals):
        if "name" in vals:
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
                except Exception:
                    _logger.info("ANAF Webservice not working.")
        if vals.get("state_id") and not isinstance(vals["state_id"], int):
            vals["state_id"] = vals["state_id"].id

        partner = super().create(vals)
        return partner

    def button_get_partner_data(self):
        if self.name and not self.vat:
            self.vat = self.name
        self.ro_vat_change()
        self.onchange_vat_subjected()  # fortare compltare ro
