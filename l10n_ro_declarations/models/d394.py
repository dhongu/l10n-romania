# -*- coding: utf-8 -*-
# ©  2018 Terrabit
# See README.rst file on addons root folder for license details


from odoo import api, fields, models
from odoo.tools import safe_eval
from odoo import tools
from lxml import etree

OPERATION_TYPE = [
    ('L', 'Customer Invoice'),
    ('A', 'Supplier Invoice'),
    ('LS', 'Special Customer Invoice'),
    ('AS', 'Special Supplier Invoice'),
    ('AI', 'VAT on Payment Supplier Invoice'),
    ('V', 'Inverse Taxation Customer Invoice'),
    ('C', 'Inverse Taxation Supplier Invoice'),
    ('N', 'Fizical Persons Supplier Invoice')
]


class D394Report(models.TransientModel):
    _name = "l10n_ro.d394_report"
    _description = "Declaration 394"
    _inherit = "l10n_ro.d000_report"
    _code = 'D394'

    item_ids = fields.One2many('l10n_ro.d394', 'report_id')

    @api.multi
    def xml_processing(self, xml_doc):
        tag_tip1 = xml_doc.xpath('//tip1')[0]

        tag_tip1.clear()
        partner_types = ['1', '2', '3', '4']
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

                tag = etree.SubElement(sub2, "cota")
                tag.text = item.tax_value

                tag = etree.SubElement(sub2, "cuiP")
                if item.partner_id.vat:
                    tag.text = item.partner_id.vat.replace('RO', '')

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

    @api.multi
    def compute_data_for_report(self):
        self.ensure_one()
        query_inject = '''
WITH
    taxgroups AS (
            SELECT  
                
                movetax.partner_id,
                 
                count(movetax.invoice_id) as invoice_count,
                invoice.fiscal_position_id,
                invoice.type,
                movetax.tax_line_id as tax_id, 
                to_char(tax.amount,'99') as tax_value,
                movetax.company_id,
                company_currency_id,
                abs(coalesce(sum(movetax.tax_base_amount), 0.00)) AS net,
                abs(coalesce(sum(movetax.balance), 0.00)) AS tax
                    FROM
                    account_move_line AS movetax
                    INNER JOIN account_tax AS tax   ON movetax.tax_line_id = tax.id
                    INNER JOIN account_move AS move
                        ON move.id = movetax.move_id
                    INNER JOIN account_invoice as invoice on movetax.invoice_id = invoice.id
                    WHERE   movetax.tax_exigible and move.state = 'posted' and 
                            move.company_id = %s AND move.date >= %s
                            AND move.date <= %s 
                    GROUP BY movetax.partner_id,   invoice.type, invoice.fiscal_position_id,
                     movetax.tax_line_id, tax.amount, movetax.company_id, company_currency_id
    )
INSERT INTO
    l10n_ro_d394
    (
    report_id,
    create_uid,
    create_date,
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
    %s AS report_id,
    %s AS create_uid,
    NOW() AS create_date,
    groups.partner_id,
 
    groups.invoice_count,
    groups.fiscal_position_id,
    groups.type,
    groups.tax_id,
    groups.tax_value,
    groups.company_id,
    groups.company_currency_id,
    abs(groups.net),
    abs(groups.tax)
FROM
    taxgroups groups
        
        '''
        query_inject_params = (self.company_id.id, self.date_from, self.date_to, self.id, self.env.uid)
        self.env.cr.execute(query_inject, query_inject_params)
        self.refresh()
        self.item_ids.refresh()
        self.item_ids._get_partner_type()
        self.item_ids._get_operation_type()


class D394(models.TransientModel):
    _name = "l10n_ro.d394"
    _description = "Declaration 394"
    _order = 'report_id,partner_type'

    report_id = fields.Many2one('l10n_ro.d394_report')
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    invoice_count = fields.Integer(string='Invoice Count', readonly=True)

    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', readonly=True)
    tax_id = fields.Many2one('account.tax', string='Originator tax', readonly=True)
    type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Vendor Bill'),
        ('out_refund', 'Customer Credit Note'),
        ('in_refund', 'Vendor Credit Note'),
    ], readonly=True)
    tax_value = fields.Char(readonly=True)
    net = fields.Monetary(default=0.0, currency_field='company_currency_id', readonly=True)
    tax = fields.Monetary(default=0.0, currency_field='company_currency_id', readonly=True)
    # date = fields.Date(string='Date',  readonly=True )
    company_id = fields.Many2one('res.company', string="Company", readonly=True)
    company_currency_id = fields.Many2one('res.currency', string="Company Currency", readonly=True)

    partner_type = fields.Char('Partner Type', compute="_get_partner_type", store=True, help=''' 
            1.Persoane impozabile inregistrate in scopuri de TVA in Romania
            2.Persoane neinregistrate in scopuri de TVA
            3.Persoane impozabile nestabilite în România care sunt stabilite în alt stat membru, 
              neînregistrate şi care nu sunt obligate să se înregistreze în scopuri de TVA în România 
            4.Persoane impozabile neînregistrate şi care nu sunt obligate să se înregistreze în scopuri 
              de TVA în România,nestabilite pe teritoriul Uniunii Europene 
    ''')
    operation_type = fields.Selection(OPERATION_TYPE, compute='_get_operation_type', store=True,
                                      string='Operation Type')

    @api.multi
    def _get_partner_type(self):
        for item in self:
            partner = item.partner_id
            eur_countries = []
            eur_grp = self.env.ref('base.europe')
            if eur_grp:
                eur_countries = [country.id for country in eur_grp.country_ids]
            if partner.country_id and partner.country_id.id == self.env.ref('base.ro').id:
                if partner.vat_subjected:
                    new_type = '1'
                else:
                    new_type = '2'
            elif partner.country_id.id in eur_countries:
                new_type = '3'
            else:
                new_type = '4'
            item.partner_type = new_type
        return True

    @api.multi
    def _get_operation_type(self):
        for item in self:
            partner = item.partner_id
            country_ro = self.env.ref('base.ro')
            if item.type in ('out_invoice', 'out_refund'):
                oper_type = 'L'
            else:
                oper_type = 'A'
            item.operation_type = oper_type
        return True
