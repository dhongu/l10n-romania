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
