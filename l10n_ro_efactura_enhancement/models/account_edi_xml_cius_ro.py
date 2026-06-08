# ©  2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


import logging

from odoo import _, models
from odoo.tools import float_is_zero
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

DEFAULT_VAT = "0000000000000"


def _has_vat(vat):
    return bool(vat and len(vat) > 1)


class AccountEdiUBL(models.AbstractModel):
    _name = "account.edi.ubl"
    _inherit = "account.edi.ubl"
    # do not remove


class AccountEdiXmlUBLRO(models.AbstractModel):
    _inherit = "account.edi.xml.ubl_ro"

    def _get_invoice_line_price_vals(self, line):
        # old helper
        vals = super()._get_invoice_line_price_vals(line)
        if float_is_zero(vals["price_amount"], precision_rounding=0.01):
            vals["price_amount"] = 0.0
        return vals

    def _get_address_node(self, vals):
        # New helper: put default street if not present
        res = super()._get_address_node(vals)
        if not res["cbc:StreetName"]["_text"]:
            res["cbc:StreetName"] = {"_text": "Principala"}
        return res

    def _get_partner_party_vals(self, partner, role):
        # old helper
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

        # partner = partner.commercial_partner_id

        postal_address = vals.get("postal_address_vals", {})
        if not postal_address.get("street_name", False):
            postal_address["street_name"] = "Principala"

        if partner.state_id and partner.state_id.code == "B":
            if "city_id" in partner._fields and partner.city_id:
                postal_address["city_name"] = partner.city_id.name.upper()

        if postal_address.get("country_subentity", False) == "RO-B":
            if "SECTOR" not in (postal_address.get("city_name") or "").upper():
                postal_code = postal_address.get("postal_zone", False)
                if postal_code and postal_code[0] == "0" and postal_code[1] in ["1", "2", "3", "4", "5", "6"]:
                    postal_address["city_name"] = "SECTOR" + postal_code[1]
                else:
                    postal_address["city_name"] = "SECTOR1"
            postal_address["city_name"] = (
                (postal_address.get("city_name") or "").upper().replace(" ", "").replace("UL", "")
            )
            if partner.city != postal_address["city_name"]:
                partner.write({"city": postal_address["city_name"]})

        if not partner.is_company:
            vals["endpoint_id"] = "0000000000000"
        return vals

    def _get_partner_party_tax_scheme_vals_list(self, partner, role):
        # old helper
        # EXTENDS account.edi.xml.ubl_21
        vals_list = super()._get_partner_party_tax_scheme_vals_list(partner, role)
        partner = partner.commercial_partner_id
        for vals in vals_list:
            if not partner.is_company:
                vals["company_id"] = "0000000000000"
        return vals_list

    def _get_partner_party_legal_entity_vals_list(self, partner):
        # old helper
        val_list = super()._get_partner_party_legal_entity_vals_list(partner)
        partner = partner.commercial_partner_id
        if not partner.is_company:
            for vals in val_list:
                if vals.get("commercial_partner") == partner:
                    vals["company_id"] = "0000000000000"
        return val_list

    def _get_invoice_line_item_vals(self, line, taxes_vals):
        # old helper
        vals = super()._get_invoice_line_item_vals(line, taxes_vals)
        name = vals.get("name") or "n/a"
        vals["name"] = name[:100]
        description = vals.get("description") or vals["name"]
        if "\n" in description:
            description_array = description.split("\n")
            description = "\n".join(description_array[1:])
        vals["description"] = description[:200]
        return vals

    def get_description(self, line):
        """
        Returns only description
        :param line: invoice line
        :return: description
        """
        line_name = line.name or ""
        if line_name:
            product = line.product_id
            product_name = product.display_name or product.name or ""
            if product and product_name and product_name in line_name:
                if line_name != product_name:
                    return line_name.replace(product_name, "", 1).strip()
                else:
                    return line_name
            else:
                return line_name
        else:
            if line.product_id:
                return line.product_id.name or ""
            else:
                return line_name

    def _add_document_line_item_nodes(self, line_node, vals):
        # New helper extension: keep base behavior, then optionally use free-text line description
        res = super()._add_document_line_item_nodes(line_node, vals)

        # Ensure structure exists and apply safe truncation for product-based defaults
        product = vals["base_line"]["product_id"]
        item = line_node.setdefault("cac:Item", {})
        desc = item.setdefault("cbc:Description", {})
        name = item.setdefault("cbc:Name", {})
        # Default from product, truncated
        if not desc.get("_text"):
            default_desc = product.description_sale or product.name or ""
            desc["_text"] = (default_desc or "")[:200]
        else:
            desc["_text"] = desc["_text"][:200]
        if not name.get("_text"):
            name["_text"] = (product.name or "")[:100]
        else:
            name["_text"] = name["_text"][:100]
        # Apply behavior only when system parameter is enabled
        get_param = self.env["ir.config_parameter"].sudo().get_param
        use_line_desc = safe_eval(get_param("efactura.use_line_description", "False"))

        if use_line_desc:
            line = vals["base_line"]["record"]
            if getattr(line, "name", None):
                description = self.get_description(line)
                if description:
                    desc["_text"] = description[:200]
                    name["_text"] = description[:100]
        line_node["cac:Item"]["cbc:Description"]["_text"] = desc["_text"]
        line_node["cac:Item"]["cbc:Name"]["_text"] = name["_text"]
        if item.get("cac:AdditionalItemProperty"):
            item["cac:AdditionalItemProperty"] = []
        return res

    def _add_invoice_line_item_nodes(self, line_node, vals):
        # New helper
        # Restrict name and description length
        # Replace name with description if present
        # Call the proper parent hook for invoice line items
        res = super()._add_invoice_line_item_nodes(line_node, vals)

        # Apply behavior only when system parameter is enabled
        get_param = self.env["ir.config_parameter"].sudo().get_param
        use_line_desc = safe_eval(get_param("efactura.use_line_description", "False"))
        replace_unit_uom = safe_eval(get_param("efactura.replace_unit_uom", "False"))
        item = line_node.setdefault("cac:Item", {})
        desc = item.setdefault("cbc:Description", {})
        name = item.setdefault("cbc:Name", {})
        if use_line_desc:
            line = vals["base_line"]["record"]
            # Normalize and truncate the line description
            if getattr(line, "name", None):
                description = self.get_description(line)
                if description:
                    desc["_text"] = description[:200]
                    name["_text"] = description[:100]

        # When a free-text line description is used, drop additional properties
        if item.get("cac:AdditionalItemProperty"):
            item["cac:AdditionalItemProperty"] = []
        if desc:
            line_node["cac:Item"]["cbc:Description"]["_text"] = desc["_text"][:200]
        if name:
            line_node["cac:Item"]["cbc:Name"]["_text"] = name["_text"][:100]
        # replace line uom if parameter is set for unit
        if (
            replace_unit_uom
            and line_node["cbc:InvoicedQuantity"]["unitCode"]
            and line_node["cbc:InvoicedQuantity"]["unitCode"] == "C62"
        ):
            line_node["cbc:InvoicedQuantity"]["unitCode"] = replace_unit_uom
        return res

    def _export_invoice_vals(self, invoice):
        # old helper
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
        if "despatch_advice" in vals_list["vals"] and vals_list["vals"]["despatch_advice"]:
            vals_list["vals"]["despatch_advice"] = vals_list["vals"]["despatch_advice"][:200]
        if "pos_order_ids" in invoice._fields and invoice.pos_order_ids:
            if vals_list["vals"]["document_type_code"] == 380:
                vals_list["vals"]["document_type_code"] = 751
        return vals_list

    def _add_invoice_header_nodes(self, document_node, vals):
        """New helper"""
        res = super()._add_invoice_header_nodes(document_node, vals)
        if (
            document_node.get("cac:OrderReference")
            and document_node["cac:OrderReference"].get("cbc:SalesOrderID")
            and document_node["cac:OrderReference"]["cbc:SalesOrderID"].get("_text")
        ):
            document_node["cac:OrderReference"]["cbc:SalesOrderID"]["_text"] = document_node["cac:OrderReference"][
                "cbc:SalesOrderID"
            ]["_text"][:200]

        if document_node.get("cbc:Note"):
            if isinstance(document_node["cbc:Note"], list):
                for note in document_node["cbc:Note"]:
                    if isinstance(note, dict) and note.get("_text"):
                        note["_text"] = note["_text"][:300]
            if isinstance(document_node["cbc:Note"], dict) and document_node["cbc:Note"].get("_text"):
                document_node["cbc:Note"]["_text"] = document_node["cbc:Note"]["_text"][:300]

        invoice = vals["invoice"]
        if (
            "pos_order_ids" in invoice._fields
            and invoice.pos_order_ids
            and document_node.get("cbc:InvoiceTypeCode")
            and document_node["cbc:InvoiceTypeCode"].get("_text") == 380
        ):
            document_node["cbc:InvoiceTypeCode"] = {"_text": 751}

        return res


class AccountEdiXmlUBLBIS3(models.AbstractModel):
    _inherit = "account.edi.xml.ubl_bis3"

    def _add_invoice_payment_means_nodes(self, document_node, vals):
        # New helper:
        # Build multiple cac:PaymentMeans nodes (code 42), one per eligible bank,
        # when the multi-bank parameter is enabled for customer invoices.
        # Otherwise, keep the default BIS3 behavior (single node).
        res = super()._add_invoice_payment_means_nodes(document_node, vals)

        get_param = self.env["ir.config_parameter"].sudo().get_param
        get_all_banks = safe_eval(get_param("efactura.get_all_banks", "False"))
        invoice = vals["invoice"]

        if get_all_banks and invoice.move_type == "out_invoice":
            domain = [("l10n_ro_print_report", "=", True), ("currency_id", "=", invoice.currency_id.id)]
            banks = self.env["res.partner.bank"].search(domain)

            if banks:
                payment_means_nodes = []
                for bank in banks:
                    node = {
                        "cbc:PaymentMeansCode": {
                            "_text": 42,
                        },
                        # 'cbc:PaymentDueDate': {'_text': invoice.invoice_date_due or invoice.invoice_date},
                        "cac:PayeeFinancialAccount": self._get_financial_account_node({**vals, "partner_bank": bank}),
                    }
                    if node["cac:PayeeFinancialAccount"] and node["cac:PayeeFinancialAccount"].get(
                        "cac:FinancialInstitutionBranch"
                    ):
                        node["cac:PayeeFinancialAccount"].pop("cac:FinancialInstitutionBranch")
                    payment_means_nodes.append(node)

                # Replace any existing single node with the list of nodes
                document_node["cac:PaymentMeans"] = payment_means_nodes

        return res

    def _invoice_constraints_cen_en16931_ubl_new(self, invoice, vals):
        """
        New helper:
        Adjust only the BR-61 behavior to allow multiple cac:PaymentMeans
        All other constraints are inherited from the core implementation.
        """
        # If multiple cac:PaymentMeans are present (list), call super() with a
        # temporary view that uses only the first payment means node so that the
        # core implementation (which expects a dict) does not crash.
        payment_means = vals["document_node"].get("cac:PaymentMeans")
        if isinstance(payment_means, list):
            first_pm = payment_means[0] if payment_means else {}
            document_node_copy = dict(vals["document_node"])
            document_node_copy["cac:PaymentMeans"] = [first_pm]
            vals_for_super = {**vals, "document_node": document_node_copy}
            constraints = super()._invoice_constraints_cen_en16931_ubl_new(invoice, vals_for_super)
        else:
            constraints = super()._invoice_constraints_cen_en16931_ubl_new(invoice, vals)

        get_param = self.env["ir.config_parameter"].sudo().get_param
        get_all_banks = safe_eval(get_param("efactura.get_all_banks", "False"))

        # Determine payment means code (from the first node if multiple)
        pm_node = None
        if isinstance(payment_means, list):
            pm_node = payment_means[0] if payment_means else {}
        else:
            pm_node = payment_means or {}
        pm_code = pm_node.get("cbc:PaymentMeansCode", {}).get("_text")

        if pm_code in (30, 58) and get_all_banks and invoice.move_type == "out_invoice":
            accounts = pm_node.get("cac:PayeeFinancialAccount")
            has_account = False
            if isinstance(accounts, list):
                has_account = any(bool(acc) for acc in accounts)
            else:
                has_account = bool(accounts)

            constraints["cen_en16931_payment_account_identifier"] = (
                None
                if has_account
                else _("For credit transfer, at least one payee financial account should be provided.")
            )

        return constraints

    def _get_invoice_monetary_total_vals(
        self, invoice, taxes_vals, line_extension_amount, allowance_total_amount, charge_total_amount
    ):
        # old helper
        vals = super()._get_invoice_monetary_total_vals(
            invoice, taxes_vals, line_extension_amount, allowance_total_amount, charge_total_amount
        )

        if invoice.payment_state != "paid":
            vals["prepaid_amount"] = 0.0
            vals["payable_amount"] = invoice.amount_total

        return vals

    def _invoice_constraints_peppol_en16931_ubl_new(self, invoice, vals):
        res = super()._invoice_constraints_peppol_en16931_ubl_new(invoice, vals)
        if "ubl_peppol_en16931-r010" in res:
            res.pop("ubl_peppol_en16931-r010")
        return res

    def _ubl_add_accounting_customer_party_tax_scheme_nodes(self, vals):
        # EXTENDS account.edi.xml.ubl_bis3, for boolean not iterable error
        partner = vals["party_vals"]["partner"]
        commercial_partner = partner.commercial_partner_id
        if not _has_vat(commercial_partner.vat) and not commercial_partner.is_company:
            commercial_partner.company_registry = DEFAULT_VAT
        res = super()._ubl_add_accounting_customer_party_tax_scheme_nodes(vals)
        if vals["party_node"]["cac:PartyTaxScheme"]:
            if (
                commercial_partner.country_id.code == "RO"
                and "RO" not in vals["party_node"]["cac:PartyTaxScheme"][0]["cbc:CompanyID"]["_text"]
                and commercial_partner.is_company
                and commercial_partner.vat
            ):
                vals["party_node"]["cac:PartyTaxScheme"][0]["cbc:CompanyID"]["_text"] = "RO" + commercial_partner.vat
        return res

    def _ubl_add_order_reference_node(self, vals):
        # linit salesorder names
        res = super()._ubl_add_order_reference_node(vals)
        order_ref_node = vals.get("document_node", {}).get("cac:OrderReference")
        if order_ref_node and order_ref_node.get("cbc:SalesOrderID", {}).get("_text"):
            order_ref_node["cbc:SalesOrderID"]["_text"] = order_ref_node["cbc:SalesOrderID"]["_text"][:200]
        return res

    def _ubl_add_accounting_supplier_party_legal_entity_nodes(self, vals):
        res = super()._ubl_add_accounting_supplier_party_legal_entity_nodes(vals)
        if (
            vals.get("party_node", {}).get("cac:PartyTaxScheme", {})
            and vals.get("party_vals").get("partner")
            and hasattr(vals.get("party_vals").get("partner"), "nrc")
            and vals.get("party_vals").get("partner").nrc
        ):
            vals["party_node"]["cac:PartyLegalEntity"] = [
                {
                    "cbc:RegistrationName": {"_text": vals.get("party_vals").get("partner").name},
                    "cbc:CompanyID": {"_text": vals.get("party_vals").get("partner").nrc},
                }
            ]
        return res

    def _ubl_add_accounting_customer_party_legal_entity_nodes(self, vals):
        res = super()._ubl_add_accounting_customer_party_legal_entity_nodes(vals)
        if (
            vals.get("party_node", {}).get("cac:PartyTaxScheme", {})
            and vals.get("party_vals").get("partner")
            and hasattr(vals.get("party_vals").get("partner"), "nrc")
            and vals.get("party_vals").get("partner").nrc
        ):
            vals["party_node"]["cac:PartyLegalEntity"] = [
                {
                    "cbc:RegistrationName": {"_text": vals.get("party_vals").get("partner").name},
                    "cbc:CompanyID": {"_text": vals.get("party_vals").get("partner").nrc},
                }
            ]
        return res
