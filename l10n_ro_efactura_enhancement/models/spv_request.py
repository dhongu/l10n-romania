# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import json
import logging
import re

from odoo.addons.l10n_ro_edi.models import utils as edi_utils
from odoo.addons.l10n_ro_message_spv.models import ciusro_document as spv_document

_logger = logging.getLogger(__name__)

# First bytes a successful SPV payload must start with, per endpoint.
#
# ANAF regularly answers HTTP 200 with a body that is not the expected payload:
# a JSON error object (download limit reached, unknown id_incarcare), a plain
# text message or an HTML page coming from its gateway during maintenance.
# ``make_efactura_request`` only maps the 204/400/401/403/500 status codes, so
# such a body is handed over to the callers, which then crash while parsing it
# (lxml "Start tag expected, '<' not found, line 1, column 1" on stareMesaj,
# BadZipFile on descarcare, a corrupted PDF attachment on transformare).
ENDPOINT_PREFIXES = {
    "upload": (b"<",),
    "uploadb2c": (b"<",),
    "stareMesaj": (b"<",),
    "descarcare": (b"PK",),
    "transformare": (b"%PDF",),
    "listaMesajeFactura": (b"{", b"["),
    "listaMesajePaginatieFactura": (b"{", b"["),
}

# Keys ANAF uses to carry the error text in its JSON answers.
JSON_ERROR_KEYS = ("eroare", "message", "Message", "error", "titlu")

# Number of characters of the raw answer kept in the error message and the log.
SNIPPET_LENGTH = 300


def _answer_detail(content):
    """Return a short, human readable description of an unexpected SPV answer."""
    if content[:1] in (b"{", b"["):
        try:
            answer = json.loads(content.decode("utf-8", errors="replace"))
        except ValueError:
            answer = None
        if isinstance(answer, dict):
            for key in JSON_ERROR_KEYS:
                if answer.get(key):
                    return str(answer[key])[:SNIPPET_LENGTH]

    # Not a JSON error we recognise: keep a readable excerpt of the raw body.
    # Markup is stripped so an HTML gateway page stays legible in the chatter.
    text = content[: SNIPPET_LENGTH * 8].decode("utf-8", errors="replace")
    text = re.sub(r"<[^>]*>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:SNIPPET_LENGTH] or "-"


def check_spv_answer(company, endpoint, content):
    """Check that ``content`` can be the payload expected for ``endpoint``.

    :param company: ``res.company`` object, used for the translations
    :param endpoint: SPV endpoint the answer comes from
    :param content: raw body returned by the SPV
    :return: an error string when the body cannot be parsed by the caller,
        ``None`` when it looks valid or when the endpoint is not known here
    """
    prefixes = ENDPOINT_PREFIXES.get(endpoint)
    if not prefixes:
        return None

    stripped = (content or b"").lstrip()
    if not stripped:
        return company.env._(
            "The SPV answered with an empty body on %(endpoint)s. Please try again later.",
            endpoint=endpoint,
        )
    if stripped.startswith(prefixes):
        return None

    return company.env._(
        "The SPV answered with unexpected content on %(endpoint)s: %(detail)s",
        endpoint=endpoint,
        detail=_answer_detail(stripped),
    )


def _patch_make_efactura_request(module):
    """Wrap ``module.make_efactura_request`` so that an unexpected SPV answer is
    reported as a business error in the chatter instead of crashing the caller.

    The wrapper is installed on the module holding the function, not on the
    modules importing it, so it covers every request made through it.
    """
    original = module.make_efactura_request
    if getattr(original, "_l10n_ro_answer_checked", False):
        return

    def make_efactura_request(session, company, endpoint, params, data=None):
        result = original(
            session=session,
            company=company,
            endpoint=endpoint,
            params=params,
            data=data,
        )
        if "content" not in result:
            return result

        error = check_spv_answer(company, endpoint, result["content"])
        if error:
            _logger.warning("Unexpected SPV answer on %s (params=%s): %s", endpoint, params, error)
            return {"error": error}
        return result

    make_efactura_request._l10n_ro_answer_checked = True
    make_efactura_request.__wrapped__ = original
    module.make_efactura_request = make_efactura_request


# ``l10n_ro_message_spv`` keeps its own copy of the function, so both need the wrapper.
_patch_make_efactura_request(edi_utils)
_patch_make_efactura_request(spv_document)
