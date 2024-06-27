import io
import requests
import zipfile

from lxml import etree
from odoo import models, fields, api, _

NS_UPLOAD = {"ns": "mfp:anaf:dgti:spv:respUploadFisier:v1"}
NS_STATUS = {"ns": "mfp:anaf:dgti:efactura:stareMesajFactura:v1"}
NS_HEADER = {"ns": "mfp:anaf:dgti:efactura:mesajEroriFactuta:v1"}
NS_SIGNATURE = {"ns": "http://www.w3.org/2000/09/xmldsig#"}


class L10nRoEdiDocument(models.Model):
    _name = 'l10n_ro_edi.document'
    _description = "Document object for tracking CIUS-RO XML sent to E-Factura"
    _order = 'datetime DESC, id DESC'

    invoice_id = fields.Many2one(comodel_name='account.move', required=True)
    state = fields.Selection(
        selection=[
            ('invoice_sending', 'Sending'),
            ('invoice_sending_failed', 'Error'),
            ('invoice_sent', 'Sent'),
        ],
        string='E-Factura Status',
        required=True,
    )
    datetime = fields.Datetime(default=fields.Datetime.now, required=True)
    attachment_id = fields.Many2one(comodel_name='ir.attachment')
    message = fields.Char()
    key_loading = fields.Char()         # To be used to fetch the status of previously sent XML
    key_signature = fields.Char()       # Received from a successful response: to be saved for government purposes
    key_certificate = fields.Char()     # Received from a successful response: to be saved for government purposes

    def unlink(self):
        """ This method make sure that the created attachment (if it exists) is also deleted """
        self.attachment_id.sudo().unlink()
        return super().unlink()

    @api.model
    def _make_efactura_request(self, company, endpoint, method, params, data=None, session=None) -> dict[str, str | bytes]:
        """ Make an API request to the Romanian SPV, handle the response, and return a `result` dictionary
            :param company: `res.company` object containing l10n_ro_edi_test_env, l10n_ro_edi_access_token
            :param endpoint: 'upload' (for sending) |
                             'stareMesaj' (for fetching status) |
                             'descarcare' (for downloading answer)
            :param method: 'post' (for 'upload') |
                           'get' (for 'stareMesaj'|'descarcare')
            :param params: Dictionary of query parameters
            :param data: xml data for 'upload' request
            :return: dictionary of {'error': <str>} or {'content': <response.content>} from E-Factura
        """
        send_mode = 'test' if company.l10n_ro_edi_test_env else 'prod'
        url = f"https://api.anaf.ro/{send_mode}/FCTEL/rest/{endpoint}"
        headers = {'Content-Type': 'application/xml',
                   'Authorization': f'Bearer {company.l10n_ro_edi_access_token}'}

        try:
            requester = session or requests
            response = requester.request(method=method, url=url, params=params, data=data, headers=headers, timeout=10)
        except requests.HTTPError as e:
            return {'error': str(e)}
        if response.status_code == 400:
            error_json = response.json()
            return {'error': error_json['message']}
        if response.status_code == 403:
            return {'error': _('Access token is forbidden.')}
        if response.status_code == 204:
            return {'error': _('You reached the limit of requests. Please try again later.')}

        return {'content': response.content}

    @api.model
    def _request_ciusro_send_invoice(self, company, xml_data, move_type='out_invoice'):
        """ This method makes an 'upload' request to send xml_data to Romanian SPV.
            Based on the result, it will then process the answer and returns a dictionary,
            which may consist of either an 'error' or a 'key_loading' string
            :param company: `res.company` object
            :param xml_data: string of XML data to be sent
            :param move_type: `move_type` field from `account.move` object, used for the request parameter
            :return: result dictionary -> {'error': <str>} | {'key_loading': <str>}
        """
        result = self._make_efactura_request(
            company=company,
            endpoint='upload',
            method='POST',
            params={'standard': 'UBL' if move_type == 'out_invoice' else 'CN',
                    'cif': company.vat.replace('RO', '')},
            data=xml_data,
        )
        if 'error' in result:
            return result

        root = etree.fromstring(result['content'])
        res_status = root.get('ExecutionStatus')
        if res_status == '1':
            error_elements = root.findall('.//ns:Errors', namespaces=NS_UPLOAD)
            error_messages = [error_element.get('errorMessage') for error_element in error_elements]
            return {'error': '\n'.join(error_messages)}
        else:
            return {'key_loading': root.get('index_incarcare')}

    @api.model
    def _request_ciusro_fetch_status(self, company, key_loading, session=None):
        """ This method makes a "Fetch Status" (GET/stareMesaj) request to the Romanian SPV.
            After processing the response, it will return 1 of the following 3 possible object:
             - {'error': <str>} ~ failing response from a bad request
             - {'key_download': <str>} ~ The response was successful, and we can use this key to download the answer
             - {} ~ (empty dict) The response was successful but the SPV haven't finished processing the XML yet.
        :param company: `res.company` object
        :param key_loading: content of `key_loading` received from `_request_ciusro_send_invoice`
        :param session: optional `requests.session` object
        :return: {'error': <str>} | {'key_download': <str>} | {}
        """
        result = self._make_efactura_request(
            company=company,
            endpoint='stareMesaj',
            method='GET',
            params={'id_incarcare': key_loading},
            session=session,
        )
        if 'error' in result:
            return result

        root = etree.fromstring(result['content'])
        error_elements = root.findall('.//ns:Errors', namespaces=NS_STATUS)
        if error_elements:
            return {'error': '\n'.join(error_element.get('errorMessage') for error_element in error_elements)}

        state_status = root.get('stare')
        if state_status in ('nok', 'ok'):
            return {'key_download': root.get('id_descarcare')}
        else:
            return {}

    @api.model
    def _request_ciusro_download_answer(self, company, key_download, session=None):
        """ This method makes a "Download Answer" (GET/descarcare) request to the Romanian SPV.
            It then processes the response by opening the received zip file and returns either:
             - {'error': <str>} ~ failing response from a bad request / unaccepted XML answer from the SPV
             - <successful response dictionary> ~ contains the necessary information to be stored from the SPV
        :param company: a `res.company` object
        :param key_download: content of `key_download` received from `_request_ciusro_send_invoice`
        :param session: optional `requests.session` object
        :return: {'error': <str>} | {'attachment_raw': <str>, 'key_signature': <str>, 'key_certificate': <str>'}
        """
        result = self._make_efactura_request(
            company=company,
            endpoint='descarcare',
            method='GET',
            params={'id': key_download},
            session=session,
        )
        if 'error' in result:
            return result

        # E-Factura gives download response in ZIP format
        zip_ref = zipfile.ZipFile(io.BytesIO(result['content']))
        signature_file = next(file for file in zip_ref.namelist() if 'semnatura' in file)
        xml_bytes = zip_ref.open(signature_file)
        root = etree.parse(xml_bytes)
        error_element = root.find('.//ns:Error', namespaces=NS_HEADER)
        if error_element is not None:
            return {'error': error_element.get('errorMessage')}

        # Pretty-print the XML content of the signature file to be saved as attachment
        attachment_raw = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        return {
            'attachment_raw': attachment_raw,
            'key_signature': root.find('.//ns:SignatureValue', namespaces=NS_SIGNATURE).text,
            'key_certificate': root.find('.//ns:X509Certificate', namespaces=NS_SIGNATURE).text,
        }

    def action_l10n_ro_edi_fetch_status(self):
        """ Fetch the latest response from E-Factura about the XML sent """
        self.ensure_one()
        # Do the batch fetch process on a single invoice/document
        self.invoice_id._l10n_ro_edi_fetch_invoice_sending_documents()

    def action_l10n_ro_edi_download_signature(self):
        """ Download the received successful signature XML file from E-Factura """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self.attachment_id.id}?download=true',
        }
