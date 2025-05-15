import requests

from odoo import _
from odoo.addons.l10n_ro_efactura.models import ciusro_document
import logging
_logger = logging.getLogger(__name__)

_original_make_efactura_request = ciusro_document.make_efactura_request


def make_efactura_request(session, company, endpoint, method, params, data=None) -> dict[str, str | bytes]:
    """
    Make an API request to the Romanian SPV, handle the response, and return a ``result`` dictionary.

    :param session: ``requests`` or ``requests.Session()`` object
    :param company: ``res.company`` object containing l10n_ro_edi_test_env, l10n_ro_edi_access_token
    :param endpoint: ``upload`` (for sending) | ``stareMesaj`` (for fetching status) | ``descarcare`` (for downloading answer)
    :param method: ``post`` (for `upload`) | ``get`` (for `stareMesaj` | `descarcare`)
    :param params: Dictionary of query parameters
    :param data: XML data for ``upload`` request
    :return: Dictionary of {'error': <str>} or {'content': <response.content>} from E-Factura
    """
    send_mode = 'test' if company.l10n_ro_edi_test_env else 'prod'
    url = f"https://api.anaf.ro/{send_mode}/FCTEL/rest/{endpoint}"
    headers = {'Content-Type': 'application/xml',
               'Authorization': f'Bearer {company.l10n_ro_edi_access_token}'}

    try:
        response = session.request(method=method, url=url, params=params, data=data, headers=headers, timeout=60)
    except requests.HTTPError as e:
        return {'error': str(e)}
    if response.status_code == 204:
        return {'error': _('You reached the limit of requests. Please try again later.')}
    if response.status_code == 400:
        error_json = response.json()
        return {'error': error_json['message']}
    if response.status_code == 401:
        return {'error': _('Access token is unauthorized.')}
    if response.status_code == 403:
        return {'error': _('Access token is forbidden.')}
    if response.status_code == 500:
        _logger.error(f"Error in E-Factura: {response.content}")
        return {'error': _('There is something wrong with the SPV. Please try again later.')}

    return {'content': response.content}



ciusro_document.make_efactura_request = make_efactura_request
