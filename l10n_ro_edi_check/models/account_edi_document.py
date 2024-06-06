# ©  2024-now Dan Stoica <danila(@)terrabit(.)ro
# See README.rst file on addons root folder for license details


import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


# class AccountEdiDocument(models.Model):
#     _inherit = "account.edi.document"
#
#     @api.model
#     def _cron_process_documents_web_services(self, job_count=None):
#         domain = [
#             ("state", "in", ("to_send", "to_cancel")),
#             ("move_id.state", "=", "posted"),
#             ("move_id.date", ">=", "2024-01-01"),
#         ]
#         edi_documents = self.search(domain)
#
#         for edi_document in edi_documents:
#             key = "ro_efactura_{}".format(edi_document.move_id.id)
#             domain = [("identity_key", "=", key), ("state", "=", "failed")]
#             existing = self.env["queue.job"].sudo().search(domain, limit=1)
#             if not existing:
#                 edi_document.with_delay(identity_key=key)._process_documents_web_services()
#
#         self.env.ref("queue_job_cron_jobrunner.queue_job_cron")._trigger()
