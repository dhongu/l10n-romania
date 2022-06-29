# ©  2008-2022 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from lxml import etree

from odoo import models

# class IrActionsReport(models.Model):
#     _inherit = 'ir.actions.report'
#
#     def _postprocess_pdf_report(self, record, buffer):
#         '''Add the pdf report in the e-fff XML as base64 string.
#         '''
#         result = super()._postprocess_pdf_report(record, buffer)
#
#         if record._name == 'account.move':
#             edi_attachment = record.edi_document_ids.filtered(lambda d: d.edi_format_id.code == 'cirus_ro').attachment_id
#             if edi_attachment:
#                     edi_attachment.write({
#                         'res_model': 'account.move',
#                         'res_id': record.id,
#                         'datas': base64.b64encode(new_xml),
#                         'mimetype': 'application/xml',
#                     })
#
#         return result
