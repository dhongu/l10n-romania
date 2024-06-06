# Copyright (C) 2022 Dorin Hongu <dhongu(@)gmail(.)com
# Copyright (C) 2022 NextERP Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


# class AccountEdiXmlCIUSRO(models.Model):
#     _inherit = "account.edi.xml.cius_ro"
#
#     def _get_delivery_vals_list(self, invoice):
#         res = super()._get_delivery_vals_list(invoice)
#
#         shipping_address = False
#         if "partner_shipping_id" in invoice._fields and invoice.partner_shipping_id:
#             shipping_address = invoice.partner_shipping_id
#             if shipping_address == invoice.partner_id:
#                 shipping_address = False
#         if shipping_address:
#             res = [
#                 {
#                     "actual_delivery_date": invoice.invoice_date,
#                     "delivery_location_vals": {
#                         "delivery_address_vals": self._get_partner_address_vals(shipping_address),
#                     },
#                 }
#             ]
#         return res
