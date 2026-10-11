# ©  2026 Terrabit
# See README.rst file on addons root folder for license details
"""ANAF look-up and Romanian tax code helpers, shared by the public route and the address check."""

import logging

import requests

from odoo import fields

_logger = logging.getLogger(__name__)

ANAF_URL = "https://webservicesp.anaf.ro/api/PlatitorTvaRest/v9/tva"
# a customer is waiting, typing or submitting: better no answer than a long wait
ANAF_TIMEOUT = 5
# check digit weights of the Romanian personal numeric code (CNP)
CNP_WEIGHTS = (2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9)


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


def anaf_lookup(env, number):
    """Look ``number`` up at ANAF, with the settings of ``l10n_ro_partner_create_by_vat``.

    Its own request rather than ``_get_Anaf``: that one waits up to 30 s and answers the same text
    for a company not found and for a service down.

    :return: ``(state, values)``: ``found`` with the partner values (plus ``anaf_radiated``,
        ``anaf_inactive`` and ``anaf_inactive_date``), ``not_found`` or ``unavailable``
    """
    get_param = env["ir.config_parameter"].sudo().get_param
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
    inactive_date = (status.get("dataInactivare") or "").strip()
    values = env["res.partner"].sudo()._Anaf_to_Odoo(result)
    if not values:
        return "not_found", {}
    values.update(anaf_radiated=radiated, anaf_inactive=inactive, anaf_inactive_date=inactive_date)
    return "found", values
