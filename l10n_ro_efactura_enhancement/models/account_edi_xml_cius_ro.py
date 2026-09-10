# ©  2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


import logging

from odoo import models
from odoo.tools.safe_eval import safe_eval

from odoo.addons.account_edi_ubl_cii.models.account_edi_common import FloatFmt

_logger = logging.getLogger(__name__)

DEFAULT_VAT = "0000000000000"

# Limita de caractere impusa de CIUS-RO pentru Avizul de plata (BT-83), verificata de
# schematronul ANAF prin regula BR-RO-L140: „Numarul maxim permis de caractere pentru
# Aviz de plata (BT-83) este 140.
# Tichet 9441: valoarea era 200, preluata din corespondenta tichetului 9369 si nu din
# raspunsul ANAF, deci facturile lungi ramaneau respinse chiar si dupa trunchiere.
PAYMENT_ID_MAX_LEN = 140

# Limita CIUS-RO pentru Adresa - Linia 2 (BT-51 cumparator / BT-76 livrare) si pentru
# Punctul de contact al Cumparatorului (BT-56), verificata prin regula BR-RO-L100.
# Tichet 9441: le trunchiem doar pe acestea, fiindca doar pentru ele avem respingeri
# reale de la ANAF -- nu presupunem limite pentru celelalte campuri de adresa.
ADDRESS_LINE_MAX_LEN = 100
CONTACT_NAME_MAX_LEN = 100


def _has_vat(vat):
    return bool(vat and len(vat) > 1)


class AccountEdiUBL(models.AbstractModel):
    _name = "account.edi.ubl"
    _inherit = "account.edi.ubl"
    # do not remove


class AccountEdiXmlUBLRO(models.AbstractModel):
    _inherit = "account.edi.xml.ubl_ro"

    def _ubl_add_payment_means_nodes(self, vals):
        # EXTENDS account.edi.xml.ubl_ro
        res = super()._ubl_add_payment_means_nodes(vals)
        self._l10n_ro_truncate_payment_identifiers(vals["document_node"])
        return res

    def _ubl_get_partner_address_node(self, vals, partner):
        # EXTENDS account.edi.xml.ubl_ro
        node = super()._ubl_get_partner_address_node(vals, partner)
        self._l10n_ro_truncate_node_text(node, "cbc:AdditionalStreetName", ADDRESS_LINE_MAX_LEN)
        return node

    def _ubl_add_party_contact_node(self, vals):
        # EXTENDS account.edi.xml.ubl_ro
        res = super()._ubl_add_party_contact_node(vals)
        self._l10n_ro_truncate_node_text(vals["party_node"].get("cac:Contact"), "cbc:Name", CONTACT_NAME_MAX_LEN)
        return res

    def _l10n_ro_truncate_node_text(self, node, tag, max_len):
        """Scurteaza la ``max_len`` textul unui nod, daca exista si e prea lung.

        ANAF respinge factura cu BR-RO-L100 cand Adresa - Linia 2 (BT-51 / BT-76) sau
        Punctul de contact al Cumparatorului (BT-56) depasesc 100 de caractere. Cazuri
        reale intalnite: ``street2`` folosit de clientii din magazin drept camp de
        observatii, si denumiri de institutii mai lungi de 100 de caractere.
        """
        if not isinstance(node, dict):
            return
        value = (node.get(tag) or {}).get("_text")
        if isinstance(value, str) and len(value) > max_len:
            node[tag]["_text"] = value[:max_len].rstrip()

    def _l10n_ro_shorten_payment_identifier(self, value):
        """Scurteaza o referinta de plata la PAYMENT_ID_MAX_LEN caractere.

        Taie la ultimul separator " - " care mai incape, ca sa nu rupa in mijlocul
        unui cod de comanda - referintele sunt concatenate cu acest separator, iar
        reconcilierea automata sparge exact pe el. Daca nu exista un separator
        rezonabil de aproape de limita, taie brut.
        """
        truncated = value[:PAYMENT_ID_MAX_LEN]
        separator_index = truncated.rfind(" - ")
        if separator_index >= PAYMENT_ID_MAX_LEN // 2:
            return truncated[:separator_index]
        return truncated.rstrip()

    def _l10n_ro_truncate_payment_identifiers(self, document_node):
        """ANAF respinge e-Factura (BR-RO-L140) daca cbc:PaymentID / cbc:InstructionID
        depasesc PAYMENT_ID_MAX_LEN caractere.

        Tichet 9369: pe facturile care consolideaza multe comenzi, ``payment_reference``
        poate depasi singur limita (referinte concatenate pentru reconciliere), iar
        factura ramane blocata la transmitere. Scurtam aici, in generator, ca sa nu
        depindem de curatarea manuala a campului pe fiecare factura.
        """
        nodes = document_node.get("cac:PaymentMeans") or []
        if isinstance(nodes, dict):
            nodes = [nodes]
        for node in nodes:
            if not isinstance(node, dict):
                continue
            for tag in ("cbc:PaymentID", "cbc:InstructionID"):
                value = (node.get(tag) or {}).get("_text")
                if isinstance(value, str) and len(value) > PAYMENT_ID_MAX_LEN:
                    node[tag]["_text"] = self._l10n_ro_shorten_payment_identifier(value)

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

    def _ubl_add_legal_monetary_total_prepaid_payable_amount_node(self, vals, in_foreign_currency=True):
        """Cat timp factura nu e stinsa, declara PrepaidAmount = 0 si PayableAmount = totalul.

        Standardul Odoo scrie PayableAmount = amount_residual si PrepaidAmount =
        amount_total - amount_residual, adica suma de plata din XML depinde de ce
        plati sunt alocate in Odoo in momentul trimiterii la ANAF.

        Nu e ce vrem la livrarile cu plata la ramburs (cash on delivery): incasarea
        se inregistreaza in Odoo pe fluxul de curierat, dar factura trimisa
        cumparatorului trebuie sa ceara tot totalul, altfel ajunge la ANAF cu o
        suma de plata mai mica (uneori zero) decat cea pe care o plateste efectiv
        clientul curierului.

        Pe 18.0 acelasi comportament era implementat in _get_invoice_monetary_total_vals;
        in 19.0 acel hook (si _add_invoice_monetary_total_vals) nu mai e apelat de nimeni.
        """
        # EXTENDS account.edi.xml.ubl_bis3
        super()._ubl_add_legal_monetary_total_prepaid_payable_amount_node(vals, in_foreign_currency=in_foreign_currency)
        if not self._is_document(vals, "invoice", "credit_note", "self_invoice", "self_credit_note"):
            return
        invoice = vals.get("invoice")
        if not invoice or invoice.payment_state == "paid":
            return

        currency = vals["currency_id"] if in_foreign_currency else vals["company_currency"]
        if in_foreign_currency:
            amount_total = invoice.amount_total
        else:
            amount_total = invoice.amount_total_signed * -invoice.direction_sign

        node = vals["legal_monetary_total_node"]
        node["cbc:PrepaidAmount"]["_text"] = FloatFmt(0.0, min_dp=currency.decimal_places)
        node["cbc:PayableAmount"]["_text"] = FloatFmt(amount_total, min_dp=currency.decimal_places)

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

    def _get_invoice_node(self, vals):
        # EXTENDS account.edi.xml.ubl_20 (prin ubl_bis3)
        # deltatech_account_edi_ubl_advice (daca e instalat) seteaza cac:DespatchDocumentReference
        # (BT-16) concatenand numele tuturor pickingurilor "done" ale liniilor de vanzare facturate,
        # fara nicio limita de lungime. Pe comenzi cu multe livrari partiale acumulate in timp
        # (tichet 9429), lista poate depasi cele 200 de caractere admise de ANAF pentru BT-16 ->
        # factura e respinsa la transmitere cu eroarea BR-RO-L200. Aceeasi regula e deja aplicata
        # pentru BT-13/BT-14 in _ubl_add_order_reference_node.
        # Suprascriem aici _get_invoice_node (nu _add_invoice_header_nodes) ca sa nu depindem de
        # ordinea de incarcare fata de deltatech_account_edi_ubl_advice: la momentul in care
        # super() se termina, document_node e deja complet construit, inclusiv despatch reference
        # daca acel modul e instalat; daca nu e instalat, cheia lipseste si nu facem nimic.
        document_node = super()._get_invoice_node(vals)
        despatch_id = document_node.get("cac:DespatchDocumentReference", {}).get("cbc:ID", {})
        value = despatch_id.get("_text")
        if value and len(value) > 200:
            despatch_id["_text"] = self._l10n_ro_truncate_despatch_advice(value)
        return document_node

    def _l10n_ro_truncate_despatch_advice(self, value, max_len=200):
        """Trunchiaza lista de referinte de pickinguri (separate prin ", ") la max_len
        caractere, pastrand cat mai multe referinte intregi in loc sa taie in mijlocul
        unui nume de picking.
        """
        names = value.split(", ")
        kept = []
        length = 0
        for name in names:
            extra = len(name) + (2 if kept else 0)
            if length + extra > max_len:
                break
            kept.append(name)
            length += extra
        return ", ".join(kept) if kept else value[:max_len]

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
