# ©  2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, models
from odoo.exceptions import ValidationError

from odoo.addons.l10n_ro_edi.models.account_edi_xml_ubl_ciusro import (
    SECTOR_RO_CODES,
    get_formatted_sector_ro,
)


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.constrains("street", "city", "state_id", "country_id", "parent_id", "type")
    def _check_pos_efactura_data(self):
        if not self.env.context.get("pos_efactura_check"):
            return
        for partner in self:
            missing = partner._get_pos_efactura_missing_data()
            if missing:
                raise ValidationError(
                    self.env._(
                        "The partner %(partner)s cannot receive an e-Factura invoice:\n- %(missing)s\n"
                        "If the data could not be fetched from ANAF, fill it in manually.",
                        partner=partner.display_name,
                        missing="\n- ".join(missing),
                    )
                )

    def _get_pos_efactura_missing_data(self):
        """Return the e-Factura (CIUS-RO) problems of the partner's invoicing data"""
        self.ensure_one()
        # The address of a contact person is synced from its company
        if self.parent_id and self.type == "contact":
            return []
        missing = []
        if not self.street:
            missing.append(self.env._("Street"))
        if not self.city:
            missing.append(self.env._("City"))
        if not self.state_id:
            missing.append(self.env._("State (county)"))
        if not self.country_id:
            missing.append(self.env._("Country"))
        if (
            self.country_id.code == "RO"
            and self.state_id.code == "B"
            and self.city
            and get_formatted_sector_ro(self.city) not in SECTOR_RO_CODES
        ):
            missing.append(self.env._("For Bucharest the city must be the sector, e.g. 'Sector 1'"))
        return missing
