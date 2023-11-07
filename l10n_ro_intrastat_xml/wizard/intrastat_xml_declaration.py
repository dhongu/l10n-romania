# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import base64
import xml.etree.ElementTree as ET

from odoo import _, fields, models
from odoo.exceptions import RedirectWarning, UserError

unicode = str

INTRASTAT_XMLNS = "http://www.intrastat.ro/xml/InsSchema"


class IntrastatDeclaration(models.TransientModel):
    """
    Intrastat XML Declaration
    """

    _name = "l10n.ro.intrastat.xml.declaration"
    _description = "Intrastat XML Declaration"

    def _get_def_monthyear(self):
        td = fields.Date.context_today(self)
        return td.strftime("%Y"), td.strftime("%m")

    def _get_def_month(self):
        return self._get_def_monthyear()[1]

    def _get_def_year(self):
        return self._get_def_monthyear()[0]

    def _get_country_ver(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        return get_param("l10n_ro_intrastat_xml.country_ver", default="2021")

    def _get_eu_country_ver(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        return get_param("l10n_ro_intrastat_xml.eu_country_ver", default="2021")

    def _get_cn8(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        return get_param("l10n_ro_intrastat_xml.cn8", default="2023")

    def _get_mode_of_transport_ver(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        return get_param("l10n_ro_intrastat_xml.mode_of_transport_ver", default="2005")

    def _get_delivery_terms_ver(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        return get_param("l10n_ro_intrastat_xml.delivery_terms_ver", default="2021")

    def _get_nature_of_transaction_a_ver(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        return get_param("l10n_ro_intrastat_xml.nature_of_transaction_a_ver", default="2010")

    def _get_nature_of_transaction_b_ver(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        return get_param("l10n_ro_intrastat_xml.nature_of_transaction_b_ver", default="2010")

    def _get_county_ver(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        return get_param("l10n_ro_intrastat_xml.county_ver", default="1")

    def _get_locality_ver(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        return get_param("l10n_ro_intrastat_xml.locality_ver", default="06/2006")

    def _get_unit_ver(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        return get_param("l10n_ro_intrastat_xml.unit_ver", default="1")

    name = fields.Char("File Name", default="intrastat.xml")
    month = fields.Selection(
        [
            ("01", "January"),
            ("02", "February"),
            ("03", "March"),
            ("04", "April"),
            ("05", "May"),
            ("06", "June"),
            ("07", "July"),
            ("08", "August"),
            ("09", "September"),
            ("10", "October"),
            ("11", "November"),
            ("12", "December"),
        ],
        "Month",
        required=True,
        default=_get_def_month,
    )
    year = fields.Char("Year", size=4, required=True, default=_get_def_year)

    type = fields.Selection(
        [("arrivals", "Arrivals"), ("dispatches", "Dispatches")],
        default="arrivals",
        string="Type",
        required=True,
    )

    contact_id = fields.Many2one("res.partner", "Contact", domain=[("is_company", "=", False)], required=True)
    file_save = fields.Binary("Intrastat Report File", readonly=True)
    state = fields.Selection([("draft", "Draft"), ("download", "Download")], string="State", default="draft")

    display_versions = fields.Boolean("Display Versions", default=False)
    cn8 = fields.Char("CN8", size=4, required=True, default=_get_cn8)

    country_ver = fields.Char("CountryVer", size=4, required=True, default=_get_country_ver)
    eu_country_ver = fields.Char("EuCountryVer", size=4, required=True, default=_get_eu_country_ver)
    mode_of_transport_ver = fields.Char("ModeOfTransportVer", size=4, required=True, default=_get_mode_of_transport_ver)
    delivery_terms_ver = fields.Char("DeliveryTermsVer", size=4, required=True, default=_get_delivery_terms_ver)
    nature_of_transaction_a_ver = fields.Char(
        "NatureOfTransactionAVer", size=4, required=True, default=_get_nature_of_transaction_a_ver
    )
    nature_of_transaction_b_ver = fields.Char(
        "NatureOfTransactionBVer", size=4, required=True, default=_get_nature_of_transaction_b_ver
    )
    county_ver = fields.Char("CountyVer", size=4, required=True, default=_get_county_ver)
    locality_ver = fields.Char("LocalityVer", size=4, required=True, default=_get_locality_ver)
    unit_ver = fields.Char("UnitVer", size=4, required=True, default=_get_unit_ver)

    enterprise = fields.Boolean("Enterprise", default=False, compute="_compute_enterprise")

    def _compute_enterprise(self):
        for rec in self:
            rec.enterprise = self.env["ir.module.module"].search(
                [("name", "=", "account_intrastat"), ("state", "=", "installed")]
            )

    def _company_warning(self, translated_msg):
        """
        Raise a error with custom message,
        asking user to configure company settings
        """
        action = self.env.ref("base.action_res_company_form")
        raise RedirectWarning(translated_msg, action.id, _("Go to company configuration screen"))

    def create_xml(self):
        """
        Creates xml that is to be exported and sent to estate for partner vat intra.
        :return: Value for next action.
        :rtype: dict
        """

        set_param = self.env["ir.config_parameter"].sudo().set_param
        set_param("l10n_ro_intrastat_xml.country_ver", self.country_ver)
        set_param("l10n_ro_intrastat_xml.eu_country_ver", self.eu_country_ver)
        set_param("l10n_ro_intrastat_xml.cn8", self.cn8)
        set_param("l10n_ro_intrastat_xml.mode_of_transport_ver", self.mode_of_transport_ver)
        set_param("l10n_ro_intrastat_xml.delivery_terms_ver", self.delivery_terms_ver)
        set_param("l10n_ro_intrastat_xml.nature_of_transaction_a_ver", self.nature_of_transaction_a_ver)
        set_param("l10n_ro_intrastat_xml.nature_of_transaction_b_ver", self.nature_of_transaction_b_ver)
        set_param("l10n_ro_intrastat_xml.county_ver", self.county_ver)
        set_param("l10n_ro_intrastat_xml.locality_ver", self.locality_ver)
        set_param("l10n_ro_intrastat_xml.unit_ver", self.unit_ver)

        decl_datas = self
        company = self.env.user.company_id
        if not (company.partner_id and company.partner_id.country_id and company.partner_id.country_id.id):
            self._company_warning(
                _("The country of your company is not set, " "please make sure to configure it first."),
            )

        if not company.vat:
            self._company_warning(
                _("The VAT of your company is not set, " "please make sure to configure it first."),
            )
        if len(decl_datas.year) != 4:
            raise UserError(_("Year must be 4 digits number (YYYY)"))

        # Create root declaration

        decl = ET.Element("InsNewArrival") if decl_datas.type == "arrivals" else ET.Element("InsNewDispatch")

        decl.set("SchemaVersion", "1.0")
        decl.set("xmlns", INTRASTAT_XMLNS)

        CodeVersion = ET.SubElement(decl, "InsCodeVersions")
        tag = ET.SubElement(CodeVersion, "CountryVer")
        tag.text = self.country_ver
        tag = ET.SubElement(CodeVersion, "EuCountryVer")
        tag.text = self.eu_country_ver
        tag = ET.SubElement(CodeVersion, "CnVer")
        tag.text = self.cn8
        tag = ET.SubElement(CodeVersion, "ModeOfTransportVer")
        tag.text = self.mode_of_transport_ver
        tag = ET.SubElement(CodeVersion, "DeliveryTermsVer")
        tag.text = self.delivery_terms_ver
        tag = ET.SubElement(CodeVersion, "NatureOfTransactionAVer")
        tag.text = self.nature_of_transaction_a_ver
        tag = ET.SubElement(CodeVersion, "NatureOfTransactionBVer")
        tag.text = self.nature_of_transaction_b_ver
        tag = ET.SubElement(CodeVersion, "CountyVer")
        tag.text = self.county_ver
        tag = ET.SubElement(CodeVersion, "LocalityVer")
        tag.text = self.locality_ver
        tag = ET.SubElement(CodeVersion, "UnitVer")
        tag.text = self.unit_ver

        # Add Administration elements
        header = ET.SubElement(decl, "InsDeclarationHeader")
        tag = ET.SubElement(header, "VatNr")
        vat = company.vat
        if vat[:2] == "RO":
            vat = "00" + vat[2:]
        if vat[:2] != "00":
            vat = "00" + vat

        tag.text = vat

        tag = ET.SubElement(header, "FirmName")
        tag.text = company.partner_id.name

        tag = ET.SubElement(header, "RefPeriod")
        tag.text = decl_datas.year + "-" + decl_datas.month

        last_name = decl_datas.contact_id.name.split(" ")[-1]
        first_name = " ".join(decl_datas.contact_id.name.split(" ")[:-1])

        ContactPerson = ET.SubElement(header, "ContactPerson")
        tag = ET.SubElement(ContactPerson, "LastName")
        tag.text = last_name
        tag = ET.SubElement(ContactPerson, "FirstName")
        tag.text = first_name
        tag = ET.SubElement(ContactPerson, "Phone")
        tag.text = decl_datas.contact_id.phone
        tag = ET.SubElement(ContactPerson, "Position")
        tag.text = decl_datas.contact_id.function

        self._get_lines(decl_datas, dispatchmode=(decl_datas.type != "arrivals"), decl=decl)

        # Get xml string with declaration
        data_file = ET.tostring(decl, encoding="UTF-8", method="xml")

        # change state of the wizard
        self.write(
            {
                "name": "intrastat_{}{}.xml".format(decl_datas.year, decl_datas.month),
                "file_save": base64.encodebytes(data_file),
                "state": "download",
            },
        )
        return {
            "name": _("Save"),
            "context": self.env.context,
            "view_mode": "form",
            "res_model": "l10n.ro.intrastat.xml.declaration",
            "type": "ir.actions.act_window",
            "target": "new",
            "res_id": self.id,
        }

    def _get_lines(self, decl_datas, dispatchmode, decl):
        company = self.env.user.company_id

        mode1 = "out_invoice" if dispatchmode else "in_invoice"
        mode2 = "out_refund" if dispatchmode else "in_refund"

        entries = []
        # care sunt liniile de facturi relevante pentru delcaratia de intrastat
        sqlreq = """
    select
        inv_line.id
    from
        account_move_line inv_line
        join account_move inv on inv_line.move_id=inv.id
        left join res_country on res_country.id = inv.intrastat_country_id
        left join res_partner on res_partner.id = inv.partner_id
        left join res_country countrypartner on
                        countrypartner.id = res_partner.country_id
        join product_product on inv_line.product_id=product_product.id
        join product_template on product_product.product_tmpl_id=product_template.id
    where
        inv.state = 'posted'
        and inv.company_id=%(company)s
        and not product_template.type='service'
        and (res_country.intrastat=true or (inv.intrastat_country_id is null
                                            and countrypartner.intrastat=true))
        and ((res_country.code is not null and not res_country.code=%(country)s)
             or (res_country.code is null and countrypartner.code is not null
             and not countrypartner.code=%(country)s))
        and inv.move_type in (%(mode1)s, %(mode2)s)
        and to_char(inv.invoice_date, 'YYYY')=%(year)s
        and to_char(inv.invoice_date, 'MM')=%(month)s
        and exclude_from_invoice_tab = false

            """

        self.env.cr.execute(
            sqlreq,
            {
                "company": company.id,
                "country": company.partner_id.country_id.code,
                "mode1": mode1,
                "mode2": mode2,
                "year": decl_datas.year,
                "month": decl_datas.month,
            },
        )

        lines = self.env.cr.fetchall()
        invoice_lines_ids = [rec[0] for rec in lines]
        invoice_lines = self.env["account.move.line"].browse(invoice_lines_ids)

        for inv_line in invoice_lines:
            invoice = inv_line.move_id
            # Check type of transaction
            if "intrastat_transaction_id" in invoice._fields:
                if invoice.intrastat_transaction_id:
                    intrastat_transaction = invoice.intrastat_transaction_id
                else:
                    intrastat_transaction = company.intrastat_transaction_id
            else:  # enterprise
                intrastat_transaction = inv_line.intrastat_transaction_id

            if not intrastat_transaction:
                raise UserError(_("Invoice %s without Intrastat Trasaction") % invoice.name)

            if intrastat_transaction.parent_id:
                TrCodeA = intrastat_transaction.parent_id.code
                TrCodeB = intrastat_transaction.code
            else:
                TrCodeA = intrastat_transaction.code
                TrCodeB = ""

            if self.enterprise:
                ModeOfTransport = (
                    invoice.intrastat_transport_mode_id.code or company.intrastat_transport_mode_id.code or False
                )
            else:
                ModeOfTransport = invoice.transport_mode_id.code or company.transport_mode_id.code or False

            if not ModeOfTransport:
                raise UserError(_("Invoice %s without Transport Mode") % invoice.name)

            DeliveryTerms = invoice.invoice_incoterm_id.code or company.incoterm_id.code or False

            if not DeliveryTerms:
                raise UserError(_("Invoice %s without incoterm") % invoice.name)

            Country = invoice.intrastat_country_id.code or invoice.partner_id.country_id.code or False

            if not Country:
                raise UserError(_("Invoice %s without intrastat country") % invoice.name)

            if not inv_line.move_id.commercial_partner_id.is_company:
                continue

            if not inv_line.move_id.commercial_partner_id.vat:
                raise UserError(
                    _('Partner "%s" has no VAT code, please configure it') % inv_line.move_id.partner_id.display_name
                )
            if inv_line.move_id.commercial_partner_id.vat:
                VatPrefix = Country
                PartnerVatNr = inv_line.move_id.commercial_partner_id.vat.replace(VatPrefix, "")
                PartnerVatNr = PartnerVatNr.replace("EL", "")
            else:
                PartnerVatNr = ""

            if inv_line.product_id.country_id:
                OriginCountry = inv_line.product_id.country_id.code
            else:
                OriginCountry = Country

            # Check commodity codes
            intrastat_id = inv_line.product_id.search_intrastat_code()
            if intrastat_id and intrastat_id.code:
                Cn8Code = intrastat_id.code
                suppl_unit_code = intrastat_id.suppl_unit_code
            else:
                raise UserError(
                    _('Product "%s" has no intrastat code, please configure it') % inv_line.product_id.display_name
                )

            amount = inv_line.price_subtotal
            amount = invoice.currency_id._convert(
                from_amount=amount,
                to_currency=company.currency_id,
                company=company,
                date=invoice.invoice_date,
            )

            supply_units = inv_line.product_uom_id._compute_quantity(inv_line.quantity, inv_line.product_id.uom_id)
            weight = (inv_line.product_id.weight or 0.0) * supply_units

            entries += [
                {
                    "Cn8Code": Cn8Code,
                    "SupplUnitCode": suppl_unit_code,
                    "OriginCountry": OriginCountry,
                    "Country": Country,
                    "TrCodeA": TrCodeA,
                    "TrCodeB": TrCodeB,
                    "DeliveryTerms": DeliveryTerms,
                    "ModeOfTransport": ModeOfTransport,
                    "amount": amount,
                    "weight": weight,
                    "supply_units": supply_units,
                    "PartnerVatNr": PartnerVatNr,
                }
            ]

        numlgn = 0
        for entry in entries:
            numlgn += 1
            # amounts = entries[linekey]

            if dispatchmode:
                item = ET.SubElement(decl, "InsDispatchItem")
            else:
                item = ET.SubElement(decl, "InsArrivalItem")
            item.set("OrderNr", unicode(numlgn))

            tag = ET.SubElement(item, "Cn8Code")
            tag.text = unicode(entry["Cn8Code"])

            tag = ET.SubElement(item, "InvoiceValue")
            tag.text = unicode(int(round(entry["amount"], 0)))

            tag = ET.SubElement(item, "StatisticalValue")
            tag.text = unicode(int(round(entry["amount"], 0)))

            tag = ET.SubElement(item, "NetMass")
            tag.text = unicode(int(round(entry["weight"], 0)))

            if entry["SupplUnitCode"]:
                SupplUnitsInfo = ET.SubElement(item, "InsSupplUnitsInfo")
                tag = ET.SubElement(SupplUnitsInfo, "SupplUnitCode")
                tag.text = unicode(entry["SupplUnitCode"])
                tag = ET.SubElement(SupplUnitsInfo, "QtyInSupplUnits")
                tag.text = unicode(int(round(entry["supply_units"], 0)))

            tag = ET.SubElement(item, "NatureOfTransactionACode")
            tag.text = unicode(entry["TrCodeA"])
            if entry["TrCodeB"]:
                tag = ET.SubElement(item, "NatureOfTransactionBCode")
                tag.text = unicode(entry["TrCodeB"])

            tag = ET.SubElement(item, "DeliveryTermsCode")
            tag.text = unicode(entry["DeliveryTerms"])

            tag = ET.SubElement(item, "ModeOfTransportCode")
            tag.text = unicode(entry["ModeOfTransport"])

            tag = ET.SubElement(item, "CountryOfOrigin")
            tag.text = unicode(entry["Country"])

            if dispatchmode:
                tag = ET.SubElement(item, "CountryOfDestination")
                tag.text = unicode(entry["Country"])
                tag = ET.SubElement(item, "PartnerCountryCode")
                country = entry["Country"]
                if country == "NL":
                    country = "QV"
                tag.text = unicode(country)
                tag = ET.SubElement(item, "PartnerVatNr")
                tag.text = unicode(entry["PartnerVatNr"])

            else:
                tag = ET.SubElement(item, "CountryOfConsignment")
                tag.text = unicode(entry["Country"])

        return decl
