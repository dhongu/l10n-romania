# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo.addons.l10n_ro_edi_stock.models.etransport_api import ETransportAPI


class ETransportActionsAPI(ETransportAPI):
    """Trimiterea evenimentelor de după UIT (ștergere, confirmare, modificare vehicul).

    ANAF primește aceste evenimente pe același endpoint de upload ca notificarea
    (`upload/ETRANSP/{cif}/2`); diferă doar conținutul XML. Refolosim `upload_data`
    din standard și, prin moștenire de clasă, patch-ul de timeout / retry pe
    `_make_etransport_request` din `l10n_ro_etransport_enhancement`.

    `upload_data` din standard NU întoarce un UIT pentru evenimente — răspunsul
    conține doar `index_incarcare`, iar validarea reală se află abia din
    `stareMesaj/{index_incarcare}` (vezi `l10n.ro.etransport.event._fetch_status`).
    """

    def upload_action(self, company_id, data):
        return self.upload_data(company_id=company_id, data=data)
