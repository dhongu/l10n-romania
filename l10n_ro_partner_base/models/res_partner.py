# Copyright (C) 2015 Forest and Biomass Romania
# Copyright (C) 2020 NextERP Romania
# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import re

import requests

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

# ANAF returns the old "cedilla" diacritics; normalize them to the comma forms.
CEDILLA_FIX = str.maketrans("şţŞŢ", "șțȘȚ")

# https://static.anaf.ro/static/10/Anaf/Informatii_R/Servicii_web/doc_WS_V9.txt
ANAF_URL = "https://webservicesp.anaf.ro/api/PlatitorTvaRest/v9/tva"
ANAF_TIMEOUT = 30
ANAF_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MSIE 7.01; Windows NT 5.0)",
    "Content-Type": "application/json;",
}

# (odoo field, key in the flattened ANAF result, write policy)
ANAF_FIELDS = [
    ("vat", "vat", "always"),
    ("nrc", "nrRegCom", "always"),
    ("street", "street", "always"),
    ("street2", "street2", "always"),
    ("city", "city", "always"),
    ("city_id", "city_id", "always"),
    ("state_id", "state_id", "always"),
    ("zip", "codPostal", "if_value"),
    ("phone", "telefon", "if_empty"),
]

UNIQUE_PARAM = "l10n_ro_partner_unique.vat_nrc_unique"
UNIQUE_MODES = ("off", "vat", "vat_nrc")
RO_CUI_RE = re.compile(r"^(?:[Rr][Oo]\s*)?(\d{2,10})$")
EU_VAT_RE = re.compile(r"^([A-Za-z]{2})\s*(\d{4,15})$")


class ResPartner(models.Model):
    _inherit = "res.partner"

    l10n_ro_vat_subjected = fields.Boolean(string="Romania - VAT Subjected")
    l10n_ro_vat_number = fields.Char(
        string="Romania - VAT number digits",
        compute="_compute_l10n_ro_vat_number",
        store=True,
        help="VAT number without country code.",
    )
    l10n_ro_partner_warning = fields.Text(string="Romania - Warning", compute="_compute_l10n_ro_partner_warning")

    @api.depends("vat")
    def _compute_l10n_ro_vat_number(self):
        for partner in self:
            number = ""
            if partner.vat:
                number = self._split_vat(partner.vat)[1]
            partner.l10n_ro_vat_number = number

    @api.depends("vat", "country_id", "street", "city", "state_id", "zip")
    def _compute_l10n_ro_partner_warning(self):
        for partner in self:
            partner.l10n_ro_partner_warning = False
            if partner.country_id.code != "RO":
                continue
            missing = []
            if not partner.vat and partner.is_company:
                missing.append(self.env._("VAT"))
            if not partner.street:
                missing.append(self.env._("Street"))
            if not partner.city:
                missing.append(self.env._("City"))
            if not partner.state_id:
                missing.append(self.env._("State"))
            if not partner.zip:
                missing.append(self.env._("ZIP"))
            if missing:
                partner.l10n_ro_partner_warning = self.env._("Missing: ") + ", ".join(missing)

    # ------------------------------------------------------------------
    # CUI / VAT handling
    # ------------------------------------------------------------------
    def _l10n_ro_map_vat_country_code(self, country_code):
        return {"RE": "FR", "GP": "FR", "MQ": "FR", "GF": "FR", "EL": "GR"}.get(country_code, country_code)

    def _split_vat(self, vat):
        """Accept the Romanian CUI without the "RO" prefix.

        The country is taken from the record itself, never from a database
        lookup (the record is already stored when the check runs)."""
        vat_country, vat_number = super()._split_vat(vat)
        if vat_country or not vat or not vat.isdigit():
            return vat_country, vat_number
        country_code = self.country_id.code if len(self) == 1 else False
        if country_code and self._l10n_ro_map_vat_country_code(country_code.upper()) == "RO":
            vat_country = "RO"
        return vat_country, vat_number

    def _get_ro_vat(self):
        """RO prefix only for VAT payers; plain digits for the others."""
        self.ensure_one()
        vat = self.vat
        if vat and self.country_id.code == "RO":
            if self.l10n_ro_vat_subjected and vat.isdigit():
                vat = "RO" + vat
            elif not self.l10n_ro_vat_subjected and not vat.isdigit():
                vat = self._split_vat(vat)[1]
        return vat

    @api.constrains("vat", "country_id")
    def _check_vat(self, validation="error"):
        """Romanian partners are not validated by the generic VAT check; the
        prefix is set from ``l10n_ro_vat_subjected`` instead."""
        if self.env.context.get("no_vat_validation"):
            return
        ro_partners = self.filtered(lambda p: p.country_id.code == "RO")
        super(ResPartner, self - ro_partners)._check_vat(validation)
        for partner in ro_partners:
            ro_vat = partner._get_ro_vat()
            if partner.vat != ro_vat:
                partner.vat = ro_vat

    # ------------------------------------------------------------------
    # ANAF
    # ------------------------------------------------------------------
    @api.model
    def _l10n_ro_anaf_request(self, cui, check_date=False):
        """Query the ANAF VAT payer web service (v9) for one CUI.

        :param str cui: VAT number without country code
        :return: tuple (error message, ANAF result dict)
        """
        get_param = self.env["ir.config_parameter"].sudo().get_param
        url = get_param("l10n_ro_partner_base.anaf_url", ANAF_URL)
        if not check_date:
            check_date = fields.Date.to_string(fields.Date.today())
        payload = [{"cui": int(cui), "data": check_date}]
        try:
            response = requests.post(url, json=payload, headers=ANAF_HEADERS, timeout=ANAF_TIMEOUT)
        except Exception as ex:  # noqa: BLE001 - any network failure
            return (
                self.env._(
                    "ANAF Webservice not working. Exception raised: %(error)s",
                    error=ex,
                ),
                {},
            )
        if response.status_code != 200 or response.headers.get("content-type") != "application/json":
            return (
                self.env._(
                    "Anaf request error: \nresponse=%(response)s \nreason=%(reason)s \ntext=%(text)s",
                    response=response,
                    reason=response.reason,
                    text=response.text,
                ),
                {},
            )
        found = response.json().get("found") or []
        result = found[0] if found and found[0] else {}
        if not result.get("date_generale"):
            return (
                self.env._("Anaf didn't find any company with VAT=%(vat)s !", vat=cui),
                {},
            )
        return "", result

    @api.model
    def _l10n_ro_anaf_address(self, data):
        """Street, city, state and zip from the fiscal domicile of ANAF."""

        def clean(text):
            return (text or "").translate(CEDILLA_FIX).strip()

        def city_name(text):
            city = text.replace(".", "").upper()
            if "SECTOR" in city and "MUN" in city:
                city = city.split("MUN")[0]
            for tag in ("MUNICIPIUL", "MUN", "ORȘ", "JUD"):
                city = city.replace(tag, "")
            return city.strip().title()

        street = clean(data.get("ddenumire_Strada"))
        number = clean(data.get("dnumar_Strada"))
        if number:
            street += " Nr. " + number
        street = street.strip().title()
        street2 = clean(data.get("ddetalii_Adresa")).title()
        if not street and street2:
            street, street2 = street2, ""
        state = self.env["res.country.state"]
        state_code = data.get("dcod_JudetAuto")
        if state_code:
            state = state.search(
                [
                    ("code", "=", state_code),
                    ("country_id", "=", self.env.ref("base.ro").id),
                ],
                limit=1,
            )
        state_name = city_name(clean(data.get("ddenumire_Judet")))
        if not state and state_name:
            state = state.search([("name", "=", state_name)], limit=1)
        return {
            "street": street,
            "street2": street2,
            "zip": (data.get("dcod_Postal") or "").strip(),
            "city": city_name(clean(data.get("ddenumire_Localitate"))),
            "state_id": state,
        }

    def _l10n_ro_anaf_to_values(self, result):
        """Map an ANAF answer on partner values."""
        flat = {}
        for key in (
            "date_generale",
            "inregistrare_scop_Tva",
            "inregistrare_RTVAI",
            "stare_inactiv",
            "inregistrare_SplitTVA",
            "adresa_sediu_social",
            "adresa_domiciliu_fiscal",
        ):
            flat.update(result.get(key, {}))
        if not flat.get("denumire"):
            return {}
        values = {
            "name": flat["denumire"].translate(CEDILLA_FIX).upper(),
            "l10n_ro_vat_subjected": bool(flat.get("scpTVA")),
            "company_type": "company",
        }
        flat.update(self._l10n_ro_anaf_address(flat))
        flat["vat"] = ("RO" if flat.get("scpTVA") else "") + str(flat.get("cui", ""))
        state = flat["state_id"]
        if "city_id" in self._fields and state and flat["city"]:
            city = self.env["res.city"].search([("state_id", "=", state.id), ("name", "=ilike", flat["city"])], limit=1)
            if city:
                flat["city_id"] = city.id
        if state == self.env.ref("base.RO_B"):
            zip_code = flat.get("codPostal") or flat.get("zip")
            if zip_code and zip_code[0] != "0":
                flat["codPostal"] = "0" + zip_code
        if not flat.get("codPostal"):
            flat["codPostal"] = flat.get("zip")
        for field_name, key, policy in ANAF_FIELDS:
            if key not in flat or field_name not in self._fields:
                continue
            value = flat[key]
            if policy == "if_value" and not value:
                continue
            if policy == "if_empty" and (not value or getattr(self, field_name, None)):
                continue
            if isinstance(value, models.BaseModel):
                value = value.id
            values[field_name] = value
        return values

    def _l10n_ro_anaf_fill(self):
        """Write on the partner the data that ANAF holds for its VAT number.

        :return: dict with a ``warning`` key when ANAF could not be queried
        """
        self.ensure_one()
        if not self.vat or self.parent_id:
            return {}
        vat_country, vat_number = self._split_vat(self.vat.strip().upper())
        vat_country = vat_country.upper()
        if not vat_country and self.country_id:
            vat_country = self._l10n_ro_map_vat_country_code(self.country_id.code.upper())
            vat_number = vat_number or self.vat
        if vat_country != "RO" or not vat_number.isdigit():
            return {}
        error, result = self._l10n_ro_anaf_request(vat_number)
        if error:
            return {"warning": {"title": self.env._("ANAF"), "message": error}}
        values = self._l10n_ro_anaf_to_values(result)
        if values:
            values["country_id"] = self.env.ref("base.ro").id
            self.write(values)
        return {}

    def l10n_ro_get_anaf_data(self):
        """Read again the data from ANAF (button / wizard). Returns the onchange
        result, with a ``warning`` key on failure."""
        self.ensure_one()
        if self.country_id and self.country_id.code != "RO":
            return False
        if self.name and not self.vat:
            match = RO_CUI_RE.match(self.name.strip())
            if match:
                self.vat = "RO" + match.group(1)
        return self._l10n_ro_anaf_fill()

    # ------------------------------------------------------------------
    # VIES (non-Romanian partners)
    # ------------------------------------------------------------------
    @api.model
    def _l10n_ro_vies_client(self):
        try:
            from zeep import Client  # pylint: disable=import-outside-toplevel
        except ImportError as e:
            raise UserError(
                self.env._("The 'zeep' library is required for VIES lookups. Install it with: pip install zeep")
            ) from e
        return Client("http://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl")

    def _l10n_ro_vies_check(self, client, country_code, vat_number):
        response = client.service.checkVat(countryCode=country_code, vatNumber=vat_number)
        if not response.valid and country_code == "GB":
            response = client.service.checkVat(countryCode="XI", vatNumber=vat_number)
        return response

    def _l10n_ro_vies_country(self, country_code):
        code = {"EL": "GR", "XI": "GB"}.get(country_code, country_code)
        return self.env["res.country"].search([("code", "=ilike", code)], limit=1)

    def l10n_ro_get_name_from_vies(self):
        self.ensure_one()
        client = self._l10n_ro_vies_client()
        if self.vat and not self.vat.isdigit():
            vat_number, country_code = self.vat[2:], self.vat[:2]
        elif self.country_id:
            vat_number = self.vat
            country_code = "EL" if self.country_id.code == "GR" else self.country_id.code
        else:
            raise UserError(self.env._("Please add the country code to the vat number or country field"))
        try:
            response = self._l10n_ro_vies_check(client, country_code, vat_number)
        except Exception as e:  # noqa: BLE001
            raise UserError(self.env._("VIES service error: %s", e)) from e
        if not response.valid:
            raise UserError(self.env._("Invalid VAT"))
        self.vat = vat_number
        country = self._l10n_ro_vies_country(country_code)
        if country:
            self.country_id = country
        self.name = response.name
        self.street = response.address

    @api.model
    def _l10n_ro_create_vals_from_vies(self, vals, country_code, vat_number):
        """VIES lookup at creation; updates ``vals`` in place."""
        try:
            client = self._l10n_ro_vies_client()
            vies_code = "EL" if country_code == "GR" else country_code
            response = self._l10n_ro_vies_check(client, vies_code, vat_number)
            if response.valid:
                vals["vat"] = country_code + vat_number
                if response.name:
                    vals["name"] = response.name
                if response.address:
                    vals["street"] = response.address
                country = self._l10n_ro_vies_country(country_code)
                if country:
                    vals["country_id"] = country.id
        except Exception as e:  # noqa: BLE001
            _logger.warning("VIES service not available. Exception: %s", e)

    # ------------------------------------------------------------------
    # Create from a name that is a VAT number
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            name = (vals.get("name") or "").strip()
            if not name:
                continue
            match = RO_CUI_RE.match(name)
            if match:
                self._l10n_ro_complete_vals_from_anaf(vals, match.group(1))
                continue
            match = EU_VAT_RE.match(name)
            if match and match.group(1).upper() != "RO":
                self._l10n_ro_create_vals_from_vies(vals, match.group(1).upper(), match.group(2))
        return super().create(vals_list)

    @api.model
    def _l10n_ro_complete_vals_from_anaf(self, vals, vat_number):
        vals["vat"] = "RO" + vat_number
        try:
            error, result = self._l10n_ro_anaf_request(vat_number)
            new_values = self._l10n_ro_anaf_to_values(result) if result else {}
        except Exception as e:  # noqa: BLE001
            _logger.warning("ANAF Webservice not working. Exception: %s", e)
            return
        vals.update(new_values)

    # ------------------------------------------------------------------
    # Unique partners
    # ------------------------------------------------------------------
    @api.model
    def _l10n_ro_unique_mode(self):
        """How the uniqueness of company partners is checked: ``off``,
        ``vat`` (VAT only) or ``vat_nrc`` (VAT and NRC)."""
        mode = self.env["ir.config_parameter"].sudo().get_param(UNIQUE_PARAM)
        return mode if mode in UNIQUE_MODES else "off"

    def _l10n_ro_unique_domain(self, mode):
        self.ensure_one()
        vat = (self.vat or "").strip().upper()
        nrc = (self.nrc or "").strip().upper() if self.nrc else ""
        vat_digits = vat.replace("RO", "")
        vat_prefixed = "RO" + vat_digits
        domain = [
            ("company_id", "=", self.company_id.id if self.company_id else False),
            ("parent_id", "=", False),
            ("id", "!=", self.id),
            ("is_company", "=", True),
        ]
        vat_domain = [
            "|",
            ("vat", "=ilike", vat_prefixed),
            ("vat", "=ilike", vat_digits),
        ]
        if mode == "vat_nrc":
            return domain + ["&"] + vat_domain + ["|", ("nrc", "=ilike", nrc), ("nrc", "=", False)]
        return domain + vat_domain

    @api.constrains("vat", "nrc", "is_company")
    def _l10n_ro_check_vat_unique(self):
        if self.env.context.get("partner_merge"):
            return
        mode = self._l10n_ro_unique_mode()
        if mode == "off":
            return
        for record in self.filtered("is_company"):
            if record.parent_id or not record.vat:
                continue
            company = record.company_id or self.env.company
            if company.account_fiscal_country_id.code != "RO":
                continue
            if self.env["res.partner"].search(record._l10n_ro_unique_domain(mode), limit=1):
                raise ValidationError(
                    self.env._(
                        "The VAT and NRC pair (%(vat)s, %(nrc)s) must be unique!",
                        vat=record.vat,
                        nrc=record.nrc,
                    )
                )
