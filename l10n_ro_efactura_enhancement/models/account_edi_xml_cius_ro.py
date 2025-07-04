# ©  2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


import logging

from odoo import models
from odoo.tools import float_is_zero
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class AccountEdiXmlUBLRO(models.AbstractModel):
    _inherit = "account.edi.xml.ubl_ro"

    def _get_invoice_line_price_vals(self, line):
        vals = super()._get_invoice_line_price_vals(line)
        if float_is_zero(vals["price_amount"], precision_rounding=0.01):
            vals["price_amount"] = 0.0
        return vals

    def _get_partner_party_vals(self, partner, role):
        # EXTENDS account.edi.xml.ubl_21

        _logger.info("partner %s (%s)", partner.name, partner.id)

        if not partner.country_code:
            _logger.warning(
                "Partner %s (%s) has no country_code set, using 'RO' as default.",
                partner.name,
                partner.id,
            )

        if not partner.state_id.code:
            _logger.warning(
                "Partner %s (%s) has no state_id set, using 'B' as default.",
                partner.name,
                partner.id,
            )

        vals = super()._get_partner_party_vals(partner, role)

        partner = partner.commercial_partner_id

        postal_address = vals.get("postal_address_vals", {})
        if not postal_address.get("street_name", False):
            postal_address["street_name"] = "Principala"

        if postal_address.get("country_subentity", False) == "RO-B":
            if "SECTOR" not in postal_address.get("city_name", "").upper():
                postal_code = postal_address.get("postal_zone", False)
                if postal_code and postal_code[0] == "0" and postal_code[1] in ["1", "2", "3", "4", "5", "6"]:
                    postal_address["city_name"] = "SECTOR" + postal_code[1]
                else:
                    postal_address["city_name"] = "SECTOR1"

        if not partner.is_company:
            vals["endpoint_id"] = "0000000000000"
        return vals

    def _get_partner_party_tax_scheme_vals_list(self, partner, role):
        # EXTENDS account.edi.xml.ubl_21
        vals_list = super()._get_partner_party_tax_scheme_vals_list(partner, role)
        partner = partner.commercial_partner_id
        for vals in vals_list:
            if not partner.is_company:
                vals["company_id"] = "0000000000000"
        return vals_list

    def _get_partner_party_legal_entity_vals_list(self, partner):
        val_list = super()._get_partner_party_legal_entity_vals_list(partner)
        partner = partner.commercial_partner_id
        if not partner.is_company:
            for vals in val_list:
                if vals.get("commercial_partner") == partner:
                    vals["company_id"] = "0000000000000"
        return val_list

    def _get_invoice_line_item_vals(self, line, taxes_vals):
        vals = super()._get_invoice_line_item_vals(line, taxes_vals)
        name = vals.get("name") or "n/a"
        vals["name"] = name[:100]
        description = vals.get("description") or vals["name"]
        vals["description"] = description[:200]

        return vals

    def _export_invoice_vals(self, invoice):
        vals_list = super()._export_invoice_vals(invoice)
        # get_param = self.env["ir.config_parameter"].sudo().get_param
        # clean_chars = safe_eval(get_param("efactura.clean_name", False))
        # if not clean_chars:
        #     return vals_list
        # if "vals" in vals_list and vals_list["vals"] and "id" in vals_list["vals"] and vals_list["vals"]["id"]:
        #     vals_list["vals"]["id"] = vals_list["vals"]["id"].replace("/", "")
        if vals_list["vals"]["sales_order_id"]:
            vals_list["vals"]["sales_order_id"] = vals_list["vals"]["sales_order_id"][:200]
        if vals_list["vals"]["order_reference"]:
            vals_list["vals"]["order_reference"] = vals_list["vals"]["order_reference"][:200]
        if "pos_order_ids" in invoice._fields and invoice.pos_order_ids:
            if vals_list["vals"]["document_type_code"] == 380:
                vals_list["vals"]["document_type_code"] = 751
        return vals_list

    def _export_invoice_constraints(self, invoice, vals):
        partner = invoice.commercial_partner_id

        if partner.country_id.code == "RO" and not partner.is_company:
            # if not partner.vat:
            #     partner.with_context(no_vat_validation=True).write({"vat": "0000000000000"})
            if not partner.street:
                partner.write({"street": "Principala"})

            if partner.state_id and partner.state_id.code == "B":
                if not partner.city:
                    partner.write({"city": "SECTOR1"})
                if "SECTOR" not in partner.city.upper():
                    partner.write({"city": "SECTOR1"})

        constraints = super()._export_invoice_constraints(invoice, vals)

        if not partner.is_company:
            constraints.pop("ciusro_customer_tax_identifier_required", False)

        return constraints

    def _get_invoice_payment_means_vals_list(self, invoice):
        # add accounts according to the invoice currency and l10n_ro_print_report
        get_param = self.env["ir.config_parameter"].sudo().get_param
        get_all_banks = get_param("efactura.get_all_banks", "False")
        get_all_banks = safe_eval(get_all_banks)
        if get_all_banks and invoice.move_type == "out_invoice":
            domain = [("l10n_ro_print_report", "=", True), ("currency_id", "=", invoice.currency_id.id)]
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
