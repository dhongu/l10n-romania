# ©  2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import logging
import re

from markupsafe import Markup, escape

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_date, remove_accents

_logger = logging.getLogger(__name__)

# Marks a suggestion that came from ANAF; it travels back to the server in the
# `entity_type` the autocomplete widget hands over after the partner is saved
ANAF_ENTITY_TYPE = "l10n_ro_anaf"
# The same for a company from another EU country, found in VIES
VIES_ENTITY_TYPE = "l10n_ro_vies"
# VIES may be slow: the check of a Romanian company only adds a line to a note, so it waits less
VIES_STATUS_TIMEOUT = 5

# Kept on refresh when the partner already has one: a local phone is usually the better one
ANAF_FILL_IF_EMPTY = ("phone",)

# Kept on refresh when ANAF leaves them empty and the address is the same (villages without a
# street register): the street is required on an e-Factura invoice
ANAF_KEEP_IF_EMPTY = ("street", "street2", "zip")


class ResPartner(models.Model):
    _inherit = "res.partner"

    # The Romanian VAT fields, with the names and types l10n_ro_config (OCA) and l10n_ro_anaf_partner
    # also declare: the data stays when one of them is installed or removed
    l10n_ro_vat_subjected = fields.Boolean(
        string="VAT Payer",
        help="The partner is registered for VAT purposes (scpTVA). Filled in from ANAF.",
    )
    l10n_ro_vat_number = fields.Char(
        string="VAT Number Digits",
        compute="_compute_l10n_ro_vat_number",
        store=True,
        help="The Tax ID without the country prefix.",
    )

    @api.depends("vat")
    def _compute_l10n_ro_vat_number(self):
        for partner in self:
            partner.l10n_ro_vat_number = re.sub(r"\D", "", partner.vat or "")

    @api.model
    def autocomplete_by_vat(self, vat, query_country_id, timeout=15):
        suggestions = self._l10n_ro_anaf_autocomplete(vat, query_country_id)
        if suggestions is None:
            suggestions = self._l10n_ro_vies_autocomplete(vat)
        if suggestions is None:
            return super().autocomplete_by_vat(vat, query_country_id, timeout=timeout)
        return suggestions

    @api.model
    def autocomplete_by_name(self, query, query_country_id, timeout=15):
        # A CUI without RO does not look like a VAT number to the widget and is searched as a name
        suggestions = self._l10n_ro_anaf_autocomplete(query, query_country_id)
        if suggestions is None:
            suggestions = self._l10n_ro_vies_autocomplete(query)
        if suggestions is None:
            return super().autocomplete_by_name(query, query_country_id, timeout=timeout)
        return suggestions

    @api.model
    def enrich_by_vat(self, vat, timeout=15):
        # The Enrich action (new in 20.0) asks by the Tax ID or by the Company ID (RO_EN): a Romanian
        # CUI is answered by ANAF, without IAP credit. Only the empty fields of the partner are filled
        country = self.country_id if len(self) == 1 else self.env["res.country"]
        result = self._l10n_ro_anaf_lookup(vat, country.id or False)
        if result is None:
            return super().enrich_by_vat(vat, timeout=timeout)
        if result["state"] != "found":
            return {}
        return dict(result["partner"], entity_type=ANAF_ENTITY_TYPE)

    @api.model
    def _l10n_ro_anaf_autocomplete(self, query, query_country_id):
        """Suggestions from ANAF for a Romanian CUI; ``None`` to leave the query to IAP"""
        result = self._l10n_ro_anaf_lookup(query, query_country_id)
        if result is None:
            return None
        if result["state"] != "found":
            return []
        return [self._l10n_ro_anaf_suggestion(result["partner"])]

    @api.model
    def _l10n_ro_anaf_lookup(self, query, query_country_id):
        """The ANAF answer for a Romanian CUI; ``None`` to leave the query to IAP"""
        lookup = self.env["l10n.ro.anaf.partner.lookup"]
        query = (query or "").strip()
        cui = lookup.normalize_cui(query)
        if not lookup.is_valid_cui(cui):
            return None
        # `False` means the country of the company, `0` a worldwide search
        if query_country_id is False:
            query_country_id = self.env.company.country_id.id
        country = self.env["res.country"].browse(query_country_id)
        if not (query.upper().startswith("RO") or country.code == "RO"):
            return None
        result = lookup.lookup(cui)
        if result["state"] == "unavailable":
            # ANAF is down: IAP may still know the company
            return None
        return result

    @api.model
    def _l10n_ro_vies_autocomplete(self, query):
        """The suggestion from VIES for the VAT number of a company from another EU country;
        ``None`` to leave the query to IAP"""
        lookup = self.env["l10n.ro.anaf.partner.lookup"]
        prefix, number = lookup.split_eu_vat((query or "").strip())
        # A Romanian CUI is ANAF's
        if not prefix or prefix == "RO":
            return None
        result = lookup.vies_lookup(prefix + number)
        if result["state"] == "invalid":
            # A name such as "Delta 2000" that only starts like a VAT number
            return None
        # Not in VIES, VIES down, or a member state that keeps the name to itself (Germany, Spain):
        # IAP may still know the company
        if result["state"] != "found" or not result["has_details"]:
            return None
        return [self._l10n_ro_anaf_suggestion(result["partner"], entity_type=VIES_ENTITY_TYPE)]

    @api.model
    def _l10n_ro_anaf_suggestion(self, values, entity_type=ANAF_ENTITY_TYPE):
        """The partner values in the shape of an IAP suggestion"""
        suggestion = dict(values, entity_type=entity_type, duns=False)
        # city_id only where base_address_extended adds it (with the cities of l10n_ro_city)
        for field_name in ("country_id", "state_id", "city_id"):
            if field_name not in values:
                continue
            record = self.env[self._fields[field_name].comodel_name].browse(values[field_name])
            suggestion[field_name] = {"id": record.id, "display_name": record.display_name} if record else False
        return suggestion

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        """The VAT payer box once on the partner form: this module shows it with the Tax ID, and
        l10n_ro_config (OCA) adds one more under the trade register number"""
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == "form":
            for node in arch.xpath("//div[@name='l10n_ro_vat_subjected_info'] | //label[@for='l10n_ro_vat_subjected']"):
                node.getparent().remove(node)
        return arch, view

    def onchange(self, values, field_names, fields_spec):
        """Choosing the city of a Romanian partner keeps the postal code it already has, and a city
        set together with its postal code (the ANAF data) is not replaced from that postal code.

        base_address_extended replaces the postal code with the city's, which for a town is empty
        or a generic one: the street postal code from ANAF, or one typed in, would be lost.
        l10n_ro_city picks the Bucharest sector from the postal code, and ANAF sometimes gives a
        postal code of another sector than the address.
        """
        result = super().onchange(values, field_names, fields_spec)
        changed = result.get("value") or {}
        if "city_id" not in field_names or not changed or self._l10n_ro_onchange_country(values) != "RO":
            return result
        if values.get("zip") and "zip" in changed and changed["zip"] != values["zip"]:
            changed.pop("zip")
        city = values.get("city_id")
        city_id = city.get("id") if isinstance(city, dict) else city
        if city_id and "zip" in field_names and "city_id" in changed:
            new = changed["city_id"]
            if (new.get("id") if isinstance(new, dict) else new) != city_id:
                changed.pop("city_id")
                changed.pop("city", None)
        return result

    @api.model
    def _l10n_ro_onchange_country(self, values):
        country = values.get("country_id")
        country_id = country.get("id") if isinstance(country, dict) else country
        return self.env["res.country"].browse(country_id).code

    @api.model
    def enrich_by_duns(self, duns, timeout=15):
        # The ANAF suggestion is already complete: no enrichment, so no IAP credit
        company = self.env.context.get("enriched_company_data") or {}
        if company.get("entity_type") in (ANAF_ENTITY_TYPE, VIES_ENTITY_TYPE):
            return dict(company)
        return super().enrich_by_duns(duns, timeout=timeout)

    def enrich_company_message_post(self, data):
        entity_type = data.get("entity_type")
        if entity_type not in (ANAF_ENTITY_TYPE, VIES_ENTITY_TYPE):
            return super().enrich_company_message_post(data)
        for partner in self:
            date = format_date(partner.env, fields.Date.context_today(partner))
            if entity_type == VIES_ENTITY_TYPE:
                partner._l10n_ro_set_vies_valid(True)
                body = escape(self.env._("Company data taken from VIES on %(date)s.", date=date))
            else:
                body = escape(self.env._("Company data taken from ANAF on %(date)s.", date=date))
                body += partner._l10n_ro_vies_status_line()
            partner.message_post(body=body, subtype_xmlid="mail.mt_note")

    # ------------------------------------------------------------------
    # VIES status
    # ------------------------------------------------------------------

    def _l10n_ro_vies_status_line(self, result=None):
        """A paragraph saying whether the VAT number of the partner is in VIES, for a note.

        A Romanian company is in VIES only when registered for VAT (art. 316 of the Fiscal Code); a
        company that is not a VAT payer is not asked about.
        """
        self.ensure_one()
        lookup = self.env["l10n.ro.anaf.partner.lookup"]
        vat = self.vat or ""
        if self.country_id.code == "RO":
            # The VAT payer box, not the RO prefix: l10n_ro_config writes the prefix on its own
            if not self.l10n_ro_vat_subjected:
                return Markup("")
            vat = "RO" + lookup.normalize_cui(vat)
        if not lookup.split_eu_vat(vat)[0]:
            return Markup("")
        if result is None:
            result = lookup.vies_lookup(vat, timeout=VIES_STATUS_TIMEOUT)
        if result["state"] == "found":
            line = self.env._("VIES: valid for intra-community operations.")
        elif result["state"] == "not_found":
            line = self.env._("VIES: not registered for intra-community operations.")
        else:
            line = self.env._("VIES did not answer: the intra-community status was not checked.")
        return Markup("<p>%s</p>") % line

    def _l10n_ro_set_vies_valid(self, valid):
        """``Intra-Community Valid`` (base_vat) from the VIES answer, for a partner from another EU
        country: the fiscal position of intra-community supplies is chosen from it"""
        if "vies_valid" not in self._fields:
            return
        partners = self.filtered(lambda p: p.country_id.code != "RO" and p.vies_valid != valid)
        if partners:
            partners.vies_valid = valid

    # ------------------------------------------------------------------
    # Update an existing partner from ANAF
    # ------------------------------------------------------------------

    def action_l10n_ro_anaf_refresh(self):
        lookup = self.env["l10n.ro.anaf.partner.lookup"]
        for partner in self:
            result = lookup.lookup(partner.vat or "")
            if result["state"] == "invalid":
                raise UserError(self.env._("%(vat)s is not a valid CUI.", vat=partner.vat or ""))
            if result["state"] == "unavailable":
                raise UserError(self.env._("ANAF did not answer. Try again in a moment."))
            if result["state"] != "found":
                raise UserError(self.env._("ANAF has no company registered under %(vat)s.", vat=partner.vat))
            same_address = partner._l10n_ro_anaf_same_address(result["partner"])
            values = {
                name: value
                for name, value in result["partner"].items()
                if name in partner._fields
                and not (
                    partner[name]
                    and (name in ANAF_FILL_IF_EMPTY or (not value and same_address and name in ANAF_KEEP_IF_EMPTY))
                )
            }
            changes = partner._l10n_ro_anaf_changes(values)
            partner.write(values)
            partner._l10n_ro_anaf_post_refresh(changes, result)
        return True

    def _l10n_ro_anaf_same_address(self, values):
        """ANAF gives the partner's city and county, and no other street: the partner's address
        details still belong there.

        In another locality, or next to a new street, the old street details and postal code would
        make an address that does not exist, so they are cleared as ANAF has them. A partner without
        a county matches on the city.
        """
        self.ensure_one()

        def normalized(text):
            return remove_accents(text or "").strip().casefold()

        if self.state_id and self.state_id.id != values.get("state_id"):
            return False
        if values.get("street") and normalized(values["street"]) != normalized(self.street):
            return False
        return bool(self.city) and normalized(self.city) == normalized(values.get("city"))

    def _l10n_ro_anaf_changes(self, values):
        """``[(label, old, new)]`` for the values that differ from the partner's"""
        self.ensure_one()
        changes = []
        for name, value in values.items():
            field = self._fields[name]
            old = self[name]
            if field.type == "many2one":
                new = self.env[field.comodel_name].browse(value)
                if old == new:
                    continue
                old, new = old.display_name, new.display_name
            elif (old or False) == (value or False):
                continue
            elif field.type == "boolean":
                old, new = (self.env._("Yes") if flag else self.env._("No") for flag in (old, value))
            else:
                new = value
            changes.append((field._description_string(self.env), old or "", new or ""))
        return changes

    def _l10n_ro_anaf_post_refresh(self, changes, result):
        self.ensure_one()
        if changes:
            lines = Markup("").join(Markup("<li>%s: %s → %s</li>") % (label, old, new) for label, old, new in changes)
            body = Markup("%s<ul>%s</ul>") % (self.env._("Updated from ANAF:"), lines)
        else:
            body = escape(self.env._("Checked against ANAF: no change."))
        status = []
        if result.get("struck_off"):
            status.append(self.env._("ANAF lists the company as struck off."))
        if result.get("inactive"):
            status.append(self.env._("ANAF lists the company as an inactive taxpayer."))
        for line in status:
            body += Markup("<p><b>%s</b></p>") % line
        body += self._l10n_ro_vies_status_line()
        self.message_post(body=body, subtype_xmlid="mail.mt_note")

    def action_l10n_ro_vies_refresh(self):
        """Update a company from another EU country from VIES: the name and the address when the
        member state shares them, and ``Intra-Community Valid``"""
        lookup = self.env["l10n.ro.anaf.partner.lookup"]
        for partner in self:
            result = lookup.vies_lookup(partner.vat or "")
            if result["state"] == "invalid":
                raise UserError(self.env._("%(vat)s is not a VAT number of an EU country.", vat=partner.vat or ""))
            if result["state"] == "unavailable":
                raise UserError(self.env._("VIES did not answer. Try again in a moment."))
            if result["state"] == "found":
                # Only what VIES knows: a member state that keeps the address does not erase the partner's
                values = {
                    name: value
                    for name, value in result["partner"].items()
                    if name in partner._fields and value and name not in ("vat", "is_company")
                }
                changes = partner._l10n_ro_anaf_changes(values)
                partner.write(values)
            else:
                changes = []
            partner._l10n_ro_set_vies_valid(result["state"] == "found")
            if changes:
                lines = Markup("").join(
                    Markup("<li>%s: %s → %s</li>") % (label, old, new) for label, old, new in changes
                )
                body = Markup("%s<ul>%s</ul>") % (self.env._("Updated from VIES:"), lines)
            else:
                body = escape(self.env._("Checked against VIES: no change."))
            body += partner._l10n_ro_vies_status_line(result)
            partner.message_post(body=body, subtype_xmlid="mail.mt_note")
        return True

    # ------------------------------------------------------------------
    # A partner created with its CUI as the name (quick create, import, API)
    # ------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get("l10n_ro_anaf_no_autofill"):
            for vals in vals_list:
                vals.update(self._l10n_ro_anaf_autofill_values(vals))
        return super().create(vals_list)

    @api.model
    def _l10n_ro_anaf_autofill_values(self, vals):
        """The ANAF data for a partner whose name is a Romanian CUI; ``{}`` otherwise"""
        name = (vals.get("name") or "").strip()
        if not name or vals.get("parent_id"):
            return {}
        lookup = self.env["l10n.ro.anaf.partner.lookup"]
        # A name holding anything but digits after an optional RO is not a CUI
        cui = lookup.normalize_cui(name)
        if not lookup.is_valid_cui(cui):
            return {}
        # A Tax ID given with the partner wins, unless it is this same CUI: that one is derived from
        # the name (l10n_ro_partner_create_by_vat_button writes it before this override runs)
        if vals.get("vat") and lookup.normalize_cui(vals["vat"]) != cui:
            return {}
        country = self.env["res.country"].browse(vals.get("country_id"))
        if country and country.code != "RO":
            return {}
        result = lookup.lookup(cui)
        if result["state"] != "found":
            _logger.info("ANAF: no data for the new partner %s (%s)", name, result["state"])
            return {}
        # What the caller set explicitly wins, except the name and the Tax ID, which were the CUI
        return {
            key: value
            for key, value in result["partner"].items()
            if key in self._fields and (key in ("name", "vat") or not vals.get(key))
        }
