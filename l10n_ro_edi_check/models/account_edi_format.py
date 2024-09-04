# Copyright (C) 2022 Dorin Hongu <dhongu(@)gmail(.)com
# Copyright (C) 2022 NextERP Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models
from odoo.tools.safe_eval import safe_eval

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

        res = super(AccountEdiXmlCIUSRO, self)._find_value(xpath, xml_element, namespaces=namespaces)

        return res


class AccountEdiXmlBis3(models.AbstractModel):
    _inherit = "account.edi.xml.ubl_bis3"

    def _get_invoice_payment_means_vals_list(self, invoice):
        # rewrite function to send all bank accounts printed in invoice, if parameter set
        get_param = self.env["ir.config_parameter"].sudo().get_param
        get_all_banks = get_param("l10n_ro_edi_check.get_all_banks", "False")
        get_all_banks = safe_eval(get_all_banks)
        if get_all_banks and invoice.move_type == "out_invoice":
            domain = [("l10n_ro_print_report", "=", True), ("currency_id", "=", invoice.company_id.currency_id.id)]
            banks = self.env["res.partner.bank"].search(domain)
            if banks:
                vals = []
                for bank in banks:
                    val = {
                        "payment_means_code": 30,
                        "payee_financial_account_vals": self._get_financial_account_vals(bank),
                    }
                    vals.append(val)
                return vals
            else:
                return super()._get_invoice_payment_means_vals_list(invoice)
        else:
            return super()._get_invoice_payment_means_vals_list(invoice)
