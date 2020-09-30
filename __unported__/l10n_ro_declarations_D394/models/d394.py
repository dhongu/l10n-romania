# -*- coding: utf-8 -*-
# ©  2018 Terrabit
# See README.rst file on addons root folder for license details


from odoo import api, fields, models
from odoo.tools import safe_eval
from odoo import tools
from lxml import etree

OPERATION_TYPE = [
    ("L", "Customer Invoice"),
    ("A", "Supplier Invoice"),
    ("LS", "Special Customer Invoice"),
    ("AS", "Special Supplier Invoice"),
    ("AI", "VAT on Payment Supplier Invoice"),
    ("V", "Inverse Taxation Customer Invoice"),
    ("C", "Inverse Taxation Supplier Invoice"),
    ("N", "Physical Persons Supplier Invoice"),
]


class Declaration(models.Model):
    _inherit = "l10n_ro.declaration"
    code = fields.Selection(selection_add=[("D394", "D394")])


class D394Report(models.TransientModel):
    _name = "l10n_ro.d394_report"
    _description = "Declaration 394"
    _inherit = "l10n_ro.d000_report"
    _code = "D394"

    item_ids = fields.One2many("l10n_ro.d394", "report_id", string="Facturi")
    plaje_ids = fields.One2many("l10n_ro.d394.plaje", "report_id", string="Plaje de facturi")

    def get_sum_bf(self, tax_value):
        baza = 0
        tva = 0
        for item in self.item_ids.filtered(lambda r: r.type == "purchase" and r.tax_value == tax_value):
            baza += item.net
            tva += item.tax

        return baza, tva


    def xml_processing(self, xml_doc):

        for i in ["24", "20", "19", "9", "5"]:
            tag_ab = xml_doc.xpath("//info1/AB" + i)[0]
            tag_ab.clear()
            baza, tva = self.get_sum_bf(" " + i)
            if baza:
                tag = etree.SubElement(tag_ab, "baza")
                tag.text = str(baza)
                tag = etree.SubElement(tag_ab, "tva")
                tag.text = str(tva)

        # tag_plaja1 = xml_doc.xpath('//plaja1')[0]
        tag_facturi2 = xml_doc.xpath("//facturi2")[0]
        tag_facturi2.clear()
        # plaja_parent = tag_plaja1.find('..')  # retrieve the parent
        # plaja_parent.remove(tag_plaja1)
        i = 0
        nr_fact = 0
        for item in self.plaje_ids:
            i += 1
            # plaja = etree.SubElement(plaja_parent, "plaja%s" % i)
            # tag = etree.SubElement(plaja, "serie_i")
            # tag.text = item.serie
            # tag = etree.SubElement(plaja, "nr_i")
            # tag.text = item.journal_id.sequence_id.
            #
            # tag = etree.SubElement(plaja, "serie_f")
            # tag.text = item.serie
            # tag = etree.SubElement(plaja, "nr_f")
            # tag.text = '0'

            nr_fact = int(item.pana_la_nr) - int(item.de_la_nr) + 1

            plaja = etree.SubElement(tag_facturi2, "plaja")
            tag = etree.SubElement(plaja, "serie_i")
            tag.text = item.serie
            tag = etree.SubElement(plaja, "nr_i")
            tag.text = item.de_la_nr

            tag = etree.SubElement(plaja, "serie_f")
            tag.text = item.serie
            tag = etree.SubElement(plaja, "nr_f")
            tag.text = item.pana_la_nr

        tag = etree.SubElement(tag_facturi2, "fact_emise")
        tag.text = str(nr_fact)

        tag_tip1 = xml_doc.xpath("//tip1")[0]

        tag_tip1.clear()
        partner_types = ["1", "2", "3", "4"]
        for partner_type in partner_types:
            item_type = self.item_ids.filtered(lambda r: r.partner_type == partner_type)
            if item_type:
                tag = etree.Element("tip_partener")
                tag.text = partner_type
                tag_tip1.append(tag)
            seq = 1
            for item in item_type:
                sub1 = etree.SubElement(tag_tip1, "sub1")
                sub2 = etree.SubElement(sub1, "sub2")

                tag = etree.SubElement(sub2, "seq2")
                tag.text = str(seq)

                tag = etree.SubElement(sub2, "denP")
                tag.text = item.partner_id.name

                tag = etree.SubElement(sub2, "Tip")
                tag.text = item.operation_type

                if item.operation_type == "N":
                    tag = etree.SubElement(sub2, "tip_document")
                    tag.text = "1"  # factura

                tag = etree.SubElement(sub2, "cota")
                tag.text = item.tax_value

                tag = etree.SubElement(sub2, "cuiP")
                if item.partner_id.vat:
                    tag.text = item.partner_id.vat.replace("RO", "")

                tag = etree.SubElement(sub2, "nrfact")
                tag.text = str(item.invoice_count)

                tag = etree.SubElement(sub2, "baza")
                tag.text = str(round(item.net, 0))

                tag = etree.SubElement(sub2, "tva")
                tag.text = str(round(item.tax, 0))

                seq += 1
            tag = etree.Element("tip1")
            tag_tip1.addnext(tag)
            tag_tip1 = tag

        return xml_doc


    def compute_data_for_report(self):
        self.ensure_one()


        query_inject = """
            WITH
                taxgroups AS (
                SELECT
                    ai.commercial_partner_id as partner_id, count(ai.number) as invoice_count,
                     ai.fiscal_position_id,

                     ai.type, tax_id,
                     to_char(coalesce(tax.amount,0),'99') as tax_value,
                    ai.company_id,
                     sum(coalesce(tax_line.base, amount_total_company_signed)) as net,
                    sum(tax_line.amount) as tax

                           FROM account_move as ai
                            LEFT JOIN account_invoice_tax as tax_line  on tax_line.invoice_id = ai.id
                                     LEFT JOIN account_tax AS tax   ON tax_id = tax.id

                           WHERE
                            ai.type <> 'entry' AND
                           ai.date >= %(date_from)s      AND ai.date <= %(date_to)s
                             and (tax_line.amount  > 0 or  tax_line.amount is null)
                           GROUP BY
                               ai.commercial_partner_id, ai.type, tax_id,
                               tax.amount, ai.fiscal_position_id,    ai.company_id, ai.currency_id
                )
            INSERT INTO
                l10n_ro_d394
                (
                report_id,  create_uid, create_date,
                partner_id,

                invoice_count,
                fiscal_position_id,
                type,
                tax_id,
                tax_value,
                company_id,
                company_currency_id,
                net,
                tax
                )
            SELECT
                %(report_id)s AS report_id, %(uid)s AS create_uid, NOW() AS create_date,
                groups.partner_id,

                groups.invoice_count,
                groups.fiscal_position_id,
                groups.type,
                groups.tax_id,
                groups.tax_value,
                groups.company_id,
                %(company_currency_id)s as company_currency_id,
                abs(groups.net),
                abs(groups.tax)
            FROM
                taxgroups groups

        """
        query_inject_params = {
            "company_id": self.company_id.id,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "report_id": self.id,
            "uid": self.env.uid,
            "company_currency_id": self.company_id.currency_id.id,
        }

        # daca o factura are mai multe tva-uri atunci aceasta este numarata de mai multe ori.

        self.env.cr.execute(query_inject, query_inject_params)

        query_inject = """
            WITH
                taxgroups AS (
                        SELECT

                            movetax.partner_id,

                            count(move.id) as invoice_count,

                            voucher.voucher_type  as type  ,
                            movetax.tax_line_id as tax_id,
                            to_char(coalesce(tax.amount,0),'99') as tax_value,
                            movetax.company_id,
                            company_currency_id,
                            abs(coalesce(sum(movetax.tax_base_amount), 0.00)) AS net,
                            abs(coalesce(sum(movetax.balance), 0.00)) AS tax
                                FROM
                                account_move_line AS movetax
                                INNER JOIN account_tax AS tax   ON movetax.tax_line_id = tax.id
                                INNER JOIN account_move AS move ON move.id = movetax.move_id

                                 JOIN account_voucher as voucher on move.id = voucher.move_id
                                WHERE   movetax.tax_exigible and move.state = 'posted' and


                                        move.company_id = %(company_id)s AND
                                         tax_base_amount > 0 and   -- nu se caluleaza baza la taxarea inversa care nu trebuie inclusa in raport
                                        move.date >= %(date_from)s      AND move.date <= %(date_to)s
                               GROUP BY movetax.partner_id,     voucher.voucher_type,
                                 movetax.tax_line_id, tax.amount, movetax.company_id, company_currency_id
                )
            INSERT INTO
                l10n_ro_d394
                (
                report_id,  create_uid, create_date,
                partner_id,

                invoice_count,
                fiscal_position_id,
                type,
                tax_id,
                tax_value,
                company_id,
                company_currency_id,
                net,
                tax
                )
            SELECT
                %(report_id)s AS report_id, %(uid)s AS create_uid, NOW() AS create_date,
                groups.partner_id,

                groups.invoice_count,
                null as fiscal_position_id,
                groups.type,
                groups.tax_id,
                groups.tax_value,
                groups.company_id,
                %(company_currency_id)s as company_currency_id,
                abs(groups.net),
                abs(groups.tax)
            FROM
                taxgroups groups

        """
        query_inject_params = {
            "company_id": self.company_id.id,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "report_id": self.id,
            "uid": self.env.uid,
            "company_currency_id": self.company_id.currency_id.id,
        }

        # daca o factura are mai multe tva-uri atunci aceasta este numarata de mai multe ori.

        self.env.cr.execute(query_inject, query_inject_params)

        self.refresh()
        self.item_ids.refresh()
        self.item_ids._get_partner_type()
        self.item_ids._get_operation_type()

        query_inject = """
            INSERT INTO
                l10n_ro_d394_plaje
                (
                report_id,
                create_uid,
                create_date,
                journal_id,
                de_la,
                pana_la
                )
            SELECT
                %(report_id)s AS report_id,
                %(uid)s AS create_uid,
                NOW() AS create_date,
                journal_id,
                min(number) as de_la,
                max(number) as pana_la
            FROM
                account_invoice
                JOIN account_journal on account_journal.id = account_invoice.journal_id
            WHERE
                  account_journal.type = 'sale' and
                  account_invoice.company_id = %(company_id)s AND
                  date >= %(date_from)s AND date <= %(date_to)s
            GROUP BY journal_id

        """
        query_inject_params = {
            "company_id": self.company_id.id,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "report_id": self.id,
            "uid": self.env.uid,
        }
        self.env.cr.execute(query_inject, query_inject_params)


class D394Plaje(models.TransientModel):
    _name = "l10n_ro.d394.plaje"
    _description = "Declaration 394 Plaje de facturi"

    report_id = fields.Many2one("l10n_ro.d394_report")
    journal_id = fields.Many2one("account.journal")
    de_la = fields.Char()
    pana_la = fields.Char()

    serie = fields.Char(compute="_comute_serie")
    de_la_nr = fields.Char(compute="_comute_serie")
    pana_la_nr = fields.Char(compute="_comute_serie")

    def get_doc_number(self, nume):
        NrDoc = nume or ""
        Serie = ""
        if "/" in NrDoc:
            seg = NrDoc.split("/")
            NrDoc = seg[-1]
            Serie = "/".join(seg[:-1])
        elif "." in NrDoc:
            seg = NrDoc.split(".")
            NrDoc = seg[-1]
            Serie = ".".join(seg[:-1])
        else:
            Serie = nume or ""
            Serie = "".join([s for s in Serie if not s.isdigit()])

        NrDoc = "".join([s for s in NrDoc[-10:] if s.isdigit()])
        return NrDoc, Serie


    @api.depends("journal_id")
    def _comute_serie(self):
        for item in self:
            de_la_nr, serie = item.get_doc_number(item.de_la)
            pana_la_nr, serie = item.get_doc_number(item.pana_la)

            item.serie = serie
            item.de_la_nr = de_la_nr
            item.pana_la_nr = pana_la_nr


class D394(models.TransientModel):
    _name = "l10n_ro.d394"
    _description = "Declaration 394"
    _order = "report_id,partner_type"

    report_id = fields.Many2one("l10n_ro.d394_report")
    partner_id = fields.Many2one("res.partner", string="Partner", readonly=True)
    invoice_count = fields.Integer(string="Invoice Count", readonly=True)

    fiscal_position_id = fields.Many2one("account.fiscal.position", string="Fiscal Position", readonly=True)
    tax_id = fields.Many2one("account.tax", string="Originator tax", readonly=True)
    type = fields.Selection(
        [
            ("out_invoice", "Customer Invoice"),
            ("in_invoice", "Vendor Bill"),
            ("out_refund", "Customer Credit Note"),
            ("in_refund", "Vendor Credit Note"),
            ("sale", "Sale voucher"),
            ("purchase", "Purchase voucher"),
        ],
        readonly=True,
    )
    tax_value = fields.Char(readonly=True)
    net = fields.Monetary(default=0.0, currency_field="company_currency_id", readonly=True)
    tax = fields.Monetary(default=0.0, currency_field="company_currency_id", readonly=True)
    # date = fields.Date(string='Date',  readonly=True )
    company_id = fields.Many2one("res.company", string="Company", readonly=True)
    company_currency_id = fields.Many2one("res.currency", string="Company Currency", readonly=True)

    partner_type = fields.Char(
        "Partner Type",
        compute="_get_partner_type",
        store=True,
        help="""
            1.Persoane impozabile inregistrate in scopuri de TVA in Romania
            2.Persoane neinregistrate in scopuri de TVA
            3.Persoane impozabile nestabilite în România care sunt stabilite în alt stat membru,
              neînregistrate şi care nu sunt obligate să se înregistreze în scopuri de TVA în România
            4.Persoane impozabile neînregistrate şi care nu sunt obligate să se înregistreze în scopuri
              de TVA în România,nestabilite pe teritoriul Uniunii Europene
    """,
    )
    operation_type = fields.Selection(
        OPERATION_TYPE, compute="_get_operation_type", store=True, string="Operation Type"
    )


    def _get_partner_type(self):
        for item in self:
            partner = item.partner_id
            # daca nu este completata tara unui partener se considera ca este Romanaia
            country = partner.country_id or self.env.ref("base.ro")
            eur_countries = []
            eur_grp = self.env.ref("base.europe")
            if eur_grp:
                eur_countries = [country.id for country in eur_grp.country_ids]
            if country.id == self.env.ref("base.ro").id:
                if partner.vat_subjected:
                    new_type = "1"
                else:
                    new_type = "2"
            elif partner.country_id.id in eur_countries:
                new_type = "3"
            else:
                new_type = "4"
            item.partner_type = new_type
        return True


    def _get_operation_type(self):
        """
        :return:
            ('L', 'Customer Invoice'),
            ('A', 'Supplier Invoice'),
            ('LS', 'Special Customer Invoice'),
            ('AS', 'Special Supplier Invoice'),
            ('AI', 'VAT on Payment Supplier Invoice'),
            ('V', 'Inverse Taxation Customer Invoice'),
            ('C', 'Inverse Taxation Supplier Invoice'),
            ('N', 'Physical  Persons Supplier Invoice')
        """

        inverse_taxation_position = self.env.user.company_id.property_inverse_taxation_position_id
        inverse_taxation = self.env["account.tax"]
        for line in inverse_taxation_position.tax_ids:
            if line.tax_dest_id.amount_type == "group":
                inverse_taxation |= line.tax_dest_id.children_tax_ids
            else:
                inverse_taxation |= line.tax_dest_id

        for item in self:
            oper_type = "N"
            if item.partner_type == "1":
                if item.type in ("out_invoice", "out_refund"):
                    oper_type = "L"  # L - Livare - Vanzare
                else:
                    oper_type = "A"  # A- Achizitie
                    if item.fiscal_position_id == item.company_id.property_vat_on_payment_position_id:
                        oper_type = "AI"
                    if item.tax_id.id in inverse_taxation.ids:
                        oper_type = "C"

            elif item.partner_type == "2":
                oper_type = "N"
            item.operation_type = oper_type
        return True
