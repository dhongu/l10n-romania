# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from odoo.addons.l10n_ro_edi_stock.models.etransport_api import ETransportAPI

_logger = logging.getLogger(__name__)

# Timeout implicit (secunde) folosit când compania nu are unul configurat.
# Standardul Odoo are 10s hardcodat, insuficient pentru api.anaf.ro la ore de vârf.
DEFAULT_ETRANSPORT_TIMEOUT = 60

# Reîncercări doar pentru cererile GET (idempotente - interogarea stării).
# Încărcarea documentului (POST) NU se reîncearcă automat: ANAF poate să fi
# înregistrat deja notificarea, iar o retrimitere ar genera un UIT duplicat.
GET_RETRY = Retry(
    total=3,
    connect=3,
    read=2,
    backoff_factor=1,
    status_forcelist=(500, 502, 503, 504),
    allowed_methods=frozenset(["GET"]),
)


def _apply_timeout(session, timeout):
    """Forțează timeout-ul pe o sesiune requests, indiferent ce primește session.request().

    Standardul apelează session.request(..., timeout=10). Rescriem metoda pe
    instanță ca să suprascriem valoarea, fără să duplicăm logica din core.
    """
    if getattr(session, "_l10n_ro_etransport_timeout", None) == timeout:
        return session

    original_request = session.request

    def request(*args, **kwargs):
        kwargs["timeout"] = timeout
        return original_request(*args, **kwargs)

    session.request = request
    session._l10n_ro_etransport_timeout = timeout
    return session


def _make_etransport_request(self, company, endpoint: str, method: str, session=None, data=None) -> dict:
    timeout = company.l10n_ro_etransport_timeout or DEFAULT_ETRANSPORT_TIMEOUT

    if session is None:
        session = requests.Session()

    if method.lower() == "get":
        session.mount("https://", HTTPAdapter(max_retries=GET_RETRY))

    _apply_timeout(session, timeout)
    _logger.debug("eTransport request %s %s (timeout=%ss)", method, endpoint, timeout)

    return _make_etransport_request.origin(self, company, endpoint, method, session=session, data=data)


if not getattr(ETransportAPI._make_etransport_request, "_l10n_ro_etransport_patched", False):
    _make_etransport_request.origin = ETransportAPI._make_etransport_request
    _make_etransport_request._l10n_ro_etransport_patched = True
    ETransportAPI._make_etransport_request = _make_etransport_request
