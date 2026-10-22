# ©  2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models

# Marks a suggestion that came from ANAF; it travels back to the server in the
# `entity_type` the autocomplete widget hands over after the partner is saved
ANAF_ENTITY_TYPE = "l10n_ro_anaf"


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
    def _l10n_ro_anaf_autocomplete(self, query, query_country_id):
        """Suggestions from ANAF for a Romanian CUI; ``None`` to leave the query to IAP"""
        lookup = self.env["l10n.ro.anaf.lookup"]
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
        if result["state"] != "found":
            return []
        return [self._l10n_ro_anaf_suggestion(result["partner"])]

    @api.model
    def _l10n_ro_anaf_suggestion(self, values):
        """The partner values in the shape of an IAP suggestion"""
        suggestion = dict(values, entity_type=ANAF_ENTITY_TYPE, duns=False)
        for field_name in ("country_id", "state_id"):
            record = self.env[self._fields[field_name].comodel_name].browse(values.get(field_name))
            suggestion[field_name] = {"id": record.id, "display_name": record.display_name} if record else False
        return suggestion

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
                    date=fields.Date.to_string(fields.Date.context_today(partner)),
                ),
                subtype_xmlid="mail.mt_note",
            )
