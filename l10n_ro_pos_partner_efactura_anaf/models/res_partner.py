# ©  2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import re
import unicodedata

from odoo import api, fields, models


def _normalize_city(name):
    """City name without diacritics, case and spaces, as ANAF and res.city spell it differently"""
    name = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode()
    return re.sub(r"[\s\-.]+", "", name).lower()


class ResPartner(models.Model):
    _inherit = "res.partner"

    l10n_ro_pos_anaf_to_confirm = fields.Boolean(
        string="ANAF data to confirm",
        copy=False,
        help="The customer was fetched from ANAF in the Point of Sale and the cashier has not confirmed its data yet.",
    )
    l10n_ro_pos_anaf_warnings = fields.Text(
        string="ANAF data warnings",
        compute="_compute_l10n_ro_pos_anaf_warnings",
    )

    @api.model
    def _load_pos_data_fields(self, config):
        return super()._load_pos_data_fields(config) + ["l10n_ro_pos_anaf_to_confirm"]

    @api.depends("street", "city", "state_id", "country_id", "vat", "is_company", "parent_id", "type")
    def _compute_l10n_ro_pos_anaf_warnings(self):
        for partner in self:
            warnings = partner._get_pos_efactura_missing_data() + partner._get_l10n_ro_anaf_address_warnings()
            partner.l10n_ro_pos_anaf_warnings = "\n".join(f"- {warning}" for warning in warnings) or False

    def _get_l10n_ro_anaf_address_warnings(self):
        """Return the address data ANAF often gets wrong and e-Factura does not catch"""
        self.ensure_one()
        if self.parent_id and self.type == "contact":
            return []
        warnings = []
        if self.street and not re.search(r"\d", self.street):
            warnings.append(self.env._("The street has no number"))
        if (
            self.country_id.code == "RO"
            and self.state_id
            and self.state_id.code != "B"
            and self.city
            and not ("city_id" in self._fields and self.city_id)
            and "res.city" in self.env
        ):
            cities = self.env["res.city"].search([("state_id", "=", self.state_id.id)])
            # Without the list of cities of the county there is nothing to compare with
            if cities and _normalize_city(self.city) not in {_normalize_city(city.name) for city in cities}:
                warnings.append(
                    self.env._(
                        "The city %(city)s is not in the county %(state)s",
                        city=self.city,
                        state=self.state_id.name,
                    )
                )
        return warnings

    @api.model
    def _l10n_ro_pos_partner_from_anaf(self, cui):
        partner = super()._l10n_ro_pos_partner_from_anaf(cui)
        partner.l10n_ro_pos_anaf_to_confirm = True
        return partner

    @api.model
    def l10n_ro_pos_create_partner_from_vat(self, config_id, vat_number):
        result = super().l10n_ro_pos_create_partner_from_vat(config_id, vat_number)
        # A customer already on file that e-Factura would refuse is checked like a new one
        for partner_data in result["res.partner"]:
            partner = self.browse(partner_data["id"])
            if not partner.l10n_ro_pos_anaf_to_confirm and partner._get_pos_efactura_missing_data():
                partner.l10n_ro_pos_anaf_to_confirm = True
            partner_data["l10n_ro_pos_anaf_to_confirm"] = partner.l10n_ro_pos_anaf_to_confirm
        return result

    def l10n_ro_pos_anaf_confirm(self):
        """Called from POS once the cashier has saved the partner form"""
        self.with_context(pos_efactura_check=True)._check_pos_efactura_data()
        self.l10n_ro_pos_anaf_to_confirm = False
        return True
