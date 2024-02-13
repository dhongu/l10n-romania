# Copyright (C) 2022 Dorin Hongu <dhongu(@)gmail(.)com
# Copyright (C) 2022 NextERP Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AccountEdiXmlCIUSRO(models.Model):
    _inherit = "account.edi.format"

    def _find_value(self, xpath, xml_element, namespaces=None):
        if namespaces is None:
            namespaces = {}

        namespaces.update(
            {
                "qdt": "urn:oasis:names:specification:ubl:schema:xsd:QualifiedDataTypes-2",
                "ccts": "urn:un:unece:uncefact:documentation:2",
                "udt": "urn:oasis:names:specification:ubl:schema:xsd:UnqualifiedDataTypes-2",
                "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",  # noqa: B950
                "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            }
        )

        res = super()._find_value(xpath, xml_element, namespaces=namespaces)

        return res


class AccountEdiXmlCIUSRO(models.Model):
    _inherit = "account.edi.xml.cius_ro"

    def _get_delivery_vals_list(self, invoice):
        res = super()._get_delivery_vals_list(invoice)

        shipping_address = False
        if "partner_shipping_id" in invoice._fields and invoice.partner_shipping_id:
            shipping_address = invoice.partner_shipping_id
            if shipping_address == invoice.partner_id:
                shipping_address = False
        if shipping_address:
            res = [
                {
                    "actual_delivery_date": invoice.invoice_date,
                    "delivery_location_vals": {
                        "delivery_address_vals": self._get_partner_address_vals(
                            shipping_address
                        ),
                    },
                }
            ]
        return res
