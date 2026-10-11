# ©  2026 Terrabit
# See README.rst file on addons root folder for license details

import logging
import time
from collections import OrderedDict

import requests

from odoo import fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)

ANAF_URL = "https://webservicesp.anaf.ro/api/PlatitorTvaRest/v9/tva"
# the customer is typing: better say nothing than keep them waiting
ANAF_TIMEOUT = 5
# check digit weights of the Romanian personal numeric code (CNP)
CNP_WEIGHTS = (2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9)

# The route is public: without a limit, anyone could use it as a free proxy to ANAF. Kept in the
# memory of each worker, which is enough to stop a script, not a hard quota.
RATE_LIMIT = 20
RATE_WINDOW = 600
# a company is looked up once a day, whoever types its tax code
CACHE_TTL = 86400
CACHE_SIZE = 1000

_hits = {}
_cache = OrderedDict()


def normalize_vat(vat):
    """``RO 12 34 567``, ``ro1234567`` and ``1234567`` are the same tax code: letters and digits
    only, upper case, without a two-letter country prefix."""
    vat = "".join(ch for ch in (vat or "") if ch.isalnum()).upper()
    if len(vat) > 2 and vat[:2].isalpha():
        vat = vat[2:]
    return vat


def is_cnp(number):
    """Whether ``number`` is a valid Romanian personal numeric code (13 digits, check digit)."""
    if len(number) != 13 or not number.isdigit() or number[0] not in "12345678":
        return False
    rest = sum(int(number[i]) * CNP_WEIGHTS[i] for i in range(12)) % 11
    return int(number[12]) == (1 if rest == 10 else rest)


class AnafPrefill(http.Controller):
    # not a website route: it needs no website context, and the frontend dispatch (language
    # cookie, visitor) has nothing to add to a JSON look-up
    @http.route("/l10n_ro/anaf_lookup", type="jsonrpc", auth="public", methods=["POST"])
    def anaf_lookup(self, vat=""):
        """The ANAF data of a Romanian tax code, for the address forms.

        :return: ``{"state": ...}``: ``found`` with the company, ``not_found``, ``unavailable``,
            ``cnp`` (a personal code, not a company), ``invalid`` or ``limited``
        """
        number = normalize_vat(vat)
        if is_cnp(number):
            return {"state": "cnp"}
        if not number.isdigit() or not 2 <= len(number) <= 10:
            return {"state": "invalid"}
        cached = self._cache_get(number)
        if cached:
            return cached
        if self._rate_limited():
            return {"state": "limited"}
        state, values = self._anaf_lookup(number)
        payload = {"state": state}
        if state == "found":
            payload.update(self._anaf_payload(values))
        if state in ("found", "not_found"):
            self._cache_set(number, payload)
        return payload

    def _anaf_lookup(self, number):
        """Look ``number`` up at ANAF, with the settings of ``l10n_ro_partner_create_by_vat``.

        Its own request rather than ``_get_Anaf``: that one waits up to 30 s and answers the same
        text for a company not found and for a service down.

        :return: ``(state, values)``: ``found`` with the partner values, ``not_found`` or
            ``unavailable``
        """
        get_param = request.env["ir.config_parameter"].sudo().get_param
        headers = {"Content-Type": "application/json"}
        api_key = get_param("l10n_ro_partner_create_by_vat.anaf_api_key", "")
        if api_key:
            headers[get_param("l10n_ro_partner_create_by_vat.anaf_api_key_header_tag", "x-api-key")] = api_key
        try:
            response = requests.post(
                get_param("l10n_ro_partner_create_by_vat.anaf_url", ANAF_URL),
                json=[{"cui": number, "data": fields.Date.to_string(fields.Date.today())}],
                headers=headers,
                timeout=ANAF_TIMEOUT,
            )
            response.raise_for_status()
            found = response.json().get("found") or []
        except (requests.RequestException, ValueError) as error:
            _logger.warning("ANAF did not answer for the tax code %s: %s", number, error)
            return "unavailable", {}
        result = found[0] if found else {}
        if not result.get("date_generale"):
            return "not_found", {}
        general = result["date_generale"]
        status = result.get("stare_inactiv") or {}
        # struck off: read from the registration state, `dataRadiere` is often empty
        radiated = "RADIERE" in (general.get("stare_inregistrare") or "").upper()
        inactive = bool(status.get("statusInactivi"))
        values = request.env["res.partner"].sudo()._Anaf_to_Odoo(result)
        if not values:
            return "not_found", {}
        values.update(anaf_radiated=radiated, anaf_inactive=inactive)
        return "found", values

    def _anaf_payload(self, values):
        """Only public ANAF data, in the shape the form fields expect."""
        state = values.get("state_id")
        return {
            "name": values.get("name") or "",
            "street": values.get("street") or "",
            "city": values.get("city") or "",
            "zip": values.get("zip") or "",
            "company_registry": values.get("nrc") or "",
            "state_id": state.id if state else False,
            "vat_payer": bool(values.get("l10n_ro_vat_subjected")),
            "inactive": bool(values.get("anaf_inactive")),
            "radiated": bool(values.get("anaf_radiated")),
        }

    def _rate_limited(self):
        now = time.monotonic()
        key = request.httprequest.remote_addr or ""
        hits = [hit for hit in _hits.get(key, []) if now - hit < RATE_WINDOW]
        if len(hits) >= RATE_LIMIT:
            _hits[key] = hits
            return True
        hits.append(now)
        _hits[key] = hits
        if len(_hits) > CACHE_SIZE:
            # forget the visitors who did not come back within the window
            for ip in [ip for ip, ip_hits in _hits.items() if not ip_hits or now - ip_hits[-1] >= RATE_WINDOW]:
                _hits.pop(ip, None)
        return False

    def _cache_get(self, number):
        entry = _cache.get(number)
        if entry and time.monotonic() - entry[0] < CACHE_TTL:
            return entry[1]
        _cache.pop(number, None)
        return None

    def _cache_set(self, number, payload):
        _cache[number] = (time.monotonic(), payload)
        _cache.move_to_end(number)
        while len(_cache) > CACHE_SIZE:
            _cache.popitem(last=False)
