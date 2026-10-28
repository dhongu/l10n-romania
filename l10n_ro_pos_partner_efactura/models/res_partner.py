# ©  2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import re
import unicodedata

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.l10n_ro_edi.models.account_edi_xml_ubl_ciusro import (
    SECTOR_RO_CODES,
    get_formatted_sector_ro,
)


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

    @api.constrains("street", "city", "state_id", "country_id", "vat", "is_company")
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
        if self.is_company and not self.vat:
            missing.append(self.env._("Tax ID (CUI)"))
        if (
            self.country_id.code == "RO"
            and self.state_id.code == "B"
            and self.city
            and get_formatted_sector_ro(self.city) not in SECTOR_RO_CODES
        ):
            missing.append(self.env._("For Bucharest the city must be the sector, e.g. 'Sector 1'"))
        return missing

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
    def l10n_ro_pos_partner_from_cui(self, config_id, vat):
        """Return the customer with the CUI typed in POS, fetched from ANAF when it is not on file.

        The cashier searched by CUI: a customer on file under it is the right one, whatever its name.
        """
        config = self.env["pos.config"].browse(config_id)
        lookup = self.env["l10n.ro.anaf.partner.lookup"]
        cui = lookup.normalize_cui(vat)
        if not lookup.is_valid_cui(cui):
            raise UserError(self.env._("%(vat)s is not a valid CUI.", vat=vat))
        partner = self.search(
            ["|", ("vat", "=ilike", cui), ("vat", "=ilike", "RO" + cui), ("parent_id", "=", False)],
            limit=1,
        )
        if not partner:
            partner = self._l10n_ro_pos_partner_from_anaf(cui)
        elif not partner.l10n_ro_pos_anaf_to_confirm and partner._get_pos_efactura_missing_data():
            # A customer on file that e-Factura would refuse is checked like a new one
            partner.l10n_ro_pos_anaf_to_confirm = True
        return {
            "res.partner": self._load_pos_data_read(partner, config),
            "account.fiscal.position": self.env["account.fiscal.position"]._load_pos_data_read(
                partner.fiscal_position_id, config
            ),
        }

    @api.model
    def _l10n_ro_pos_partner_from_anaf(self, cui):
        result = self.env["l10n.ro.anaf.partner.lookup"].lookup(cui)
        if result["state"] == "unavailable":
            raise UserError(
                self.env._("ANAF did not answer. Try again in a moment, or add the customer by hand with Create.")
            )
        if result["state"] != "found":
            raise UserError(self.env._("ANAF has no company registered under the CUI %(cui)s.", cui=cui))
        if result["struck_off"]:
            # The company no longer exists: an invoice to it would be refused
            raise UserError(
                self.env._(
                    "ANAF lists the company %(name)s (CUI %(cui)s) as struck off.",
                    name=result["partner"]["name"],
                    cui=cui,
                )
            )
        partner = self.create(dict(result["partner"], l10n_ro_pos_anaf_to_confirm=True))
        if result["inactive"]:
            partner.message_post(
                body=self.env._(
                    "Fetched from ANAF in the Point of Sale. ANAF lists the company as an inactive taxpayer."
                )
            )
        return partner

    def l10n_ro_pos_anaf_confirm(self):
        """Called from POS once the cashier has saved the partner form"""
        self.with_context(pos_efactura_check=True)._check_pos_efactura_data()
        self.l10n_ro_pos_anaf_to_confirm = False
        return True
