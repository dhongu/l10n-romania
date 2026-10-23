# ©  2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import logging
import re
import unicodedata

import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# ANAF synchronous VAT registry service (v9): up to 100 CUIs per request
ANAF_URL = "https://webservicesp.anaf.ro/api/PlatitorTvaRest/v9/tva"
# The caller usually waits for the answer (a cashier, a customer): better no answer than a long wait
ANAF_TIMEOUT = 10
# Control key of the Romanian CUI
CUI_KEY = "753217532"
# ANAF still answers with the old cedilla diacritics
CEDILLA_FIX = str.maketrans("şţŞŢ", "șțȘȚ")
BUCHAREST_STATE_CODE = "B"
BUCHAREST_SECTOR_RE = re.compile(r"sector(?:ul)?\s*([1-6])\b", re.IGNORECASE)
# A Bucharest postal code starts with 0 and the sector: 030167 is in Sector 3
BUCHAREST_ZIP_SECTOR_RE = re.compile(r"^0([1-6])\d{4}$")
# Prefixes ANAF puts before the name of the locality
# The administrative units ANAF writes around the name of the locality:
# "Mun. Timișoara", "Orș. Lipova", "Sat Filipești Com. Filipești"
LOCALITY_UNIT = r"(?:mun|municipiul|oraș|oras|orș|ors|or|com|comuna|sat)\.?"
LOCALITY_PREFIX_RE = re.compile(rf"^{LOCALITY_UNIT}\s+", re.IGNORECASE)
# The commune or town a village belongs to: only the village is the locality. Stricter than the
# prefix (abbreviations with their dot, no "Sat"), as it is searched inside the name
LOCALITY_PARENT_RE = re.compile(r"\s+(?:com\.|comuna|orș\.|ors\.|oraș|oras|mun\.|municipiul)\s+(\S.*)$", re.IGNORECASE)


def _normalize_name(name):
    """A locality name without diacritics, case, spaces, dots or dashes: ANAF and res.city write it
    differently ("Sector 3" and "Sector3", "Timişoara" and "Timișoara")"""
    name = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode()
    return re.sub(r"[\s\-.]+", "", name).lower()


class L10nRoAnafPartnerLookup(models.AbstractModel):
    _name = "l10n.ro.anaf.partner.lookup"
    _description = "ANAF partner lookup"

    @api.model
    def normalize_cui(self, vat):
        """``RO 12 34 567``, ``ro1234567`` and ``1234567`` are the same CUI: digits only, without ``RO``"""
        vat = re.sub(r"[\s.\-]", "", vat or "").upper()
        if vat.startswith("RO"):
            vat = vat[2:]
        return vat

    @api.model
    def is_valid_cui(self, cui):
        """Whether ``cui`` (digits only) is a Romanian CUI with a correct control digit"""
        if not cui or not cui.isdigit() or not 2 <= len(cui) <= 10:
            return False
        body = cui[:-1].zfill(9)
        control = sum(int(digit) * int(key) for digit, key in zip(body, CUI_KEY, strict=True)) * 10 % 11
        return int(cui[-1]) == control % 10

    @api.model
    def lookup(self, vat, timeout=None):
        """Look ``vat`` up at ANAF.

        :param timeout: seconds to wait for ANAF; the system parameter, else 10, when not given
        :return: dict with ``state`` (``found``, ``not_found``, ``invalid`` or ``unavailable``) and,
            when found, ``partner`` (values ready for ``res.partner.create``), ``vat_payer``,
            ``inactive``, ``inactive_date``, ``struck_off`` and ``trade_register`` (the J… number,
            also there when the partner has no field for it)
        """
        cui = self.normalize_cui(vat)
        if not self.is_valid_cui(cui):
            return {"state": "invalid"}
        result = self._request(cui, timeout)
        if result is None:
            return {"state": "unavailable"}
        if not result or not (result.get("date_generale") or {}).get("denumire"):
            return {"state": "not_found"}
        general = result.get("date_generale") or {}
        status = result.get("stare_inactiv") or {}
        return {
            "state": "found",
            "partner": self._prepare_partner_values(result),
            "vat_payer": bool((result.get("inregistrare_scop_Tva") or {}).get("scpTVA")),
            "inactive": bool(status.get("statusInactivi")),
            "inactive_date": self._clean(status.get("dataInactivare")),
            "trade_register": self._clean(general.get("nrRegCom")),
            "struck_off": bool(status.get("dataRadiere"))
            or "RADIERE" in (general.get("stare_inregistrare") or "").upper(),
        }

    @api.model
    def _request(self, cui, timeout=None):
        """Ask ANAF about one CUI: the record found, ``{}`` when not found, ``None`` when ANAF did not answer"""
        get_param = self.env["ir.config_parameter"].sudo().get_param
        try:
            response = requests.post(
                get_param("l10n_ro_anaf_partner_lookup.url", ANAF_URL),
                json=[{"cui": int(cui), "data": fields.Date.to_string(fields.Date.context_today(self))}],
                timeout=timeout or int(get_param("l10n_ro_anaf_partner_lookup.timeout", ANAF_TIMEOUT)),
            )
            response.raise_for_status()
            found = response.json().get("found") or []
        except (requests.RequestException, ValueError) as error:
            _logger.warning("ANAF did not answer for the CUI %s: %s", cui, error)
            return None
        return found[0] if found else {}

    @api.model
    def _clean(self, text):
        return re.sub(r"\s+", " ", (text or "").translate(CEDILLA_FIX)).strip()

    @api.model
    def _title(self, text):
        """ANAF writes some addresses in capitals: keep the cashier from typing them over"""
        return text.title() if text.isupper() else text

    @api.model
    def _prepare_partner_values(self, result):
        general = result.get("date_generale") or {}
        # The fiscal domicile is where the invoice goes; the registered office is the fallback
        fiscal = result.get("adresa_domiciliu_fiscal") or {}
        office = result.get("adresa_sediu_social") or {}

        def address(fiscal_key, office_key):
            return self._clean(fiscal.get(fiscal_key)) or self._clean(office.get(office_key))

        vat_payer = bool((result.get("inregistrare_scop_Tva") or {}).get("scpTVA"))
        cui = str(general.get("cui") or "")
        values = {
            "name": self._clean(general.get("denumire")),
            "is_company": True,
            # The RO prefix only for a VAT payer, as on the invoice
            "vat": f"RO{cui}" if vat_payer else cui,
            "country_id": self.env.ref("base.ro").id,
        }
        # The VAT payer flag of the Romanian localization, whichever module defines it: without it
        # the RO prefix would be stripped again when the partner is saved
        if "l10n_ro_vat_subjected" in self.env["res.partner"]._fields:
            values["l10n_ro_vat_subjected"] = vat_payer
        street = self._title(address("ddenumire_Strada", "sdenumire_Strada"))
        number = address("dnumar_Strada", "snumar_Strada")
        if number:
            street = f"{street} Nr. {number}".strip()
        details = self._title(address("ddetalii_Adresa", "sdetalii_Adresa"))
        if not street:
            street, details = details, ""
        values["street"] = street
        values["street2"] = details
        zip_code = address("dcod_Postal", "scod_Postal") or self._clean(general.get("codPostal"))
        # Romanian postal codes have 6 digits; ANAF drops the leading 0 of the Bucharest ones
        if zip_code.isdigit() and len(zip_code) == 5:
            zip_code = "0" + zip_code
        values["zip"] = zip_code

        state_code = address("dcod_JudetAuto", "scod_JudetAuto")
        state = self.env["res.country.state"].search(
            [("country_id.code", "=", "RO"), ("code", "=", state_code)], limit=1
        )
        values["state_id"] = state.id
        locality = address("ddenumire_Localitate", "sdenumire_Localitate")
        values["city"] = self._prepare_city(locality, state_code, zip_code)
        city_id = self._prepare_city_id(values["city"], state, zip_code, self._locality_commune(locality))
        if city_id:
            values["city_id"] = city_id
        # The trade register number (J…) goes to its own field of the Romanian localization. The
        # Company ID (company_registry) is the CUI, which l10n_ro computes from the Tax ID
        if general.get("nrRegCom") and "nrc" in self.env["res.partner"]._fields:
            values["nrc"] = self._clean(general["nrRegCom"])
        if general.get("telefon"):
            values["phone"] = self._clean(general["telefon"])
        return values

    @api.model
    def _locality_commune(self, locality):
        """The commune or town a village belongs to: ``Sat Filipești Com. Filipești`` gives ``Filipești``"""
        match = LOCALITY_PARENT_RE.search(locality or "")
        return match.group(1).strip() if match else ""

    @api.model
    def _prepare_city_id(self, city, state, zip_code="", commune=""):
        """The ``res.city`` of the locality, where the partner has a ``city_id`` (base_address_extended,
        with the cities of l10n_ro_city); ``False`` when no single city matches"""
        if not state or not city or "city_id" not in self.env["res.partner"]._fields or "res.city" not in self.env:
            return False
        City = self.env["res.city"].sudo()
        cities = City.search([("state_id", "=", state.id)])
        named = cities.filtered(lambda c: _normalize_name(c.name) == _normalize_name(city))
        # Several villages of the same name in a county: the commune, then the postal code tell them apart
        if len(named) > 1 and commune and "l10n_ro_municipality" in City._fields:
            narrowed = named.filtered(lambda c: _normalize_name(c.l10n_ro_municipality) == _normalize_name(commune))
            named = narrowed or named
        if len(named) > 1 and zip_code:
            named = named.filtered(lambda c: c.zipcode == zip_code) or named
        if len(named) == 1:
            return named.id
        if named or not zip_code:
            return False
        # The name is not in the list: the postal code, street by street (l10n_ro_zip), then of the city
        if "res.zip" in self.env:
            by_street = self.env["res.zip"].sudo().search([("name", "=", zip_code)]).city_id
            by_street = by_street.filtered(lambda c: c.state_id == state)
            if len(by_street) == 1:
                return by_street.id
        by_zip = cities.filtered(lambda c: c.zipcode == zip_code)
        return by_zip.id if len(by_zip) == 1 else False

    @api.model
    def _prepare_city(self, locality, state_code, zip_code=""):
        """The locality without ``Mun.``/``Oraș``/``Com.``, a village without its commune; for Bucharest
        the sector, as e-Factura wants it"""
        if state_code == BUCHAREST_STATE_CODE:
            # ANAF does not always write the sector in the locality: the postal code tells it then
            match = BUCHAREST_SECTOR_RE.search(locality) or BUCHAREST_ZIP_SECTOR_RE.match(zip_code or "")
            # Without either, the locality is left as it is for the e-Factura check to point out
            return f"Sector {match.group(1)}" if match else locality
        return self._title(LOCALITY_PARENT_RE.sub("", LOCALITY_PREFIX_RE.sub("", locality)))
