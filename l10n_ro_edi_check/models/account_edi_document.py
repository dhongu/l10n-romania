# ©  2024-now Dan Stoica <danila(@)terrabit(.)ro
# See README.rst file on addons root folder for license details




from odoo import models, api, fields

import logging

_logger = logging.getLogger(__name__)



class AccountEdiDocument(models.Model):
    _inherit = 'account.edi.document'

    @api.model
    def _cron_process_documents_web_services(self, job_count=None):
        domain = [
            ('state', 'in', ('to_send', 'to_cancel')),
            ('move_id.state', '=', 'posted'),
            ("move_id.date", ">=", "2024-01-01")
        ]
        edi_documents = self.search(domain)

        for edi_document in edi_documents:
            edi_document.with_delay()._process_documents_web_services()

        domain = [
            ('state', 'in', ('to_send', 'to_cancel')),
            ('move_id.state', '=', 'posted'),
            ("blocking_level", "=", "error"),
            ("write_date", "<", fields.Date.today())
        ]
        edi_documents = self.search(domain)
        if edi_documents:
            edi_documents.write({"blocking_level": False})

        # self.env.ref('queue_job_cron_jobrunner.queue_job_cron')._trigger()



