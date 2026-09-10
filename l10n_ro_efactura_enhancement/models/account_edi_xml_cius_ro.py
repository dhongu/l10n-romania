# ©  2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


import logging
from typing import NamedTuple

from odoo import models
from odoo.tools.safe_eval import safe_eval

from odoo.addons.account_edi_ubl_cii.models.account_edi_common import FloatFmt

_logger = logging.getLogger(__name__)

DEFAULT_VAT = "0000000000000"

# Limitele CIUS-RO de lungime maxima impuse de schematronul ANAF (regulile
# BR-RO-L020 .. BR-RO-L1000). Valorile sunt numar de caractere Unicode, ca in
# semantica ``string-length`` folosita de validator.
#
# Harta e preluata din modulul `l10n_ro_edi_extension` al NextERP Romania
# (LGPL-3, https://github.com/NextERP-Romania/odoo-community) si verificata fata
# de schematronul CIUS-RO v1.0.9 si de validatorul oficial ROeFacturaValidator.
#
# Tichet 9441: pana acum limitele erau constante razlete, iar cea pentru BT-83
# statuse la 200 -- cifra venea din corespondenta unui tichet, nu din raspunsul
# ANAF. Nu adaugam aici nicio limita fara regula in specificatie.
#
# Valoarea unei intrari e fie limita bruta, fie un MaxLen cand ne trebuie o
# strategie de scurtare anume.


class MaxLen(NamedTuple):
    limit: int
    bt: str
    #  "plain"     - taie brut la limita
    #  "separator" - taie la ultimul " - " care incape, ca sa nu rupa un cod
    strategy: str = "plain"


DOCUMENT_LIMITS = {
    ("cbc:ID",): 200,  # BT-1
    ("cac:ContractDocumentReference", "cbc:ID"): 200,  # BT-12
    ("cac:OrderReference", "cbc:ID"): 200,  # BT-13
    ("cac:OrderReference", "cbc:SalesOrderID"): 200,  # BT-14
    ("cac:ReceiptDocumentReference", "cbc:ID"): 200,  # BT-15
    ("cac:DespatchDocumentReference", "cbc:ID"): 200,  # BT-16
    ("cac:OriginatorDocumentReference", "cbc:ID"): 200,  # BT-17
    ("cbc:AccountingCost",): 100,  # BT-19
    ("cac:PaymentTerms", "cbc:Note"): 300,  # BT-20
}

PARTY_LIMITS = {
    ("cac:Party", "cac:PartyLegalEntity", "cbc:RegistrationName"): 200,  # BT-27/44
    ("cac:Party", "cac:PartyName", "cbc:Name"): 200,  # BT-28/45
    ("cac:Party", "cac:PartyLegalEntity", "cbc:CompanyLegalForm"): 1000,  # BT-33
    ("cac:Party", "cac:PostalAddress", "cbc:StreetName"): 150,  # BT-35/50/64
    ("cac:Party", "cac:PostalAddress", "cbc:AdditionalStreetName"): 100,  # BT-36/51/65
    ("cac:Party", "cac:PostalAddress", "cbc:CityName"): 50,  # BT-37/52/66
    ("cac:Party", "cac:PostalAddress", "cbc:PostalZone"): 20,  # BT-38/53/67
    ("cac:Party", "cac:Contact", "cbc:Name"): 100,  # BT-41/56
    ("cac:Party", "cac:Contact", "cbc:Telephone"): 100,  # BT-42/57
    ("cac:Party", "cac:Contact", "cbc:ElectronicMail"): 100,  # BT-43/58
}

DELIVERY_LIMITS = {
    ("cac:DeliveryParty", "cac:PartyName", "cbc:Name"): 200,  # BT-70
    ("cac:DeliveryLocation", "cac:Address", "cbc:StreetName"): 150,  # BT-75
    ("cac:DeliveryLocation", "cac:Address", "cbc:AdditionalStreetName"): 100,  # BT-76
    ("cac:DeliveryLocation", "cac:Address", "cbc:CityName"): 50,  # BT-77
    ("cac:DeliveryLocation", "cac:Address", "cbc:PostalZone"): 20,  # BT-78
}

PAYMENT_MEANS_LIMITS = {
    ("cbc:PaymentMeansCode", "name"): 100,  # BT-82 (atribut)
    # Referintele de plata sunt concatenate cu " - " pentru reconciliere, iar
    # taierea bruta ar rupe un cod de comanda la mijloc: taiem la separator.
    ("cbc:PaymentID",): MaxLen(140, "BT-83", "separator"),
    ("cac:PayeeFinancialAccount", "cbc:Name"): 200,  # BT-85
    ("cac:CardAccount", "cbc:HolderName"): 200,  # BT-88
}

DOC_ALLOWANCE_LIMITS = {
    ("cbc:AllowanceChargeReason",): 100,  # BT-97 / BT-104
}

ADDITIONAL_DOC_REF_LIMITS = {
    ("cbc:ID",): 200,  # BT-18 / BT-122
    ("cbc:DocumentDescription",): 100,  # BT-123
    ("cac:Attachment", "cac:ExternalReference", "cbc:URI"): 200,  # BT-124
    ("cac:Attachment", "cbc:EmbeddedDocumentBinaryObject", "filename"): 200,  # BT-125-2
}

BILLING_REF_LIMITS = {
    ("cac:InvoiceDocumentReference", "cbc:ID"): 200,  # BT-25
}

LINE_LIMITS = {
    ("cbc:AccountingCost",): 100,  # BT-133
    ("cac:AllowanceCharge", "cbc:AllowanceChargeReason"): 100,  # BT-139 / BT-144
    ("cac:Item", "cbc:Name"): 100,  # BT-153
    ("cac:Item", "cbc:Description"): 200,  # BT-154
}

ITEM_PROPERTY_LIMITS = {
    ("cbc:Name",): 50,  # BT-160
    ("cbc:Value",): 100,  # BT-161
}

TAX_EXEMPTION_REASON_MAX_LEN = 100  # BT-120

# BT-22 / BT-127 (cbc:Note pe document si pe linie) NU se trunchiaza: UBL permite
# repetarea elementului, deci le spargem in mai multe noduri de cate 300 de caractere.
NOTE_MAX_LEN = 300  # BR-RO-L300

# Partile pe care se aplica PARTY_LIMITS.
PARTY_KEYS = (
    "cac:AccountingSupplierParty",
    "cac:AccountingCustomerParty",
    "cac:PayeeParty",
    "cac:TaxRepresentativeParty",
)

# Alias pastrat pentru codul si testele care citeau limita individual.
PAYMENT_ID_MAX_LEN = PAYMENT_MEANS_LIMITS[("cbc:PaymentID",)].limit


def _has_vat(vat):
    return bool(vat and len(vat) > 1)


class AccountEdiUBL(models.AbstractModel):
    _name = "account.edi.ubl"
    _inherit = "account.edi.ubl"
    # do not remove


class AccountEdiXmlUBLRO(models.AbstractModel):
    _inherit = "account.edi.xml.ubl_ro"

    def _get_invoice_node(self, vals):
        # EXTENDS account.edi.xml.ubl_ro
        document_node = super()._get_invoice_node(vals)
        self._l10n_ro_apply_length_limits(document_node)
        return document_node

    # -------------------------------------------------------------------------
    # Limitele CIUS-RO de lungime
    # -------------------------------------------------------------------------

    def _l10n_ro_apply_length_limits(self, document_node):
        """Aplica intr-o singura trecere toate limitele BR-RO-L* pe documentul gata construit.

        ANAF respinge factura integral daca un singur camp isi depaseste limita, iar
        campurile vin din date libere (nume de parteneri, adrese, note, descrieri de
        articole), deci nu putem conta pe curatarea manuala. Scurtam la generarea
        XML-ului; datele din Odoo raman neatinse.

        Se aplica la final, pe arborele complet, nu la scrierea fiecarui nod: asa prinde
        si nodurile scrise de alte module sau de standard, nu doar pe cele scrise aici.
        """
        self._l10n_ro_apply_limits(document_node, DOCUMENT_LIMITS)
        self._l10n_ro_split_note_nodes(document_node)  # BT-22

        for party_key in PARTY_KEYS:
            party_root = document_node.get(party_key)
            if party_root is not None:
                self._l10n_ro_apply_limits(party_root, PARTY_LIMITS)

        delivery_root = document_node.get("cac:Delivery")
        if delivery_root is not None:
            self._l10n_ro_apply_limits(delivery_root, DELIVERY_LIMITS)

        for node in self._l10n_ro_iter_children(document_node, "cac:PaymentMeans"):
            self._l10n_ro_apply_limits(node, PAYMENT_MEANS_LIMITS)

        for node in self._l10n_ro_iter_children(document_node, "cac:AllowanceCharge"):
            self._l10n_ro_apply_limits(node, DOC_ALLOWANCE_LIMITS)

        for node in self._l10n_ro_iter_children(document_node, "cac:AdditionalDocumentReference"):
            self._l10n_ro_apply_limits(node, ADDITIONAL_DOC_REF_LIMITS)

        for node in self._l10n_ro_iter_children(document_node, "cac:BillingReference"):
            self._l10n_ro_apply_limits(node, BILLING_REF_LIMITS)

        # BT-120: motivul scutirii / al taxarii inverse, in fiecare cac:TaxCategory.
        for tax_total in self._l10n_ro_iter_children(document_node, "cac:TaxTotal"):
            for subtotal in self._l10n_ro_iter_children(tax_total, "cac:TaxSubtotal"):
                category = subtotal.get("cac:TaxCategory")
                if isinstance(category, dict):
                    self._l10n_ro_apply_limits(category, {("cbc:TaxExemptionReason",): TAX_EXEMPTION_REASON_MAX_LEN})

        for line_tag in ("cac:InvoiceLine", "cac:CreditNoteLine", "cac:DebitNoteLine"):
            for line in self._l10n_ro_iter_children(document_node, line_tag):
                self._l10n_ro_apply_limits(line, LINE_LIMITS)
                self._l10n_ro_split_note_nodes(line)  # BT-127
                item = line.get("cac:Item")
                if isinstance(item, dict):
                    for prop in self._l10n_ro_iter_children(item, "cac:AdditionalItemProperty"):
                        self._l10n_ro_apply_limits(prop, ITEM_PROPERTY_LIMITS)

    def _l10n_ro_apply_limits(self, root, limits):
        """Aplica pe ``root`` harta ``limits`` (cale -> limita sau MaxLen)."""
        for path, spec in limits.items():
            self._l10n_ro_apply_path(root, path, self._l10n_ro_spec(spec))

    @staticmethod
    def _l10n_ro_spec(spec):
        return spec if isinstance(spec, MaxLen) else MaxLen(spec, "")

    @staticmethod
    def _l10n_ro_iter_children(parent, key):
        """Itereaza copiii ``key`` ai lui ``parent``, fie ca sunt un nod sau o lista."""
        if not isinstance(parent, dict):
            return
        value = parent.get(key)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    yield item
        elif isinstance(value, dict):
            yield value

    def _l10n_ro_apply_path(self, root, path, spec):
        """Parcurge ``path`` de la ``root`` si scurteaza valoarea din frunza.

        Nodurile intermediare pot fi liste (se itereaza). Frunza e fie un nod text
        (``{"_text": ...}``), fie un atribut XML -- caz in care calea se termina cu
        numele atributului, iar parintele il tine ca sir.
        """

        def _walk(node, remaining):
            if node is None:
                return
            if isinstance(node, list):
                for item in node:
                    _walk(item, remaining)
                return
            if not isinstance(node, dict):
                return
            if not remaining:
                value = node.get("_text")
                if isinstance(value, str):
                    node["_text"] = self._l10n_ro_shorten_value(value, spec)
                return
            head, *rest = remaining
            child = node.get(head)
            if child is None:
                return
            if not rest and isinstance(child, str):
                node[head] = self._l10n_ro_shorten_value(child, spec)
                return
            _walk(child, rest)

        _walk(root, list(path))

    def _l10n_ro_shorten_value(self, value, spec):
        """Scurteaza ``value`` la ``spec.limit``, daca e cazul.

        Schematronul masoara ``string-length(normalize-space(...))``, deci un text cu
        spatii multiple poate fi mai lung decat limita si totusi valid -- verificam pe
        forma normalizata, ca sa nu taiem mai mult decat cere ANAF.

        Strategia "separator" taie la ultimul " - " care mai incape, ca sa nu rupa in
        mijlocul unui cod de comanda: referintele de plata sunt concatenate cu acest
        separator, iar reconcilierea automata sparge exact pe el. Daca nu exista un
        separator rezonabil de aproape de limita, taie brut.
        """
        if len(" ".join(value.split())) <= spec.limit:
            return value
        truncated = value[: spec.limit]
        if spec.strategy == "separator":
            separator_index = truncated.rfind(" - ")
            if separator_index >= spec.limit // 2:
                return truncated[:separator_index]
        return truncated.rstrip()

    def _l10n_ro_split_note_nodes(self, node):
        """Rescrie ``cbc:Note`` al lui ``node`` in bucati de cel mult NOTE_MAX_LEN.

        Aplicat pe documentul gata construit, ca sa nu depinda de hook-ul care scrie
        nota -- narration-ul facturii, notele de linie sau orice alt modul care le
        completeaza ajung toate aici.
        """
        notes = node.get("cbc:Note")
        if notes is None:
            return
        if isinstance(notes, dict):
            notes = [notes]
        elif isinstance(notes, str):
            notes = [{"_text": notes}]
        if not isinstance(notes, list):
            return
        result = []
        changed = False
        for item in notes:
            text = item.get("_text") if isinstance(item, dict) else item
            if not isinstance(text, str):
                result.append(item)
                continue
            chunks = self._l10n_ro_split_note(text)
            if len(chunks) != 1 or chunks[0] != text:
                changed = True
            result.extend({"_text": chunk} for chunk in chunks)
        if changed:
            node["cbc:Note"] = result

    def _l10n_ro_split_note(self, text):
        """Sparge un text in bucati de cate NOTE_MAX_LEN caractere.

        BT-22 / BT-127 nu se trunchiaza: UBL permite repetarea lui ``cbc:Note``, deci
        pastram tot textul, in mai multe noduri. Taiem pe caractere, nu pe octeti --
        schematronul numara caractere Unicode, iar o limita pe octeti ar rupe inutil
        textele cu diacritice.
        """
        chunks = []
        remaining = text
        while remaining:
            chunk = remaining[:NOTE_MAX_LEN].strip()
            if not chunk:
                break
            chunks.append(chunk)
            remaining = remaining[len(chunk) :].lstrip()
        return chunks

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
