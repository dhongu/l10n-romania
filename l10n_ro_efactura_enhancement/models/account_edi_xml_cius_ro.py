# ©  2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


import logging

from odoo import models
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

    def get_description(self, line):
        """
        Returns only the additional description of the line, i.e. the line
        name without the product name. Empty string when the line has no
        description beyond the product itself — in that case the (optional)
        cbc:Description tag must not be rendered at all.
        :param line: invoice line
        :return: description
        """
        line_name = line.name or ""
        if not line_name:
            return ""
        product = line.product_id
        product_name = product.display_name or product.name or ""
        if product and product_name and product_name in line_name:
            return line_name.replace(product_name, "", 1).strip()
        return line_name

    def _add_document_line_item_nodes(self, line_node, vals):
        # New helper extension: keep base behavior, then optionally use free-text line description
        res = super()._add_document_line_item_nodes(line_node, vals)

        # Ensure structure exists and apply safe truncation for product-based defaults
        product = vals["base_line"]["product_id"]
        item = line_node.setdefault("cac:Item", {})
        # Odoo 19 core (commit aeb41ca7) poate seta aceste noduri pe None
        # (ca tag-ul gol să fie sărit la serializare); setdefault ar întoarce
        # atunci None și am crăpa la atribuirea "_text". Normalizăm la dict.
        if not isinstance(item.get("cbc:Description"), dict):
            item["cbc:Description"] = {}
        if not isinstance(item.get("cbc:Name"), dict):
            item["cbc:Name"] = {}
        desc = item["cbc:Description"]
        name = item["cbc:Name"]
        # Default from product, truncated. Fără fallback pe product.name:
        # numele produsului merge doar în cbc:Name; dacă nu există o descriere
        # reală, tag-ul cbc:Description (opțional, BT-154) trebuie omis —
        # serializatorul sare nodurile fără _text.
        if not desc.get("_text"):
            desc["_text"] = (product.description_sale or "")[:200] or None
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
            # Descrierea suplimentară a liniei merge în cbc:Name; Description
            # rămâne doar când textul depășește 100 de caractere (Name e
            # trunchiat) — altfel ar dubla Name-ul și e omisă mai jos.
            description = self.get_description(line) if getattr(line, "name", None) else ""
            desc["_text"] = description[:200] if description else None
            if description:
                name["_text"] = description[:100]
        # Descrierea nu trebuie să dubleze numele articolului.
        if desc.get("_text") and desc["_text"] == name.get("_text"):
            desc["_text"] = None
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
        # Vezi nota din _add_document_line_item_nodes: core-ul poate seta nodurile
        # pe None, deci nu ne putem baza pe setdefault.
        if not isinstance(item.get("cbc:Description"), dict):
            item["cbc:Description"] = {}
        if not isinstance(item.get("cbc:Name"), dict):
            item["cbc:Name"] = {}
        desc = item["cbc:Description"]
        name = item["cbc:Name"]
        if use_line_desc:
            line = vals["base_line"]["record"]
            # Core-ul a pus deja line.name (= display_name produs) în
            # Description, deci suprascriem inclusiv cu None ca tag-ul să fie
            # omis când linia nu are descriere proprie. Descrierea merge în
            # cbc:Name; Description rămâne doar când textul depășește 100 de
            # caractere (Name e trunchiat) — altfel ar dubla Name-ul și e
            # omisă mai jos.
            description = self.get_description(line) if getattr(line, "name", None) else ""
            desc["_text"] = description[:200] if description else None
            if description:
                name["_text"] = description[:100]

        # When a free-text line description is used, drop additional properties
        if item.get("cac:AdditionalItemProperty"):
            item["cac:AdditionalItemProperty"] = []
        # Descrierea nu trebuie să dubleze numele articolului.
        if desc.get("_text") and desc["_text"] == name.get("_text"):
            desc["_text"] = None
        # Truncare la limitele ANAF; dacă un nod a rămas gol îl punem înapoi pe
        # None ca serializatorul să sară peste tag-ul (opțional) gol.
        if desc.get("_text"):
            desc["_text"] = desc["_text"][:200]
        else:
            item["cbc:Description"] = None
        if name.get("_text"):
            name["_text"] = name["_text"][:100]
        else:
            item["cbc:Name"] = None
        # replace line uom if parameter is set for unit
        if (
            replace_unit_uom
            and line_node["cbc:InvoicedQuantity"]["unitCode"]
            and line_node["cbc:InvoicedQuantity"]["unitCode"] == "C62"
        ):
            line_node["cbc:InvoicedQuantity"]["unitCode"] = replace_unit_uom
        return res

    def _export_invoice_constraints(self, invoice, vals):
        """New helper"""
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


class AccountEdiXmlUBLBIS3(models.AbstractModel):
    _inherit = "account.edi.xml.ubl_bis3"

    def _ubl_add_payment_means_nodes(self, vals):
        # EXTENDS account.edi.xml.ubl_bis3
        # add accounts according to the invoice currency and l10n_ro_print_report
        get_param = self.env["ir.config_parameter"].sudo().get_param
        get_all_banks = safe_eval(get_param("efactura.get_all_banks", "False"))
        invoice = vals.get("invoice")
        if get_all_banks and invoice and invoice.move_type == "out_invoice":
            domain = [("l10n_ro_print_report", "=", True), ("currency_id", "=", invoice.currency_id.id)]
            banks = self.env["res.partner.bank"].search(domain)
            if banks:
                document_node = vals["document_node"]
                nodes = document_node.setdefault("cac:PaymentMeans", [])
                nodes.clear()
                for bank in banks:
                    node = {
                        "cbc:PaymentMeansCode": {"_text": 30, "name": "credit transfer"},
                        "cbc:PaymentID": {"_text": invoice.payment_reference or invoice.name},
                        "cac:PayeeFinancialAccount": self._ubl_get_payment_means_payee_financial_account_node_from_partner_bank(
                            vals, bank
                        ),
                    }
                    nodes.append(node)
                return
        super()._ubl_add_payment_means_nodes(vals)

    def _add_invoice_monetary_total_vals(self, vals):
        # EXTENDS account.edi.xml.ubl_bis3
        res = super()._add_invoice_monetary_total_vals(vals)
        invoice = vals.get("invoice")
        if invoice and invoice.payment_state != "paid":
            document_node = vals.get("document_node", {})
            monetary_total = document_node.get("cac:LegalMonetaryTotal", {})
            if monetary_total:
                monetary_total["cbc:PrepaidAmount"] = {"_text": 0.0}
                monetary_total["cbc:PayableAmount"] = {"_text": invoice.amount_total}
        return res

    def _invoice_constraints_peppol_en16931_ubl(self, invoice, vals):
        res = super()._invoice_constraints_peppol_en16931_ubl(invoice, vals)
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
        # limit salesorder names (BT-14) and purchase order reference (BT-13) to 200 chars
        # ANAF rule BR-RO-L200 rejects BT-13/BT-14 longer than 200 characters
        res = super()._ubl_add_order_reference_node(vals)
        order_ref_node = vals.get("document_node", {}).get("cac:OrderReference")
        if order_ref_node:
            if order_ref_node.get("cbc:SalesOrderID", {}).get("_text"):
                order_ref_node["cbc:SalesOrderID"]["_text"] = order_ref_node["cbc:SalesOrderID"]["_text"][:200]
            if order_ref_node.get("cbc:ID", {}).get("_text"):
                order_ref_node["cbc:ID"]["_text"] = order_ref_node["cbc:ID"]["_text"][:200]
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
