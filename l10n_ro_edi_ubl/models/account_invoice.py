# ©  2015-2019 Terrabit
# See README.rst file on addons root folder for license details


import base64
import logging

from lxml import etree

from odoo import api, models
from odoo.tools import float_is_zero, float_round

logger = logging.getLogger(__name__)


UOM_TO_UNECE_CODE = {
    'uom.product_uom_unit': 'C62',
    'uom.product_uom_dozen': 'DZN',
    'uom.product_uom_kgm': 'KGM',
    'uom.product_uom_gram': 'GRM',
    'uom.product_uom_day': 'DAY',
    'uom.product_uom_hour': 'HUR',
    'uom.product_uom_ton': 'TNE',
    'uom.product_uom_meter': 'MTR',
    # 'uom.product_uom_km': 'KTM',
    'uom.product_uom_cm': 'CMT',
    'uom.product_uom_litre': 'LTR',
    'uom.product_uom_cubic_meter': 'MTQ',
    'uom.product_uom_lb': 'LBR',
    'uom.product_uom_oz': 'ONZ',
    'uom.product_uom_inch': 'INH',
    'uom.product_uom_foot': 'FOT',
    'uom.product_uom_mile': 'SMI',
    'uom.product_uom_floz': 'OZA',
    'uom.product_uom_qt': 'QT',
    'uom.product_uom_gal': 'GLL',
    'uom.product_uom_cubic_inch': 'INQ',
    'uom.product_uom_cubic_foot': 'FTQ',
}


class AccountInvoice(models.Model):
    _name = "account.invoice"
    _inherit = ["account.invoice", "base.ro.ubl"]

    @api.multi
    def _ubl_add_header(self, parent_node, ns, version="2.1"):
        ubl_version = etree.SubElement(parent_node, ns["cbc"] + "UBLVersionID")
        ubl_version.text = version

        elem = etree.SubElement(parent_node, ns["cbc"] + "CustomizationID")
        elem.text = "urn:cen.eu:en16931:2017#compliant#urn:efactura.mfinante.ro:CIUS-RO:1.0.1"

        doc_id = etree.SubElement(parent_node, ns["cbc"] + "ID")
        doc_id.text = self.number

        # elem = etree.SubElement(parent_node, "CopyIndicator")
        # elem.text = "FALSE"

        issue_date = etree.SubElement(parent_node, ns["cbc"] + "IssueDate")
        issue_date.text = str(self.date_invoice)
        type_code = etree.SubElement(parent_node, ns["cbc"] + "InvoiceTypeCode")
        if self.type == "out_invoice":
            type_code.text = "380"
        elif self.type == "out_refund":
            type_code.text = "381"
        if self.comment:
            note = etree.SubElement(parent_node, ns["cbc"] + "Note")
            note.text = self.comment
        doc_currency = etree.SubElement(parent_node, ns["cbc"] + "DocumentCurrencyCode")
        doc_currency.text = self.currency_id.name
        doc_currency = etree.SubElement(parent_node, ns["cbc"] + "TaxCurrencyCode")
        doc_currency.text = self.currency_id.name
        # doc_currency = etree.SubElement(parent_node, ns["cbc"] + "PricingCurrencyCode")
        # doc_currency.text = self.currency_id.name
        # doc_currency = etree.SubElement(parent_node, ns["cbc"] + "PaymentCurrencyCode")
        # doc_currency.text = self.currency_id.name
        # doc_currency = etree.SubElement(parent_node, ns["cbc"] + "PaymentAlternativeCurrencyCode")
        # doc_currency.text = self.currency_id.name

        # line_count = etree.SubElement(parent_node, ns["cbc"] + "LineCountNumeric")
        # line_count.text = str(len(self.invoice_line_ids))

    @api.multi
    def _ubl_add_order_reference(self, parent_node, ns, version="2.1"):
        self.ensure_one()
        if self.name:
            order_ref = etree.SubElement(parent_node, ns["cac"] + "OrderReference")
            order_ref_id = etree.SubElement(order_ref, ns["cbc"] + "ID")
            order_ref_id.text = self.name

    @api.multi
    def _ubl_get_contract_document_reference_dict(self):
        """Result: dict with key = Doc Type Code, value = ID"""
        self.ensure_one()
        return {}

    @api.multi
    def _ubl_add_contract_document_reference(self, parent_node, ns, version="2.1"):
        self.ensure_one()
        cdr_dict = self._ubl_get_contract_document_reference_dict()
        for doc_type_code, doc_id in cdr_dict.items():
            cdr = etree.SubElement(parent_node, ns["cac"] + "ContractDocumentReference")
            cdr_id = etree.SubElement(cdr, ns["cbc"] + "ID")
            cdr_id.text = doc_id
            cdr_type_code = etree.SubElement(cdr, ns["cbc"] + "DocumentTypeCode")
            cdr_type_code.text = doc_type_code

    @api.multi
    def _ubl_add_attachments(self, parent_node, ns, version="2.1"):
        embed_pdf_in_ubl_xml_invoice = True  # self.company_id.embed_pdf_in_ubl_xml_invoice
        if embed_pdf_in_ubl_xml_invoice and not self._context.get("no_embedded_pdf"):
            docu_reference = etree.SubElement(parent_node, ns["cac"] + "AdditionalDocumentReference")
            docu_reference_id = etree.SubElement(docu_reference, ns["cbc"] + "ID")
            docu_reference_id.text = "Invoice-" + self.number + ".pdf"
            attach_node = etree.SubElement(docu_reference, ns["cac"] + "Attachment")
            binary_node = etree.SubElement(
                attach_node, ns["cbc"] + "EmbeddedDocumentBinaryObject", mimeCode="application/pdf"
            )
            ctx = dict()
            ctx["no_embedded_ubl_xml"] = True
            pdf_inv = self.with_context(ctx).env.ref("account.account_invoices").render_qweb_pdf(self.ids)[0]
            binary_node.text = base64.b64encode(pdf_inv)

    @api.multi
    def _ubl_add_legal_monetary_total(self, parent_node, ns, version="2.1"):
        monetary_total = etree.SubElement(parent_node, ns["cac"] + "LegalMonetaryTotal")
        cur_name = self.currency_id.name
        prec = self.currency_id.decimal_places
        line_total = etree.SubElement(monetary_total, ns["cbc"] + "LineExtensionAmount", currencyID=cur_name)
        line_total.text = "%0.*f" % (prec, self.amount_untaxed)
        tax_excl_total = etree.SubElement(monetary_total, ns["cbc"] + "TaxExclusiveAmount", currencyID=cur_name)
        tax_excl_total.text = "%0.*f" % (prec, self.amount_untaxed)
        tax_incl_total = etree.SubElement(monetary_total, ns["cbc"] + "TaxInclusiveAmount", currencyID=cur_name)
        tax_incl_total.text = "%0.*f" % (prec, self.amount_total)
        prepaid_amount = etree.SubElement(monetary_total, ns["cbc"] + "PrepaidAmount", currencyID=cur_name)
        prepaid_value = self.amount_total - self.residual
        prepaid_amount.text = "%0.*f" % (prec, prepaid_value)
        payable_amount = etree.SubElement(monetary_total, ns["cbc"] + "PayableAmount", currencyID=cur_name)
        payable_amount.text = "%0.*f" % (prec, self.residual)


    def _get_uom_unece_code(self, line):
        """
        list of codes: https://docs.peppol.eu/poacc/billing/3.0/codelist/UNECERec20/
        or https://unece.org/fileadmin/DAM/cefact/recommendations/bkup_htm/add2c.htm (sorted by letter)
        """
        xmlid = line.uom_id.get_external_id()
        if xmlid and line.uom_id.id in xmlid:
            return UOM_TO_UNECE_CODE.get(xmlid[line.uom_id.id], 'C62')
        return 'C62'

    @api.multi
    def _ubl_add_invoice_line(self, parent_node, iline, line_number, ns, version="2.1"):
        cur_name = self.currency_id.name
        line_root = etree.SubElement(parent_node, ns["cac"] + "InvoiceLine", nsmap={None: ""})
        dpo = self.env["decimal.precision"]
        qty_precision = dpo.precision_get("Product Unit of Measure")
        price_precision = dpo.precision_get("Product Price")
        account_precision = self.currency_id.decimal_places
        line_id = etree.SubElement(line_root, ns["cbc"] + "ID")
        line_id.text = str(line_number)

        uom_unece_code = self._get_uom_unece_code(iline)

        # uom_unece_code = False
        # uom_id is not a required field on account.invoice.line
        # if iline.uom_id and iline.uom_id.name:  # iline.uom_id.unece_code:
        #     uom_unece_code = iline.uom_id.name[:3]  # iline.uom_id.unece_code
        #     if uom_unece_code == "Uni":
        #         uom_unece_code = "C62"  # asta este cosul pentru bucata
        if uom_unece_code:
            quantity = etree.SubElement(line_root, ns["cbc"] + "InvoicedQuantity", unitCode=uom_unece_code)
        else:
            quantity = etree.SubElement(line_root, ns["cbc"] + "InvoicedQuantity")
        qty = iline.quantity
        quantity.text = "%0.*f" % (qty_precision, qty)

        line_amount = etree.SubElement(line_root, ns["cbc"] + "LineExtensionAmount", currencyID=cur_name)
        line_amount.text = "%0.*f" % (account_precision, iline.price_subtotal)
        # line_amount = etree.SubElement(line_root, ns["cbc"] + "TaxInclusiveAmount")
        # line_amount.text = "%0.*f" % (account_precision, iline.price_subtotal)
        # elem = etree.SubElement(line_root, ns["cbc"] + "AccountingCostCode")
        # elem.text = "MCH"

        self._ubl_add_invoice_line_tax_total(cur_name, iline, line_root, ns, version=version)
        self._ubl_add_item(
            iline.name,
            iline.product_id,
            line_root,
            ns,
            type_="sale",
            seller=iline.invoice_id.partner_id,
            version=version,
        )
        price_node = etree.SubElement(line_root, ns["cac"] + "Price")
        price_amount = etree.SubElement(price_node, ns["cbc"] + "PriceAmount", currencyID=cur_name)
        price_unit = 0.0
        # Use price_subtotal/qty to compute price_unit to be sure
        # to get a *tax_excluded* price unit
        if not float_is_zero(qty, precision_digits=qty_precision):
            price_unit = float_round(iline.price_subtotal / float(qty), precision_digits=price_precision)
        price_amount.text = "%0.*f" % (price_precision, price_unit)
        if uom_unece_code:
            base_qty = etree.SubElement(price_node, ns["cbc"] + "BaseQuantity", unitCode=uom_unece_code)
        else:
            base_qty = etree.SubElement(price_node, ns["cbc"] + "BaseQuantity")
        base_qty.text = "%0.*f" % (qty_precision, 1)

        # elem = etree.SubElement(price_node, ns["cbc"] + "PriceTypeCode")
        # elem.text = "AAB"

    def _ubl_add_invoice_line_tax_total(self, currency_code, iline, parent_node, ns, version="2.1"):
        cur_name = self.currency_id.name
        prec = self.currency_id.decimal_places
        # tax_total_node = etree.SubElement(parent_node, ns["cac"] + "TaxTotal")
        price = iline.price_unit * (1 - (iline.discount or 0.0) / 100.0)
        res_taxes = iline.invoice_line_tax_ids.compute_all(
            price, quantity=iline.quantity, product=iline.product_id, partner=self.partner_id
        )
        tax_total = float_round(res_taxes["total_included"] - res_taxes["total_excluded"], precision_digits=prec)
        # tax_amount_node = etree.SubElement(tax_total_node, ns["cbc"] + "TaxAmount", currencyID=currency_code)
        # tax_amount_node.text = "%0.*f" % (prec, tax_total)
        # if not float_is_zero(tax_total, precision_digits=prec):
        #     for res_tax in res_taxes["taxes"]:
        #         tax = self.env["account.tax"].browse(res_tax["id"])
        #         # we don't have the base amount in res_tax :-(
        #         self._ubl_add_tax_subtotal(False, res_tax["amount"], tax, cur_name, tax_total_node, ns, version=version)

    def _ubl_add_tax_total(self, currency_code, xml_root, ns, version="2.1"):
        self.ensure_one()
        cur_name = self.currency_id.name
        tax_total_node = etree.SubElement(xml_root, ns["cac"] + "TaxTotal")
        tax_amount_node = etree.SubElement(tax_total_node, ns["cbc"] + "TaxAmount", currencyID=currency_code)
        prec = self.currency_id.decimal_places
        tax_amount_node.text = "%0.*f" % (prec, self.amount_tax)
        if not float_is_zero(self.amount_tax, precision_digits=prec):
            for tline in self.tax_line_ids:
                self._ubl_add_tax_subtotal(
                    tline.base, tline.amount, tline.tax_id, cur_name, tax_total_node, ns, version=version
                )

    @api.model
    def _ubl_add_payment_means(
        self, payer_banks, payee_banks, payment_mode, date_due, parent_node, ns, payment_identifier=None, version="2.1"
    ):
        pay_means = etree.SubElement(parent_node, ns["cac"] + "PaymentMeans")

        if date_due:
            pay_due_date = etree.SubElement(pay_means, ns["cbc"] + "PaymentDueDate")
            pay_due_date.text = date_due

        for partner_bank in payer_banks:
            payee_fin_account = etree.SubElement(pay_means, ns["cac"] + "PayerFinancialAccount")

            financial_inst_id = etree.SubElement(payee_fin_account, ns["cbc"] + "ID")
            financial_inst_id.text = partner_bank.acc_number

            financial_inst_branch = etree.SubElement(payee_fin_account, ns["cac"] + "FinancialInstitutionBranch")
            financial_inst = etree.SubElement(financial_inst_branch, ns["cac"] + "FinancialInstitution")

            financial_name = etree.SubElement(financial_inst, ns["cac"] + "Name")
            financial_name.text = partner_bank.bank_id.name
            break
        for partner_bank in payee_banks:
            payee_fin_account = etree.SubElement(pay_means, ns["cac"] + "PayeeFinancialAccount")

            financial_inst_id = etree.SubElement(payee_fin_account, ns["cbc"] + "ID")
            financial_inst_id.text = partner_bank.acc_number

            financial_inst_branch = etree.SubElement(payee_fin_account, ns["cac"] + "FinancialInstitutionBranch")
            financial_inst = etree.SubElement(financial_inst_branch, ns["cac"] + "FinancialInstitution")

            financial_name = etree.SubElement(financial_inst, ns["cac"] + "Name")
            financial_name.text = partner_bank.bank_id.name
            break

    @api.model
    def _ubl_get_nsmap_namespace(self, doc_name, version="2.1"):
        nsmap, ns = super(AccountInvoice, self)._ubl_get_nsmap_namespace(doc_name, version)
        nsmap.update(
            {
                "qdt": "urn:oasis:names:specification:ubl:schema:xsd:QualifiedDataTypes-2",
                "udt": "urn:oasis:names:specification:ubl:schema:xsd:UnqualifiedDataTypes-2",
                "ccts": "urn:un:unece:uncefact:documentation:2",
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            }
        )
        return nsmap, ns

    @api.multi
    def generate_invoice_ubl_xml_etree(self, version="2.1"):
        nsmap, ns = self._ubl_get_nsmap_namespace("Invoice-2", version=version)
        xml_root = etree.Element("Invoice", nsmap=nsmap)

        self._ubl_add_header(xml_root, ns, version=version)
        self._ubl_add_order_reference(xml_root, ns, version=version)
        self._ubl_add_contract_document_reference(xml_root, ns, version=version)

        # self._ubl_add_attachments(xml_root, ns, version=version)
        self._ubl_add_supplier_party(False, self.company_id, "AccountingSupplierParty", xml_root, ns, version=version)
        self._ubl_add_customer_party(self.partner_id, False, "AccountingCustomerParty", xml_root, ns, version=version)
        # the field 'partner_shipping_id' is defined in the 'sale' module
        if hasattr(self, "partner_shipping_id") and self.partner_shipping_id:
            self._ubl_add_delivery(self.partner_shipping_id, xml_root, ns)
        # Put paymentmeans block even when invoice is paid ?
        # payment_identifier = self.get_payment_identifier()
        # self._ubl_add_payment_means(self.partner_id.bank_ids, self.company_id.partner_id.bank_ids,
        #                             self.payment_mode_id, self.date_due,
        #                             xml_root, ns, payment_identifier=payment_identifier, version=version)
        if self.payment_term_id:
            self._ubl_add_payment_terms(self.payment_term_id, xml_root, ns, version=version)
        self._ubl_add_tax_total(self.currency_id.name, xml_root, ns, version=version)
        self._ubl_add_legal_monetary_total(xml_root, ns, version=version)

        line_number = 0
        for iline in self.invoice_line_ids:
            if not iline.display_type:
                line_number += 1
                self._ubl_add_invoice_line(xml_root, iline, line_number, ns, version=version)

        return xml_root

    @api.multi
    def generate_ubl_xml_string(self, version="2.1"):
        self.ensure_one()
        assert self.state in ("open", "paid")
        assert self.type in ("out_invoice", "out_refund")
        logger.debug("Starting to generate UBL XML Invoice file")
        lang = self.get_ubl_lang()
        # The aim of injecting lang in context
        # is to have the content of the XML in the partner's lang
        # but the problem is that the error messages will also be in
        # that lang. But the error messages should almost never
        # happen except the first days of use, so it's probably
        # not worth the additional code to handle the 2 langs
        xml_root = self.with_context(lang=lang).generate_invoice_ubl_xml_etree(version=version)
        xml_string = etree.tostring(xml_root, pretty_print=True, encoding="UTF-8", xml_declaration=True)
        self._ubl_check_xml_schema(xml_string, "Invoice", version=version)
        logger.debug("Invoice UBL XML file generated for account invoice ID %d (state %s)", self.id, self.state)
        logger.debug(xml_string.decode("utf-8"))
        return xml_string

    @api.multi
    def get_ubl_filename(self, version="2.1"):
        """This method is designed to be inherited"""
        return "UBL-Invoice-%s-%s.xml" % (version, self.number)

    @api.multi
    def get_ubl_version(self):
        version = self._context.get("ubl_version") or "2.1"
        return version

    @api.multi
    def get_ubl_lang(self):
        return self.partner_id.lang or "en_US"

    @api.multi
    def embed_ubl_xml_in_pdf(self, pdf_content=None, pdf_file=None):
        self.ensure_one()
        if self.type in ("out_invoice", "out_refund") and self.state in ("open", "paid"):
            version = self.get_ubl_version()
            ubl_filename = self.get_ubl_filename(version=version)
            xml_string = self.generate_ubl_xml_string(version=version)
            pdf_content = self.embed_xml_in_pdf(xml_string, ubl_filename, pdf_content=pdf_content, pdf_file=pdf_file)
        return pdf_content

    @api.multi
    def attach_ubl_xml_file_button(self):
        self.ensure_one()
        assert self.type in ("out_invoice", "out_refund")
        assert self.state in ("open", "paid")
        version = self.get_ubl_version()
        xml_string = self.generate_ubl_xml_string(version=version)
        filename = self.get_ubl_filename(version=version)
        ctx = {}
        attach = (
            self.env["ir.attachment"]
            .with_context(ctx)
            .create(
                {
                    "name": filename,
                    "res_id": self.id,
                    "res_model": str(self._name),
                    "datas": base64.b64encode(xml_string),
                    "datas_fname": filename,
                    # I have default_type = 'out_invoice' in context, so 'type'
                    # would take 'out_invoice' value by default !
                    "type": "binary",
                }
            )
        )
        action = self.env["ir.actions.act_window"].for_xml_id("base", "action_attachment")
        action.update({"res_id": attach.id, "views": False, "view_mode": "form,tree"})
        return action
