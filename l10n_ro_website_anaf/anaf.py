# ©  2026 Terrabit
# See README.rst file on addons root folder for license details
"""ANAF look-up and Romanian tax code helpers, shared by the public route and the address check."""

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
    """Look ``number`` up at ANAF, through ``l10n_ro_anaf_partner_lookup``.

    :return: ``(state, values)``: ``found`` with the partner values (``state_id`` as a record, plus
        ``nrc``, ``l10n_ro_vat_subjected``, ``anaf_radiated``, ``anaf_inactive`` and
        ``anaf_inactive_date``), ``not_found`` or ``unavailable``. No ``is_company``: Odoo computes
        it (its own commercial entity with a Tax ID); the CUI is the ``RO_EN`` identifier, which
        Odoo deduces from the Tax ID.
    """
    result = env["l10n.ro.anaf.partner.lookup"].sudo().lookup(number, timeout=ANAF_TIMEOUT)
    if result["state"] == "unavailable":
        return "unavailable", {}
    if result["state"] != "found":
        return "not_found", {}
    values = dict(result["partner"])
    values.update(
        state_id=env["res.country.state"].sudo().browse(values.get("state_id")),
        nrc=result["trade_register"],
        l10n_ro_vat_subjected=result["vat_payer"],
        anaf_radiated=result["struck_off"],
        anaf_inactive=result["inactive"],
        anaf_inactive_date=result["inactive_date"],
    )
    return "found", values
