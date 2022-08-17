# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def create(self, vals):
        if "name" in vals:
            vat_number = vals["name"].lower().strip()
            if "ro" in vat_number:
                vat_number = vat_number.replace("ro", "")
            if vat_number.isdigit():
                try:
                    vals["vat"] = vals["name"]
                    error, result = self._get_Anaf(vat_number)
                    if result:
                        res = self._Anaf_to_Odoo(result)
                        vals.update(res)
                except Exception:
                    _logger.info("ANAF Webservice not working.")
        if vals.get("state_id") and not isinstance(vals["state_id"], int):
            vals["state_id"] = vals["state_id"].id

        partner = super(ResPartner, self).create(vals)
        partner._compute_same_vat_partner_id()
        return partner

    def button_get_partner_data(self):
        if self.name and not self.vat:
            self.vat = self.name
        self.ro_vat_change()
        self._compute_same_vat_partner_id()
