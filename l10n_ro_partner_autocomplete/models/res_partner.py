# ©  2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import logging

from markupsafe import Markup, escape

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_date

_logger = logging.getLogger(__name__)

# Marks a suggestion that came from ANAF; it travels back to the server in the
# `entity_type` the autocomplete widget hands over after the partner is saved
ANAF_ENTITY_TYPE = "l10n_ro_anaf"

# Kept on refresh when the partner already has one: a local phone is usually the better one
ANAF_FILL_IF_EMPTY = ("phone",)


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def autocomplete_by_vat(self, vat, query_country_id, timeout=15):
        suggestions = self._l10n_ro_anaf_autocomplete(vat, query_country_id)
        if suggestions is None:
            return super().autocomplete_by_vat(vat, query_country_id, timeout=timeout)
        return suggestions

    @api.model
    def autocomplete_by_name(self, query, query_country_id, timeout=15):
        # A CUI without RO does not look like a VAT number to the widget and is searched as a name
        suggestions = self._l10n_ro_anaf_autocomplete(query, query_country_id)
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
    def _l10n_ro_anaf_suggestion(self, values):
        """The partner values in the shape of an IAP suggestion"""
        suggestion = dict(values, entity_type=ANAF_ENTITY_TYPE, duns=False)
        # city_id only where base_address_extended adds it (with the cities of l10n_ro_city)
        for field_name in ("country_id", "state_id", "city_id"):
            if field_name not in values:
                continue
            record = self.env[self._fields[field_name].comodel_name].browse(values[field_name])
            suggestion[field_name] = {"id": record.id, "display_name": record.display_name} if record else False
        return suggestion

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
        if company.get("entity_type") == ANAF_ENTITY_TYPE:
            return dict(company)
        return super().enrich_by_duns(duns, timeout=timeout)

    def enrich_company_message_post(self, data):
        if data.get("entity_type") != ANAF_ENTITY_TYPE:
            return super().enrich_company_message_post(data)
        for partner in self:
            partner.message_post(
                body=self.env._(
                    "Company data taken from ANAF on %(date)s.",
                    date=format_date(partner.env, fields.Date.context_today(partner)),
                ),
                subtype_xmlid="mail.mt_note",
            )

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
            values = {
                name: value
                for name, value in result["partner"].items()
                if name in partner._fields and not (name in ANAF_FILL_IF_EMPTY and partner[name])
            }
            changes = partner._l10n_ro_anaf_changes(values)
            partner.write(values)
            partner._l10n_ro_anaf_post_refresh(changes, result)
        return True

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
        self.message_post(body=body, subtype_xmlid="mail.mt_note")

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
