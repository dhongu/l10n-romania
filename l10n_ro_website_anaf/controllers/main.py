# ©  2026 Terrabit
# See README.rst file on addons root folder for license details

import time
from collections import OrderedDict

from odoo import http
from odoo.http import request

from .. import anaf
from ..anaf import is_cnp, normalize_vat

# The route is public: without a limit, anyone could use it as a free proxy to ANAF. Kept in the
# memory of each worker, which is enough to stop a script, not a hard quota.
RATE_LIMIT = 20
RATE_WINDOW = 600
# a company is looked up once a day, whoever types its tax code
CACHE_TTL = 86400
CACHE_SIZE = 1000

_hits = {}
_cache = OrderedDict()


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
        return anaf.anaf_lookup(request.env, number)

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
