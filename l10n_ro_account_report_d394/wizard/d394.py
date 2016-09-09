# -*- coding: utf-8 -*-
# ©  2016 Forest and Biomass Romania
# See README.rst file on addons root folder for license details

import base64
from dateutil.relativedelta import relativedelta
import re

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class d394_new_report(models.TransientModel):

    """
    D394 Declaration
    """
    _name = "l10n_ro_account_report_d394.d394_new.report"
    _description = 'D394 New Declaration'

    def _get_xml_data(self):
        if self._context.get('file_save', False):
            return base64.encodestring(context['file_save'].encode('utf8'))
        return ''

    @api.model
    def _get_default_period(self):
        new_date = fields.Date.from_string(fields.Date.today()) + relativedelta(months=-1)
        period = self.env['account.period'].find(new_date)[:1]
        return period.id

    @api.multi
    @api.depends('company_id', 'period_id')
    def _get_name(self):
        self.ensure_one()
        name = 'd394'
        if self.company_id and self.company_id.vat:
            name += '_%s' % self.company_id.vat
        if self.period_id:
            name += '_%s' % self.period_id.name
        self.name = (name + '.xml').replace('/', '_')

    file_save = fields.Binary('Save File', default='_get_xml_data')
    name = fields.Char('File Name', compute='_get_name')
    msg = fields.Text('File created', readonly=True,
                      default='Save the File with '".xml"' extension.')
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        change_default=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'l10n_ro_account_report_d394.d394_new.report'))
    period_id = fields.Many2one('account.period', 'Period', required=True,
                                change_default=True,
                                default=_get_default_period)
    anaf_cross_opt = fields.Boolean('ANAF Crosschecking',
                                    related='company_id.anaf_cross_opt')
    anaf_cross_new_opt = fields.Boolean('Allow ANAF Crosschecking')
    solicit = fields.Boolean('Request VAT Reimbursment')
    achizitiiPE = fields.Boolean(
        'Purchases of Eolian Parks',
        help='Achizitii de bunuri si servicii legate direct de'
             ' bunurile imobile: Parcuri Eoliene')
    achizitiiCR = fields.Boolean(
        'Purchases of Residential Buildings',
        help='Achizitii de bunuri si servicii legate direct de'
             ' bunurile imobile: constructii rezidentiale')
    achizitiiCB = fields.Boolean(
        'Purchases of Office Buildings',
        help='Achizitii de bunuri si servicii legate direct de'
             ' bunurile imobile: cladiri de birouri')
    achizitiiCI = fields.Boolean(
        'Purchases of Industrial Buildings',
        help='Achizitii de bunuri si servicii legate direct de'
             ' bunurile imobile: constructii industriale')
    achizitiiA = fields.Boolean(
        'Purchases of Real Estates: Others',
        help='Achizitii de bunuri si servicii legate direct de'
             ' bunurile imobile: altele')
    achizitiiB24 = fields.Boolean(
        'Purchased Goods with 24% VAT',
        help='Achizitii de bunuri, cu exceptia celor legate direct'
             ' de bunuri imobile cu cota 24%')
    achizitiiB20 = fields.Boolean(
        'Purchased Goods with 20% VAT',
        help='Achizitii de bunuri, cu exceptia celor legate direct'
             ' de bunuri imobile cu cota 20%')
    achizitiiB19 = fields.Boolean(
        'Purchased Goods with 19% VAT',
        help='Achizitii de bunuri, cu exceptia celor legate direct'
             ' de bunuri imobile cu cota 19%')
    achizitiiB9 = fields.Boolean(
        'Purchased Goods with 9% VAT',
        help='Achizitii de bunuri, cu exceptia celor legate direct'
             ' de bunuri imobile cu cota 9%')
    achizitiiB5 = fields.Boolean(
        'Purchased Goods with 5% VAT',
        help='Achizitii de bunuri, cu exceptia celor legate direct'
             ' de bunuri imobile cu cota 5%')
    achizitiiS24 = fields.Boolean(
        'Purchased Services with 24% VAT',
        help='Achizitii de servicii, cu exceptia celor legate direct'
             ' de bunuri imobile cu cota 24%')
    achizitiiS20 = fields.Boolean(
        'Purchased Services with 20% VAT',
        help='Achizitii de servicii, cu exceptia celor legate direct'
             ' de bunuri imobile cu cota 20%')
    achizitiiS19 = fields.Boolean(
        'Purchased Services with 19% VAT',
        help='Achizitii de servicii, cu exceptia celor legate direct'
             ' de bunuri imobile cu cota 19%')
    achizitiiS9 = fields.Boolean(
        'Purchased Services with 9% VAT',
        help='Achizitii de servicii, cu exceptia celor legate direct'
             ' de bunuri imobile cu cota 9%')
    achizitiiS5 = fields.Boolean(
        'Purchased Services with 5% VAT',
        help='Achizitii de servicii, cu exceptia celor legate direct'
             ' de bunuri imobile cu cota 5%')
    importB = fields.Boolean(
        'Purchase Goods - Imports',
        help='Importuri de bunuri')
    acINecorp = fields.Boolean(
        'Purchase of Intangible Assets',
        help='Achizitii imobilizari necorporale')
    livrariBI = fields.Boolean(
        'Sales from Real Estates',
        help='Livrari de bunuri imobile')
    BUN24 = fields.Boolean(
        'Sales Goods with 24% VAT',
        help='Livrari de bunuri, cu exceptia bunurilor'
             ' imobile cu cota de 24%')
    BUN20 = fields.Boolean(
        'Sales Goods with 20% VAT',
        help='Livrari de bunuri, cu exceptia bunurilor'
             ' imobile cu cota de 20%')
    BUN19 = fields.Boolean(
        'Sales Goods with 19% VAT',
        help='Livrari de bunuri, cu exceptia bunurilor'
             ' imobile cu cota de 19%')
    BUN9 = fields.Boolean(
        'Sales Goods with 9% VAT',
        help='Livrari de bunuri, cu exceptia bunurilor'
             ' imobile cu cota de 9%')
    BUN5 = fields.Boolean(
        'Sales Goods with 5% VAT',
        help='Livrari de bunuri, cu exceptia bunurilor'
             ' imobile cu cota de 5%')
    valoareScutit = fields.Boolean(
        'Sales Goods exempt from VAT',
        help='Livrari de bunuri scutite de TVA')
    BunTI = fields.Boolean(
        'Sales Goods with Inverse Taxation',
        help='Livrari de bunuri/prestari de servicii pt care'
             ' se aplica taxarea inversa')
    Prest24 = fields.Boolean(
        'Sales Services with 24% VAT',
        help='Prestari de servicii cu cota de 24%')
    Prest20 = fields.Boolean(
        'Sales Services with 20% VAT',
        help='Prestari de servicii cu cota de 20%')
    Prest19 = fields.Boolean(
        'Sales Services with 19% VAT',
        help='Prestari de servicii cu cota de 19%')
    Prest9 = fields.Boolean(
        'Sales Services with 9% VAT',
        help='Prestari de servicii cu cota de 9%')
    Prest5 = fields.Boolean(
        'Sales Services with 5% VAT',
        help='Prestari de servicii cu cota de 5%')
    PrestScutit = fields.Boolean(
        'Sales Services exempt from VAT',
        help='Prestari de servicii scutite de TVA')
    LIntra = fields.Boolean(
        'Sales Goods - Intra-Community',
        help='Livrari intracomunitare de bunuri')
    PrestIntra = fields.Boolean(
        'Sales Services - Intra-Community',
        help='Prestari intracomunitare de servicii')
    Export = fields.Boolean(
        'Sales Goods - Exports',
        help='Exporturi de bunuri')
    livINecorp = fields.Boolean(
        'Sales of Intangible Assets',
        help='Livrari imobilizari necorporale')

    @api.multi
    def _update_partners(self):
        self.ensure_one()
        invoices = self.env['account.invoice'].search([
                    ('state', 'in', ['open', 'paid']),
                    ('period_id', '=', self.period_id.id),
                    ('fiscal_receipt', '=', False),
                    '|',
                    ('company_id', '=', self.company_id.id),
                    ('company_id', 'in', self.company_id.child_ids.ids)
                ])
        if invoices:
            partners = self.env['res.partner'].browse(
                set(invoices.mapped('partner_id.id')))
            partners.update_vat_one()
        return True

    @api.multi
    def _get_inv_lines(self, invoices, sel_cota, domain):
        obj_inv_line = self.env['account.invoice.line']
        invs = invoices.filtered(lambda r: domain)
        domain = [('invoice_id', 'in', invs.ids)]
        inv_lines = obj_inv_line.search(domain)
        cotas = []
        for inv in invs:
            cotas += [tax for tax in inv.tax_ids]
        filtered_inv_lines = []
        cota_amount = 0
        for cota in cotas:
            cota_inv = invs.filtered(
                lambda r: cota.id in r.tax_ids.ids)
            cota_amount = 0
            if cota.type == 'percent':
                cota_amount = int(cota.amount * 100)
            elif cota.type == 'amount':
                cota_amount = int(cota.amount)
            if cota_amount == sel_cota:
                filtered_inv_lines = []
                for inv_line in inv_lines:
                    tax = inv_line.invoice_line_tax_id
                    if cota.id in tax.ids:
                        filtered_inv_lines.append(inv_line.id)
        inv_lines = obj_inv_line.browse(filtered_inv_lines)
        return inv_lines

    @api.multi
    def _get_payments(self):
        invoice_obj = self.env['account.invoice']
        period = self.period_id
        company = self.company_id
        comp_curr = company.currency_id
        payments = []
        where = [
            ('state', 'in', ['open', 'paid']),
            ('date_invoice', '<=', period.date_stop),
            '|',
            ('company_id', '=', self.company_id.id),
            ('company_id', 'in', self.company_id.child_ids.ids)
        ]
        invoices = invoice_obj.search(where,
                                      order="type desc, date_invoice, number")
        for inv1 in invoices:
            ctx = {'date': inv1.date_invoice}
            if inv1.payment_ids:
                for payment in inv1.payment_ids:
                    if payment.period_id.id == period.id:
                        pay = {}
                        pay['type'] = inv1.type
                        pay['vat_on_payment'] = inv1.vat_on_payment
                        pay['base_24'] = pay['base_20'] = pay['base_19'] = 0.00
                        pay['base_9'] = pay['base_5'] = 0.00
                        pay['tva_24'] = pay['tva_20'] = pay['tva_19'] = 0.00
                        pay['tva_9'] = pay['tva_5'] = 0.00
                        for line in payment.move_id.line_id:
                            if ('4427' in line.account_id.code) or \
                                    ('4426' in line.account_id.code):
                                if line.tax_code_id and \
                                        ' 24' in line.tax_code_id.name:
                                    pay['base_24'] += \
                                        inv1.currency_id.with_context(
                                            ctx).compute((line.credit or \
                                                          line.debit) / 0.24,
                                                         comp_curr)
                                    pay['tva_24'] += \
                                        inv1.currency_id.with_context(
                                            ctx).compute((line.credit or \
                                                          line.debit),
                                                         comp_curr)
                                if line.tax_code_id and \
                                        ' 20' in line.tax_code_id.name:
                                    pay['base_20'] += \
                                        inv1.currency_id.with_context(
                                             ctx).compute((line.credit or \
                                                           line.debit) / 0.20,
                                                          comp_curr)
                                    pay['tva_20'] += \
                                        inv1.currency_id.with_context(
                                            ctx).compute((line.credit or \
                                                          line.debit),
                                                         comp_curr)
                                if line.tax_code_id and \
                                        ' 19' in line.tax_code_id.name:
                                    pay['base_19'] += \
                                        inv1.currency_id.with_context(
                                            ctx).compute((line.credit or \
                                                          line.debit) / 0.09,
                                                         comp_curr)
                                    pay['tva_19'] += \
                                        inv1.currency_id.with_context(
                                            ctx).compute((line.credit or \
                                                          line.debit),
                                                         comp_curr)
                                if line.tax_code_id and \
                                        ' 9' in line.tax_code_id.name:
                                    pay['base_9'] += \
                                        inv1.currency_id.with_context(
                                            ctx).compute((line.credit or \
                                                          line.debit) / 0.09,
                                                         comp_curr)
                                    pay['tva_9'] += \
                                        inv1.currency_id.with_context(
                                            ctx).compute((line.credit or \
                                                          line.debit),
                                                         comp_curr)
                                if line.tax_code_id and \
                                        ' 5' in line.tax_code_id.name:
                                    pay['base_5'] += \
                                        inv1.currency_id.with_context(
                                            ctx).compute((line.credit or \
                                                          line.debit) / 0.05,
                                                         comp_curr)
                                    pay['tva_5'] += \
                                        inv1.currency_id.with_context(
                                            ctx).compute((line.credit or \
                                                          line.debit),
                                                         comp_curr)
                        for field in ('base_24', 'base_20', 'base_19',
                                      'base_9', 'base_5',
                                      'tva_24', 'tva_20', 'tva_19',
                                      'tva_9', 'tva_5'):
                            pay[field] = int(round(pay[field]))
                        payments.append(pay)
        return payments

    def _generate_informatii(self, invoices, payments, op1, op2):
        informatii = {}
        informatii['nrCui1'] = len(
            set(op['cuiP'] for op in op1 if op['tip_partener'] == '1'))
        informatii['nrCui2'] = len(
            [op for op in op1 if op['tip_partener'] == '2'])
        informatii['nrCui3'] = len(
            set(op['cuiP'] for op in op1 if op['tip_partener'] == '3'))
        informatii['nrCui4'] = len(
            set(op['cuiP'] for op in op1 if op['tip_partener'] == '4'))
        informatii['nr_BF_i1'] = sum(
            op['nrBF'] for op in op2 if op['tip_op2'] == 'I1')
        informatii['incasari_i1'] = sum(
            op['total'] for op in op2 if op['tip_op2'] == 'I1')
        informatii['incasari_i2'] = sum(
            op['total'] for op in op2 if op['tip_op2'] == 'I2')
        informatii['nrFacturi_terti'] = len(
            set(invoices.filtered(lambda r: r.sequence_type == 'autoinv1')))
        informatii['nrFacturi_benef'] = len(
            set(invoices.filtered(lambda r: r.sequence_type == 'autoinv2')))
        informatii['nrFacturi'] = len(invoices)
        informatii['nrFacturiL_PF'] = len(
            set(invoices.filtered(lambda r: r.operation_type == 'L' and \
                                            r.partner_type == '2' and \
                                            r.amount_total <= 10000)))
        informatii['nrFacturiLS_PF'] = len(
            set(invoices.filtered(lambda r: r.operation_type == 'LS' and \
                                            r.partner_type == '2' and \
                                            r.amount_total <= 10000)))
        informatii['val_LS_PF'] = int(round(sum(
            inv.amount_total for inv in invoices.filtered(
                lambda r: r.operation_type == 'LS' and \
                          r.partner_type == '2' and \
                          r.amount_total <= 10000))))
        informatii['tvaDedAI24'] = int(round(sum(
            op['tva_24'] for op in payments if \
                op['type'] in ('in_invoice', 'in_refund') and \
                op['vat_on_payment'] is True)))
        informatii['tvaDedAI20'] = int(round(sum(
            op['tva_20'] for op in payments if \
                op['type'] in ('in_invoice', 'in_refund') and \
                op['vat_on_payment'] is True)))
        informatii['tvaDedAI19'] = int(round(sum(
            op['tva_19'] for op in payments if \
                op['type'] in ('in_invoice', 'in_refund') and \
                op['vat_on_payment'] is True)))
        informatii['tvaDedAI9'] = int(round(sum(
            op['tva_9'] for op in payments if \
                op['type'] in ('in_invoice', 'in_refund') and \
                op['vat_on_payment'] is True)))
        informatii['tvaDedAI5'] = int(round(sum(
            op['tva_5'] for op in payments if \
                op['type'] in ('in_invoice', 'in_refund') and \
                op['vat_on_payment'] is True)))

        comm_partner = self.company_id.partner_id.commercial_partner_id
        ctx = dict(self._context)
        ctx.update({'check_date': self.period_id.date_stop})

        if comm_partner.with_context(ctx)._check_vat_on_payment():
            informatii['tvaDed24'] = int(round(sum(
                op['tva_24'] for op in payments if \
                    op['type'] in ('in_invoice', 'in_refund') and \
                    op['vat_on_payment'] is False)))
            informatii['tvaDed20'] = int(round(sum(
                op['tva_20'] for op in payments if \
                    op['type'] in ('in_invoice', 'in_refund') and \
                    op['vat_on_payment'] is False)))
            informatii['tvaDed19'] = int(round(sum(
                op['tva_19'] for op in payments if \
                    op['type'] in ('in_invoice', 'in_refund') and \
                    op['vat_on_payment'] is False)))
            informatii['tvaDed9'] = int(round(sum(
                op['tva_9'] for op in payments if \
                    op['type'] in ('in_invoice', 'in_refund') and \
                    op['vat_on_payment'] is False)))
            informatii['tvaDed5'] = int(round(sum(
                op['tva_5'] for op in payments if \
                    op['type'] in ('in_invoice', 'in_refund') and \
                    op['vat_on_payment'] is False)))
            informatii['tvaCol24'] = int(round(sum(
                op['tva_24'] for op in payments if \
                    op['type'] in ('out_invoice', 'out_refund') and \
                    op['vat_on_payment'] is True)))
            informatii['tvaCol20'] = int(round(sum(
                op['tva_20'] for op in payments if \
                    op['type'] in ('out_invoice', 'out_refund') and \
                    op['vat_on_payment'] is True)))
            informatii['tvaCol19'] = int(round(sum(
                op['tva_19'] for op in payments if \
                    op['type'] in ('out_invoice', 'out_refund') and \
                    op['vat_on_payment'] is True)))
            informatii['tvaCol9'] = int(round(sum(
                op['tva_9'] for op in payments if \
                    op['type'] in ('out_invoice', 'out_refund') and \
                    op['vat_on_payment'] is True)))
            informatii['tvaCol5'] = int(round(sum(
                op['tva_5'] for op in payments if \
                    op['type'] in ('out_invoice', 'out_refund') and \
                    op['vat_on_payment'] is True)))
        informatii['incasari_ag'] = 0
        informatii['costuri_ag'] = 0
        informatii['marja_ag'] = 0
        informatii['tva_ag'] = 0
        informatii['pret_vanzare'] = 0
        informatii['pret_cumparare'] = 0
        informatii['marja_antic'] = 0
        informatii['tva_antic'] = 0
        informatii['solicit'] = int(self.solicit)
        if self.solicit:
            informatii['achizitiiPE'] = int(self.achizitiiPE)
            informatii['achizitiiCR'] = int(self.achizitiiCR)
            informatii['achizitiiCB'] = int(self.achizitiiCB)
            informatii['achizitiiCI'] = int(self.achizitiiCI)
            informatii['achizitiiA'] = int(self.achizitiiA)
            informatii['achizitiiB24'] = int(self.achizitiiB24)
            informatii['achizitiiB20'] = int(self.achizitiiB20)
            informatii['achizitiiB19'] = int(self.achizitiiB19)
            informatii['achizitiiB9'] = int(self.achizitiiB9)
            informatii['achizitiiB5'] = int(self.achizitiiB5)
            informatii['achizitiiS24'] = int(self.achizitiiS24)
            informatii['achizitiiS20'] = int(self.achizitiiS20)
            informatii['achizitiiS19'] = int(self.achizitiiS19)
            informatii['achizitiiS9'] = int(self.achizitiiS9)
            informatii['achizitiiS5'] = int(self.achizitiiS5)
            informatii['importB'] = int(self.importB)
            informatii['acINecorp'] = int(self.acINecorp)
            informatii['livrariBI'] = int(self.livrariBI)
            informatii['BUN24'] = int(self.BUN24)
            informatii['BUN20'] = int(self.BUN20)
            informatii['BUN19'] = int(self.BUN19)
            informatii['BUN9'] = int(self.BUN9)
            informatii['BUN5'] = int(self.BUN5)
            informatii['valoareScutit'] = int(self.valoareScutit)
            informatii['BunTI'] = int(self.BunTI)
            informatii['Prest24'] = int(self.Prest24)
            informatii['Prest20'] = int(self.Prest20)
            informatii['Prest19'] = int(self.Prest19)
            informatii['Prest9'] = int(self.Prest9)
            informatii['Prest5'] = int(self.Prest5)
            informatii['PrestScutit'] = int(self.PrestScutit)
            informatii['LIntra'] = int(self.LIntra)
            informatii['PrestIntra'] = int(self.PrestIntra)
            informatii['Export'] = int(self.Export)
            informatii['livINecorp'] = int(self.livINecorp)
            informatii['efectuat'] = int(self.solicit)
        return informatii

    @api.multi
    def _get_op1(self, invoices):
        self.ensure_one()
        obj_inv_line = self.env['account.invoice.line']
        obj_partner = self.env['res.partner']
        obj_tax = self.env['account.tax']
        comp_curr = self.company_id.currency_id
        op1 = []
        oper_types = set([invoice.operation_type for invoice in invoices])
        for oper_type in oper_types:
            oper_type_inv = invoices.filtered(
                lambda r: r.operation_type == oper_type)
            partner_types = set([
                invoice.partner_type for invoice in oper_type_inv])
            for partner_type in partner_types:
                part_type_inv = oper_type_inv.filtered(
                    lambda r: r.partner_type == partner_type)
                cotas = []
                for invoice in part_type_inv:
                    cotas += set([tax.id for tax in invoice.tax_ids])
                cotas = set(cotas)
                for cota in obj_tax.browse(cotas):
                    cota_inv = part_type_inv.filtered(
                        lambda r: cota.id in r.tax_ids.ids)
                    partners = cota_inv.mapped('partner_id.id')
                    #[invoice.partner_id for invoice in cota_inv]
                    for partner in obj_partner.browse(partners):
                        part_invoices = cota_inv.filtered(
                            lambda r: r.partner_id.id == partner.id)
                        cota_amount = 0
                        if cota.type == 'percent':
                            cota_amount = int(cota.amount * 100)
                        elif cota.type == 'amount':
                            cota_amount = int(cota.amount)
                        if partner_type == '2':
                            if oper_type == 'N':
                                doc_types = [
                                    inv.origin_type for inv in part_invoices]
                                for doc_type in doc_types:
                                    domain = [('invoice_id',
                                               'in',
                                               part_invoices.ids),
                                              ('invoice_id.origin_type',
                                               '=',
                                               doc_type)]
                                    inv_lines = obj_inv_line.search(domain)
                                    filtered_inv_lines = []
                                    for inv_line in inv_lines:
                                        invoice = inv_line.invoice_id
                                        product = inv_line.product_id
                                        fp = invoice.fiscal_position
                                        tax = product.supplier_taxes_id
                                        if not fp or (('National' in \
                                                fp.name) or ('Invers' in \
                                                fp.name)  or ('Scutit' in \
                                                fp.name)):
                                            tax = inv_line.invoice_line_tax_id
                                            if cota.id in tax.ids:
                                                filtered_inv_lines.append(
                                                    inv_line.id)
                                        else:
                                            inv_type = inv_line.invoice_id.type
                                            if inv_type in ('out_invoice',
                                                            'out_refund'):
                                                tax = product.taxes_id
                                            if cota.id in tax.ids:
                                                filtered_inv_lines.append(
                                                    inv_line.id)
                                    inv_lines = obj_inv_line.browse(
                                        filtered_inv_lines)
                                    baza = 0
                                    for line in inv_lines:
                                        inv_curr = line.invoice_id.currency_id
                                        inv_date = line.invoice_id.date_invoice
                                        baza += inv_curr.with_context(
                                            {'date': inv_date}).compute(
                                            line.price_subtotal, comp_curr)
                                    taxes = 0
                                    new_dict = {
                                        'tip': oper_type,
                                        'tip_partener': partner_type,
                                        'cota': cota_amount,
                                        'denP': partner.name.replace(
                                             '&', '-').replace('"', ''),
                                        'nrFact': len(set([
                                            line.invoice_id.id for \
                                            line in inv_lines])),
                                        'baza': int(round(baza)),
                                        'tip_document': doc_type,
                                    }
                            else:
                                domain = [('invoice_id',
                                           'in',
                                           part_invoices.ids)]
                                inv_lines = obj_inv_line.search(domain)
                                filtered_inv_lines = []
                                for inv_line in inv_lines:
                                    fp = inv_line.invoice_id.fiscal_position
                                    tax = inv_line.product_id.supplier_taxes_id
                                    if not fp or (('National' in \
                                            fp.name) or ('Invers' in \
                                            fp.name)  or ('Scutit' in \
                                            fp.name)):
                                        tax = inv_line.invoice_line_tax_id
                                        if cota.id in tax.ids:
                                            filtered_inv_lines.append(
                                                inv_line.id)
                                    else:
                                        inv_type = inv_line.invoice_id.type
                                        if inv_type in ('out_invoice',
                                                        'out_refund'):
                                            tax = inv_line.product_id.taxes_id
                                        if cota.id in tax.ids:
                                            filtered_inv_lines.append(
                                                inv_line.id)
                                inv_lines = obj_inv_line.browse(
                                    filtered_inv_lines)
                                baza = 0
                                taxes = 0
                                for line in inv_lines:
                                    inv_curr = line.invoice_id.currency_id
                                    inv_date = line.invoice_id.date_invoice
                                    baza += inv_curr.with_context(
                                        {'date': inv_date}).compute(
                                        line.price_subtotal, comp_curr)
                                    taxes += inv_curr.with_context(
                                        {'date': inv_date}).compute(
                                        line.price_normal_taxes and \
                                        line.price_normal_taxes or \
                                        line.price_taxes, comp_curr)
                                new_dict = {
                                    'tip': oper_type,
                                    'tip_partener': partner_type,
                                    'cota': cota_amount,
                                    'denP': partner.name.replace(
                                         '&', '-').replace('"', ''),
                                    'nrFact': len(set([
                                        line.invoice_id.id for \
                                        line in inv_lines])),
                                    'baza': int(round(baza)),
                                    'tva': int(round(taxes)),
                                }
                            if not partner.is_company:
                                if partner.vat:
                                    new_dict['cuiP'] = partner._split_vat(
                                        partner.vat)[1]
                                else:
                                    if partner.country_id:
                                        new_dict['taraP'] = \
                                            partner.country_id and \
                                            partner.country_id.code.upper()
                                    if partner.city_id:
                                        new_dict['locP'] = \
                                            partner.city_id and \
                                            partner.city_id.name
                                    if partner.state_id:
                                        new_dict['judP'] = \
                                            partner.state_id and \
                                            partner.state_id.order_code
                                    if partner.street:
                                        new_dict['strP'] = \
                                            partner.add_street and \
                                            partner.add_street
                                    if partner.add_number:
                                        new_dict['nrP'] = \
                                            partner.add_number and \
                                            partner.add_number
                                    if partner.add_block:
                                        new_dict['blP'] = \
                                            partner.add_block and \
                                            partner.add_block
                                    if partner.add_flat:
                                        new_dict['apP'] = \
                                            partner.add_flat and \
                                            partner.add_flat
                                    if partner.street2:
                                        new_dict['detP'] = \
                                            partner.street2 and \
                                            partner.street2
                            else:
                                if partner.vat:
                                    new_dict['cuiP'] = partner._split_vat(
                                        partner.vat)[1]
                        else:
                            domain = [('invoice_id', 'in', part_invoices.ids)]
                            inv_lines = obj_inv_line.search(domain)
                            filtered_inv_lines = []
                            for inv_line in inv_lines:
                                fp = inv_line.invoice_id.fiscal_position
                                tax = inv_line.product_id.supplier_taxes_id
                                if not fp or (('National' in \
                                        fp.name) or ('Invers' in \
                                        fp.name)  or ('Scutit' in \
                                        fp.name)):
                                    tax = inv_line.invoice_line_tax_id
                                    if cota.id in tax.ids:
                                        filtered_inv_lines.append(
                                            inv_line.id)
                                else:
                                    inv_type = inv_line.invoice_id.type
                                    if inv_type in ('out_invoice',
                                                    'out_refund'):
                                        tax = inv_line.product_id.taxes_id
                                    if cota.id in tax.ids:
                                        filtered_inv_lines.append(
                                            inv_line.id)
                            inv_lines = obj_inv_line.browse(filtered_inv_lines)
                            baza = 0
                            taxes = 0
                            for line in inv_lines:
                                inv_curr = line.invoice_id.currency_id
                                inv_date = line.invoice_id.date_invoice
                                baza += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_subtotal, comp_curr)
                                if line.invoice_id.operation_type in \
                                        ('L', 'A', 'AI'):
                                    taxes += inv_curr.with_context(
                                        {'date': inv_date}).compute(
                                        line.price_taxes, comp_curr)
                                if line.invoice_id.operation_type == 'C':
                                    taxes += inv_curr.with_context(
                                        {'date': inv_date}).compute(
                                        line.price_normal_taxes and \
                                        line.price_normal_taxes or \
                                        line.price_taxes, comp_curr)

                            new_dict = {
                                'tip': oper_type,
                                'tip_partener': partner_type,
                                'cota': cota_amount,
                                'cuiP': partner.vat and \
                                    partner._split_vat(partner.vat)[1] or '-',
                                'denP': partner.name.replace(
                                    '&', '-').replace('"', ''),
                                'nrFact': len(part_invoices),
                                'baza': int(round(baza)),
                                'op11': []
                            }
                            if oper_type in ('A', 'L', 'C', 'AI'):
                                new_dict['tva'] = int(round(taxes))
                            
                        codes = inv_lines.mapped('product_id.d394_id')
                        op11 = []
                        if (partner_type == '1' and \
                                oper_type in ('V', 'C')) or \
                                (partner_type == '2' and oper_type == 'N'):
                            for code in codes:
                                new_code = code
                                if code.parent_id:
                                    new_code = code.parent_id
                                cod_lines = []
                                if partner_type == '1':
                                    cod_lines = [
                                        line for line in inv_lines.filtered(
                                            lambda r:
                                            r.product_id.d394_id.id == code.id\
                                            and new_code.name <= '31')
                                    ]
                                else:
                                    cod_lines = [
                                        line for line in inv_lines.filtered(
                                            lambda r:
                                            r.product_id.d394_id.id == code.id)
                                    ]
                                if cod_lines:
                                    nrFact = len(set([
                                        line.invoice_id.id for line in \
                                        inv_lines.filtered(lambda r: \
                                        r.product_id.d394_id.id == code.id)]))
                                    baza1 = 0
                                    taxes1 = 0
                                    for line in inv_lines:
                                        inv_curr = line.invoice_id.currency_id
                                        inv_date = line.invoice_id.date_invoice
                                        baza1 += inv_curr.with_context(
                                            {'date': inv_date}).compute(
                                            line.price_subtotal, comp_curr)
                                        if oper_type == 'C':
                                            taxes1 += inv_curr.with_context(
                                                {'date': inv_date}).compute(
                                                line.price_normal_taxes and \
                                                line.price_normal_taxes or \
                                                line.price_taxes, comp_curr)
                                    op11_dict = {
                                        'codPR': code.name,
                                        'nrFactPR': nrFact,
                                        'bazaPR': int(round(baza1))
                                    }
                                    if oper_type in ('A', 'L', 'C', 'AI'):
                                        op11_dict['tvaPR'] = int(round(taxes1))
                                    op11.append(op11_dict)
                        new_dict['op11'] = op11
                        op1.append(new_dict)
        return op1

    @api.multi
    def _get_op2(self, invoices):
        self.ensure_one()
        if fields.Date.from_string(self.period_id.date_start) < \
                fields.Date.from_string('2016-10-01'):
            return []
        obj_inv_line = self.env['account.invoice.line']
        obj_period = self.env['account.period']
        comp_curr = self.company_id.currency_id
        op2 = []
        oper_type = 'I1'
        periods = set([invoice.period_id.id for invoice in invoices])
        for period in obj_period.browse(periods):
            period_inv = invoices.filtered(
                lambda r: r.period_id.id == period.id)
            nrAMEF = \
                len(set([invoice.journal_id.id for invoice in period_inv]))
            nrBF = len(period_inv)
            total = 0
            baza20 = baza19 = baza9 = baza5 = 0
            tva20 = tva19 = tva9 = tva5 = 0
            for invoice in period_inv:
                cotas = [tax for tax in invoice.tax_ids]
                for cota in cotas:
                    cota_inv = period_inv.filtered(
                        lambda r: cota.id in r.tax_ids.ids)
                    cota_amount = 0
                    if cota.type == 'percent':
                        cota_amount = int(cota.amount * 100)
                    elif cota.type == 'amount':
                        cota_amount = int(cota.amount)
                    if cota_amount in (5, 9, 19, 20):
                        domain = [('invoice_id', 'in', cota_inv.ids)]
                        inv_lines = obj_inv_line.search(domain)
                        filtered_inv_lines = []
                        for inv_line in inv_lines:
                            inv_type = inv_line.invoice_id.type
                            if inv_type in ('out_invoice',
                                            'out_refund'):
                                tax = inv_line.product_id.taxes_id
                            if cota.id in tax.ids:
                                filtered_inv_lines.append(inv_line.id)
                        inv_lines = obj_inv_line.browse(filtered_inv_lines)
                        for line in inv_lines:
                            inv_curr = line.invoice_id.currency_id
                            inv_date = line.invoice_id.date_invoice
                            if cota_amount == 20:
                                baza20 += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_subtotal, comp_curr)
                                tva20 += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_normal_taxes and \
                                    line.price_normal_taxes or \
                                    line.price_taxes, comp_curr)
                            if cota_amount == 19:
                                baza19 += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_subtotal, comp_curr)
                                tva19 += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_normal_taxes and \
                                    line.price_normal_taxes or \
                                    line.price_taxes, comp_curr)
                            elif cota_amount == 9:
                                baza9 += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_subtotal, comp_curr)
                                tva9 += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_normal_taxes and \
                                    line.price_normal_taxes or \
                                    line.price_taxes, comp_curr)
                            elif cota_amount == 5:
                                baza5 += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_subtotal, comp_curr)
                                tva5 += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_normal_taxes and \
                                    line.price_normal_taxes or \
                                    line.price_taxes, comp_curr)
                            total += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_subtotal + \
                                    line.price_normal_taxes and \
                                    line.price_normal_taxes or \
                                    line.price_taxes, comp_curr)
            op2.append({
                'tip_op2': oper_type,
                'luna': int(period.code[:2]),
                'nrAMEF': int(round(nrAMEF)),
                'nrBF': int(round(nrBF)),
                'total': int(round(total)),
                'baza20': int(round(baza20)),
                'baza19': int(round(baza19)),
                'baza9': int(round(baza9)),
                'baza5': int(round(baza5)),
                'TVA20': int(round(tva20)),
                'TVA19': int(round(tva19)),
                'TVA9': int(round(tva9)),
                'TVA5': int(round(tva5))})
        return op2

    def generate_rezumat1(self, invoices, op1s):
        self.ensure_one()
        obj_inv = self.env['account.invoice']
        obj_inv_line = self.env['account.invoice.line']
        obj_d394_code = self.env['report.394.code']
        partner_type = op1s[0]['tip_partener']
        oper_type = op1s[0]['tip']
        cota_amount = int(op1s[0]['cota'])
        rezumat1 = {}
        rezumat1['tip_partener'] = op1s[0]['tip_partener']
        rezumat1['cota'] = op1s[0]['cota']
        if partner_type == '1' and cota_amount != 0:
            rezumat1['facturiL'] = int(round(sum(
                op['nrFact'] for op in op1s if op['tip'] == 'L')))
            rezumat1['bazaL'] = int(round(sum(
                op['baza'] for op in op1s if op['tip'] == 'L')))
            rezumat1['tvaL'] = int(round(sum(
                op['tva'] for op in op1s if op['tip'] == 'L')))
        if partner_type == '1' and cota_amount == 0:
            rezumat1['facturiLS'] = int(round(sum(
                op['nrFact'] for op in op1s if op['tip'] == 'LS')))
            rezumat1['bazaLS'] = int(round(sum(
                op['baza'] for op in op1s if op['tip'] == 'LS')))
        if partner_type == '1' and cota_amount != 0:
            rezumat1['facturiA'] = int(round(sum(
                op['nrFact'] for op in op1s if op['tip'] == 'A')))
            rezumat1['bazaA'] = int(round(sum(
                op['baza'] for op in op1s if op['tip'] == 'A')))
            rezumat1['tvaA'] = int(round(sum(
                op['tva'] for op in op1s if op['tip'] == 'A')))
        if partner_type == '1' and cota_amount != 0:
            rezumat1['facturiAI'] = int(round(sum(
                op['nrFact'] for op in op1s if op['tip'] == 'AI')))
            rezumat1['bazaAI'] = int(round(sum(
                op['baza'] for op in op1s if op['tip'] == 'AI')))
            rezumat1['tvaAI'] = int(round(sum(
                op['tva'] for op in op1s if op['tip'] == 'AI')))
        if partner_type == '1' and cota_amount == 0:
            rezumat1['facturiAS'] = int(round(sum(
                op['nrFact'] for op in op1s if op['tip'] == 'AS')))
            rezumat1['bazaAS'] = int(round(sum(
                op['baza'] for op in op1s if op['tip'] == 'AS')))
        if (partner_type == '1') and (cota_amount == 0):
            rezumat1['facturiV'] = int(round(sum(
                op['nrFact'] for op in op1s if op['tip'] == 'V')))
            rezumat1['bazaV'] = int(round(sum(
                op['baza'] for op in op1s if op['tip'] == 'V')))
            #rezumat1['tvaV'] = int(round(sum(
            #    op['tva'] for op in op1s if op['tip'] == 'V')))
        if (partner_type != '2') and (cota_amount != 0):
            rezumat1['facturiC'] = int(round(sum(
                op['nrFact'] for op in op1s if op['tip'] == 'C')))
            rezumat1['bazaC'] = int(round(sum(
                op['baza'] for op in op1s if op['tip'] == 'C')))
            rezumat1['tvaC'] = int(round(sum(
                op['tva'] for op in op1s if op['tip'] == 'C')))
        if op1s[0]['tip_partener'] == '2' and ('tip_document' in op1s[0]):
            rezumat1['facturiN'] = int(round(sum(
                op['tva'] for op in op1s if op['tip'] == 'N')))
            rezumat1['document_N'] = op1s[0]['tip_document']
            rezumat1['bazaN'] = int(round(sum(
                op['baza'] for op in op1s.filtered(
                lambda r: r['tip'] == 'N'))))
        rez_detaliu = []
        for op1 in op1s:
            if op1['op11']:
                for line in op1['op11']:
                    code = line['codPR']
                    new_code = obj_d394_code.search([('name', '=', code)])
                    if len(new_code)>=2:
                           new_code = new_code[0]
                    if new_code and new_code.parent_id:
                        new_code = new_code.parent_id
                    if rez_detaliu:
                        for val in rez_detaliu:
                            if new_code.name in val.values():
                                #if op1['tip'] == 'L':
                                #    val['nrLiv'] += int(
                                #        round(line['nrFactPR']))
                                #    val['bazaLiv'] += int(
                                #        round(line['bazaPR']))
                                #    val['tvaLiv'] += int(
                                #        round(line['tvaPR']))
                                if op1['tip'] == 'V' and op1['cota'] == 0:
                                    val['nrLivV'] += int(
                                        round(line['nrFactPR']))
                                    val['bazaLivV'] += int(
                                        round(line['bazaPR']))
                                #    val['tvaLivV'] += int(
                                #        round(line['tvaPR']))
                                #if op1['tip'] == 'A':
                                #    val['nrAchiz'] += int(
                                #        round(line['nrFactPR']))
                                #    val['bazaAchiz'] += int(
                                #        round(line['bazaPR']))
                                #    val['tvaAchiz'] += int(
                                #        round(line['tvaPR']))
                                #if op1['tip'] == 'AI':
                                #    val['nrAchizAI'] += int(
                                #        round(line['nrFactPR']))
                                #    val['bazaAchizAI'] += int(
                                #       round(line['bazaPR']))
                                #    val['tvaAchizAI'] += int(
                                #        round(line['tvaPR']))
                                if op1['tip'] == 'C' and op1['cota'] != 0:
                                    val['nrAchizC'] += int(
                                        round(line['nrFactPR']))
                                    val['bazaAchizC'] += int(
                                        round(line['bazaPR']))
                                    val['tvaAchizC'] += int(
                                        round(line['tvaPR']))
                                if op1['tip'] == 'N' and partner_type == '2':
                                    val['nrN'] += int(
                                        round(line['nrFactPR']))
                                    val['valN'] += int(
                                        round(line['bazaPR']))
                            else:
                                val = {}
                                val['bun'] = new_code.name
                                #val['nrLiv'] = val['bazaLiv'] = \
                                #    val['tvaLiv'] = 0
                                if op1['tip'] == 'V' and op1['cota'] == 0:
                                    val['nrLivV'] = val['bazaLivV'] = 0
                                #    val['tvaLivV'] = 0
                                #val['nrAchiz'] = val['bazaAchiz'] = \
                                #    val['tvaAchiz'] = 0
                                #val['nrAchizAI'] = val['bazaAchizAI'] = \
                                #    val['tvaAchizAI'] = 0
                                if op1['tip'] == 'C' and op1['cota'] != 0:
                                    val['nrAchizC'] = val['bazaAchizC'] = \
                                    val['tvaAchizC'] = 0
                                if partner_type == '2':
                                    val['nrN'] = val['valN'] = 0

                                #if op1['tip'] == 'L':
                                #    val['nrLiv'] += int(
                                #        round(line['nrFactPR']))
                                #    val['bazaLiv'] += int(
                                #        round(line['bazaPR']))
                                #    val['tvaLiv'] += int(
                                #        round(line['tvaPR']))
                                if op1['tip'] == 'V' and op1['cota'] == 0:
                                    val['nrLivV'] += int(
                                        round(line['nrFactPR']))
                                    val['bazaLivV'] += int(
                                        round(line['bazaPR']))
                                #    val['tvaLivV'] += int(
                                #        round(line['tvaPR']))
                                #if op1['tip'] == 'A':
                                #    val['nrAchiz'] += int(
                                #        round(line['nrFactPR']))
                                #    val['bazaAchiz'] += int(
                                #        round(line['bazaPR']))
                                #    val['tvaAchiz'] += int(
                                #        round(line['tvaPR']))
                                #if op1['tip'] == 'AI':
                                #    val['nrAchizAI'] += int(
                                #        round(line['nrFactPR']))
                                #    val['bazaAchizAI'] += int(
                                #        round(line['bazaPR']))
                                #    val['tvaAchizAI'] += int(
                                #        round(line['tvaPR']))
                                if op1['tip'] == 'C' and op1['cota'] != 0:
                                    val['nrAchizC'] += int(
                                        round(line['nrFactPR']))
                                    val['bazaAchizC'] += int(
                                        round(line['bazaPR']))
                                    val['tvaAchizC'] += int(
                                        round(line['tvaPR']))
                                if op1['tip'] == 'N' and partner_type == '2':
                                    val['nrN'] += int(
                                        round(line['nrFactPR']))
                                    val['valN'] += int(
                                        round(line['bazaPR']))
                                rez_detaliu.append(val)
                    else:
                        val = {}
                        val['bun'] = new_code.name
                        #val['nrLiv'] = val['bazaLiv'] = \
                        #    val['tvaLiv'] = 0
                        val['nrLivV'] = val['bazaLivV'] = 0
                        #    val['tvaLivV'] = 0
                        #val['nrAchiz'] = val['bazaAchiz'] = \
                        #    val['tvaAchiz'] = 0
                        #val['nrAchizAI'] = val['bazaAchizAI'] = \
                        #    val['tvaAchizAI'] = 0
                        if op1['tip'] == 'C' and op1['cota'] != 0:
                            val['nrAchizC'] = val['bazaAchizC'] = \
                                val['tvaAchizC'] = 0
                        if partner_type == '2':
                            val['nrN'] = val['valN'] = 0

                        #if op1['tip'] == 'L':
                        #    val['nrLiv'] += int(round(line['nrFactPR']))
                        #    val['bazaLiv'] += int(round(line['bazaPR']))
                        #    val['tvaLiv'] += int(round(line['tvaPR']))
                        if op1['tip'] == 'V' and op1['cota'] == 0:
                            val['nrLivV'] += int(round(line['nrFactPR']))
                            val['bazaLivV'] += int(round(line['bazaPR']))
                        #    val['tvaLivV'] += int(round(line['tvaPR']))
                        #if op1['tip'] == 'A':
                        #    val['nrAchiz'] += int(round(line['nrFactPR']))
                        #    val['bazaAchiz'] += int(round(line['bazaPR']))
                        #    val['tvaAchiz'] += int(round(line['tvaPR']))
                        #if op1['tip'] == 'AI':
                        #    val['nrAchizAI'] += int(round(line['nrFactPR']))
                        #    val['bazaAchizAI'] += int(round(line['bazaPR']))
                        #    val['tvaAchizAI'] += int(round(line['tvaPR']))
                        if op1['tip'] == 'C' and op1['cota'] != 0:                                
                            val['nrAchizC'] += int(round(line['nrFactPR']))
                            val['bazaAchizC'] += int(round(line['bazaPR']))
                            val['tvaAchizC'] += int(round(line['tvaPR']))
                        if op1['tip'] == 'N' and partner_type == '2':
                            val['nrN'] += int(round(line['nrFactPR']))
                            val['valN'] += int(round(line['bazaPR']))
                        rez_detaliu.append(val)
        rezumat1['detaliu'] = rez_detaliu
        return rezumat1

    def _generate_rezumat1(self, invoices, payments, op1, op2):
        self.ensure_one()
        rezumat1 = []
        partner_types = set([x['tip_partener'] for x in op1])
        for partner_type in partner_types:
            cotas = set([x['cota'] for x in op1 \
                if x['tip_partener'] == partner_type])
            for cota in cotas:
                op1s = []
                if partner_type == '2':
                    doc_types = set([x['tip_document'] for \
                        x in op1 if x['tip_partener'] == partner_type and \
                        x['tip'] == 'N'])
                    for doc_type in doc_types:
                        op1s = [x for x in op1 if \
                            x['tip_partener'] == partner_type and \
                            x['cota'] == cota and \
                            x['tip_document'] == doc_type]
                    if op1s:
                        rezumat1.append(self.generate_rezumat1(invoices, op1s))
                    op1s = [x for x in op1 if \
                            x['tip_partener'] == partner_type and \
                            x['cota'] == cota and \
                            x['tip'] != 'N']
                else:
                    op1s = [x for x in op1 if \
                            x['tip_partener'] == partner_type and \
                            x['cota'] == cota]
                if op1s:
                    rezumat1.append(self.generate_rezumat1(invoices, op1s))
        return rezumat1

    def generate_rezumat2(self, sel_cota, invoices, op1s, op2):
        self.ensure_one()
        obj_inv = self.env['account.invoice']
        obj_inv_line = self.env['account.invoice.line']
        rezumat2 = {}
        if op1s:
            oper_type = op1s[0]['tip']
            cota_amount = int(op1s[0]['cota'])
            rezumat2['cota'] = op1s[0]['cota']
            # To review
            rezumat2['bazaFSLcod'] = 0
            rezumat2['TVAFSLcod'] = 0
            rezumat2['bazaFSL'] = 0
            rezumat2['TVAFSL'] = 0
            rezumat2['bazaFSA'] = 0
            rezumat2['TVAFSA'] = 0
            rezumat2['bazaFSAI'] = 0
            rezumat2['TVAFSAI'] = 0

            rezumat2['bazaBFAI'] = 0
            rezumat2['TVABFAI'] = 0

            rezumat2['bazaL_PF'] = 0
            rezumat2['tvaL_PF'] = 0

            fr_inv = domain = "r.operation_type == 'L' and \
                r.fiscal_receipt is True"
            inv_lines = self._get_inv_lines(invoices, cota_amount, domain)
            if inv_lines:
                rezumat2['bazaBFAI'] = int(round(sum(
                    line.price_subtotal for line in inv_lines if \
                    not line.invoice_id.journal_id.fiscal_receipt)))
                rezumat2['TVABFAI'] = int(round(sum(
                    line.price_normal_taxes and \
                    line.price_normal_taxes or line.price_taxes \
                    for line in inv_lines if \
                    not line.invoice_id.journal_id.fiscal_receipt)))
            rezumat2['nrFacturiL'] = int(round(sum(
                op['nrFact'] for op in op1s if op['tip'] == 'L')))
            rezumat2['bazaL'] = int(round(sum(
                op['baza'] for op in op1s if op['tip'] == 'L')))
            rezumat2['tvaL'] = int(round(sum(
                op['tva'] for op in op1s if op['tip'] == 'L')))
            rezumat2['nrFacturiA'] = int(round(sum(
                op['nrFact'] for op in op1s if op['tip'] in ('A', 'C'))))
            rezumat2['bazaA'] = int(round(sum(
                op['baza'] for op in op1s if op['tip'] in ('A', 'C'))))
            rezumat2['tvaA'] = int(round(sum(
                op['tva'] for op in op1s if op['tip'] in ('A', 'C'))))
            rezumat2['nrFacturiAI'] = int(round(sum(
                op['nrFact'] for op in op1s if op['tip'] == 'AI')))
            rezumat2['bazaAI'] = int(round(sum(
                op['baza'] for op in op1s if op['tip'] == 'AI')))
            rezumat2['tvaAI'] = int(round(sum(
                op['tva'] for op in op1s if op['tip'] == 'AI')))
            if cota_amount == 5:
                rezumat2['baza_incasari_i1'] = int(round(sum(
                    x['baza5'] for x in op2 if \
                    x['tip_op2'] == 'I1')))
                rezumat2['tva_incasari_i1'] = int(round(sum(
                    x['TVA5'] for x in op2 if \
                    x['tip_op2'] == 'I1')))
                rezumat2['baza_incasari_i2'] = int(round(sum(
                    x['baza5'] for x in op2 if \
                    x['tip_op2'] == 'I2')))
                rezumat2['tva_incasari_i2'] = int(round(sum(
                    x['TVA5'] for x in op2 if \
                    x['tip_op2'] == 'I2')))
            if cota_amount == 9:
                rezumat2['baza_incasari_i1'] = int(round(sum(
                    x['baza9'] for x in op2 if \
                    x['tip_op2'] == 'I1')))
                rezumat2['tva_incasari_i1'] = int(round(sum(
                    x['TVA9'] for x in op2 if \
                    x['tip_op2'] == 'I1')))
                rezumat2['baza_incasari_i2'] = int(round(sum(
                    x['baza9'] for x in op2 if \
                    x['tip_op2'] == 'I2')))
                rezumat2['tva_incasari_i2'] = int(round(sum(
                    x['TVA9'] for x in op2 if \
                    x['tip_op2'] == 'I2')))
            if cota_amount == 20:
                rezumat2['baza_incasari_i1'] = int(round(sum(
                    x['baza20'] for x in op2 if \
                    x['tip_op2'] == 'I1')))
                rezumat2['tva_incasari_i1'] = int(round(sum(
                    x['TVA20'] for x in op2 if \
                    x['tip_op2'] == 'I1')))
                rezumat2['baza_incasari_i2'] = int(round(sum(
                    x['baza20'] for x in op2 if \
                    x['tip_op2'] == 'I2')))
                rezumat2['tva_incasari_i2'] = int(round(sum(
                    x['TVA20'] for x in op2 if \
                    x['tip_op2'] == 'I2')))
            domain = "r.operation_type == 'L' and \
                r.partner_type == '2' and r.amount_total <= 10000"
            inv_lines = self._get_inv_lines(invoices, cota_amount, domain)

            if inv_lines:
                rezumat2['bazaL_PF'] = int(round(sum(
                    line.price_subtotal for line in inv_lines)))
                rezumat2['tvaL_PF'] = int(round(sum(
                    line.price_normal_taxes and \
                    line.price_normal_taxes or line.price_taxes \
                    for line in inv_lines)))
        else:
            rezumat2['cota'] = sel_cota
            rezumat2['bazaFSLcod'] = 0
            rezumat2['TVAFSLcod'] = 0
            rezumat2['bazaFSL'] = 0
            rezumat2['TVAFSL'] = 0
            rezumat2['bazaFSA'] = 0
            rezumat2['TVAFSA'] = 0
            rezumat2['bazaFSAI'] = 0
            rezumat2['TVAFSAI'] = 0
            rezumat2['bazaBFAI'] = 0
            rezumat2['TVABFAI'] = 0
            rezumat2['nrFacturiL'] = 0
            rezumat2['bazaL'] = 0
            rezumat2['tvaL'] = 0
            rezumat2['nrFacturiA'] = 0
            rezumat2['bazaA'] = 0
            rezumat2['tvaA'] = 0
            rezumat2['nrFacturiAI'] = 0
            rezumat2['bazaAI'] = 0
            rezumat2['tvaAI'] = 0
            rezumat2['baza_incasari_i1'] = 0
            rezumat2['tva_incasari_i1'] = 0
            rezumat2['baza_incasari_i2'] = 0
            rezumat2['tva_incasari_i2'] = 0
            rezumat2['bazaL_PF'] = 0
            rezumat2['tvaL_PF'] = 0
        return rezumat2

    def _generate_rezumat2(self, invoices, payments, op1, op2):
        self.ensure_one()
        rezumat2 = []
        cotas = set([x['cota'] for x in op1 if x['cota'] != 0] + [5, 9, 20])
        for cota in cotas:
            op1s = [x for x in op1 if x['cota'] == cota]
            rezumat2.append(self.generate_rezumat2(cota, invoices, op1s, op2))
        return rezumat2

    @api.multi
    def _get_inv_series(self):
        self.ensure_one()
        if fields.Date.from_string(self.period_id.date_start) < \
                fields.Date.from_string('2016-10-01'):
            return []
        obj_seq = self.env['ir.sequence']
        obj_invoice = self.env['account.invoice']
        regex = re.compile('[^a-zA-Z]')
        ctx = self._context.copy()
        ctx['fiscalyear_id'] = self.period_id.fiscalyear_id.id
        invoices = obj_invoice.search([
                    ('state', '!=', 'draft'),
                    ('period_id', '=', self.period_id.id),
                    ('fiscal_receipt', '=', False),
                    '|',
                    ('company_id', '=', self.company_id.id),
                    ('company_id', 'in', self.company_id.child_ids.ids),
                    '|',
                    ('type', 'in', ('out_invoice', 'out_refund')),
                    ('journal_id.sequence_type', 'in',
                     ('autoinv1', 'autoinv2'))
                ])
        seq_ids = set(invoices.mapped('journal_id.sequence_id.id'))
        sequences = obj_seq.browse(seq_ids)
        seq_dict = []
        for sequence in sequences:
            serie = sequence._interpolate(
                sequence.prefix,
                sequence.with_context(ctx)._interpolation_dict_context())
            nr_init = sequence.number_first
            nr_last = sequence.number_last
            for line in sequence.fiscal_ids:
                if line.fiscalyear_id.id == self.period_id.fiscalyear_id.id:
                    nr_init = line.number_first
                    nr_last = line.number_last
                    break
            partner = sequence.partner_id
            tip = 1
            seq = {
                'tip': tip,
                'serieI': regex.sub('', serie),
                'nrI': str(nr_init),
                'nrF': str(nr_last)
            }
            if partner:
                seq['den'] = partner.name
                seq['cui'] = partner._split_vat(
                    partner.vat)[1]
            seq_dict.append(seq)
            seq1 = seq.copy()
            if sequence.sequence_type == 'normal':
                tip = 2
            elif sequence.sequence_type == 'autoinv1':
                tip = 3
            else:
                tip = 4
            inv = invoices.filtered(lambda r: \
                r.journal_id.sequence_id.id == sequence.id).sorted(
                    key=lambda k: k.inv_number)
            seq1['tip'] = tip
            seq1['nrI'] = inv[0].inv_number
            seq1['nrF'] = inv[-1].inv_number
            seq_dict.append(seq1)
        return seq_dict

    @api.multi
    def _generate_lista(self):
        self.ensure_one()
        obj_tax = self.env['account.tax']
        obj_invoice = self.env['account.invoice']
        obj_inv_line = self.env['account.invoice.line']
        comp_curr = self.company_id.currency_id
        caens = ['1071', '4520', '4730', '47761', '47762', '4932', '55101',
                 '55102', '55103', '5630', '0812', '9313', '9602', '9603']
        lista = []
        invoices = obj_invoice.search([
                    ('type', 'in', ['out_invoice', 'out_refund']),
                    ('state', 'in', ['open', 'paid']),
                    ('period_id', '=', self.period_id.id),
                    ('fiscal_receipt', '=', False),
                    '|',
                    ('company_id', '=', self.company_id.id),
                    ('company_id', 'in', self.company_id.child_ids.ids)
                ])
        companies = set(invoices.mapped('company_id.id'))
        for company in self.env['res.company'].browse(companies):
            if company.codcaen.code.zfill(4) in caens:
                comp_inv = invoices.filtered(
                    lambda r: r.company_id.id == company.id)
                cotas = []
                for invoice in comp_inv:
                    cotas += set([tax.id for tax in invoice.tax_ids])
                cotas = set(cotas)
                for cota in obj_tax.browse(cotas):
                    cota_amount = 0
                    if cota.type == 'percent':
                        cota_amount = int(cota.amount * 100)
                    elif cota.type == 'amount':
                        cota_amount = int(cota.amount)
                    cota_inv = comp_inv.filtered(
                        lambda r: cota.id in r.tax_ids.ids)
                    inv_lines = obj_inv_line.search([
                        ('invoice_id', 'in', cota_inv.ids)])
                    bazab = bazas = tvab = tvas = 0
                    for line in inv_lines:
                        inv_curr = line.invoice_id.currency_id
                        inv_date = line.invoice_id.date_invoice
                        if line.product_id.type in ('product', 'consumables'):
                            bazab += inv_curr.with_context(
                                {'date': inv_date}).compute(
                                 line.price_subtotal, comp_curr)
                            tvab += inv_curr.with_context(
                                {'date': inv_date}).compute(
                                line.price_normal_taxes and \
                                line.price_normal_taxes or \
                                line.price_taxes, comp_curr)
                        else:
                            bazas += inv_curr.with_context(
                                {'date': inv_date}).compute(
                                 line.price_subtotal, comp_curr)
                            tvas += inv_curr.with_context(
                                {'date': inv_date}).compute(
                                line.price_normal_taxes and \
                                line.price_normal_taxes or \
                                line.price_taxes, comp_curr)
                    if bazab != 0:
                        bdict = {
                            'caen': company.codcaen.code.zfill(4),
                            'cota': cota_amount,
                            'operat': 1,
                            'valoare': int(round(bazab)),
                            'tva': int(round(tvab))
                        }
                        lista.append(bdict)
                    if bazas != 0:
                        sdict = {
                            'caen': company.codcaen.code.zfill(4),
                            'cota': cota_amount,
                            'operat': 2,
                            'valoare': int(round(bazas)),
                            'tva': int(round(tvas))
                        }
                        lista.append(sdict)
        return lista

    @api.multi
    def _generate_facturi(self):
        self.ensure_one()
        obj_inv_line = self.env['account.invoice.line']
        obj_invoice = self.env['account.invoice']
        obj_period = self.env['account.period']
        comp_curr = self.company_id.currency_id
        facturi = []
        invoices1 = obj_invoice.search([
                    ('fiscal_receipt', '=', False),
                    ('state', '!=', 'draft'),
                    ('period_id', '=', self.period_id.id),
                    '|',
                    ('company_id', '=', self.company_id.id),
                    ('company_id', 'in', self.company_id.child_ids.ids)
                ])
        invoices = invoices1.filtered(lambda r:
            r.amount_total < 0 or r.state == 'cancel' or \
            r.journal_id.sequence_type in ('autoinv1', 'autoinv2'))
        for inv in invoices:
            baza24 = baza20 = baza19 = baza9 = baza5 = 0
            tva24 = tva20 = tva19 = tva9 = tva5 = 0
            inv_curr = inv.currency_id
            inv_date = inv.date_invoice
            inv_type = False
            if inv.type in ('out_invoice', 'out_refund'):
                if inv.state == 'cancel':
                    inv_type = 2
                elif inv.amount_total < 0:
                    inv_type = 1
                elif inv.journal_id.sequence_type == 'autoinv1':
                    inv_type = 3
            elif inv.journal_id.sequence_type == 'autoinv2':
                inv_type = 4
            if inv_type:
                for line in inv.invoice_line:
                    cotas = [tax for tax in line.invoice_line_tax_id]
                    for cota in cotas:
                        cota_amount = 0
                        if cota.type == 'percent':
                            cota_amount = int(cota.amount * 100)
                        elif cota.type == 'amount':
                            cota_amount = int(cota.amount)
                        if cota_amount in (5, 9, 19, 20, 24):
                            if cota_amount == 24:
                                baza24 += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_subtotal, comp_curr)
                                tva24 += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_normal_taxes and \
                                    line.price_normal_taxes or \
                                    line.price_taxes, comp_curr)
                            elif cota_amount == 20:
                                baza20 += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_subtotal, comp_curr)
                                tva20 += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_normal_taxes and \
                                    line.price_normal_taxes or \
                                    line.price_taxes, comp_curr)
                            elif cota_amount == q9:
                                bazaq9 += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_subtotal, comp_curr)
                                tvaq9 += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_normal_taxes and \
                                    line.price_normal_taxes or \
                                    line.price_taxes, comp_curr)
                            elif cota_amount == 9:
                                baza9 += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_subtotal, comp_curr)
                                tva9 += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_normal_taxes and \
                                    line.price_normal_taxes or \
                                    line.price_taxes, comp_curr)
                            elif cota_amount == 5:
                                baza5 += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_subtotal, comp_curr)
                                tva5 += inv_curr.with_context(
                                    {'date': inv_date}).compute(
                                    line.price_normal_taxes and \
                                    line.price_normal_taxes or \
                                    line.price_taxes, comp_curr)
                new_dict = {
                    'tip_factura': inv_type,
                    'serie': inv.inv_serie,
                    'nr': inv.inv_number,
                }
                if inv_type == 3:
                    new_dict.update({
                        'baza24': int(round(baza24)),
                        'baza20': int(round(baza20)),
                        'baza19': int(round(baza19)),
                        'baza9': int(round(baza9)),
                        'baza5': int(round(baza5)),
                        'tva5': int(round(tva20)),
                        'tva9': int(round(tva9)),
                        'tva19': int(round(tva19)),
                        'tva20': int(round(tva20)),
                        'tva24': int(round(tva24))
                    })
                facturi.append(new_dict)
        return facturi

    @api.multi
    def _get_datas(self):
        self.ensure_one()
        ctx = dict(self._context)
        obj_invoice = self.env['account.invoice']
        obj_inv_line = self.env['account.invoice.line']
        obj_period = self.env['account.period']
        obj_sequence = self.env['ir.sequence']
        obj_company = self.env['res.company']
        obj_currency = self.env['res.currency']
        obj_partner = self.env['res.partner']
        obj_tax_obj = self.env['account.tax']

        xmldict = {}

        user = self.env.user
        function = email = ''
        if user.partner_id.function:
            function = user.partner_id.function
        else:
            raise UserError(_('You need to define your Job Position.'))
        uid_name = user.partner_id.name.split()
        uid_fname = ' '.join(uid_name[:-1])
        uid_name = uid_name[-1]

        company = self.company_id

        comm_partner = self.company_id.partner_id.commercial_partner_id
        decl_partner = self.company_id.partner_id
        repr_partner = False
        if company.is_fiscal_repr:
            repr_partner = company.fiscal_repr_id
        int_partner = user.partner_id.commercial_partner_id

        comp_currency = company.currency_id.id
        period = self.period_id
        # Add period date in context for chacking VAT on Payment option
        ctx1 = ctx.copy()
        ctx1.update({'check_date': self.period_id.date_stop})

        xmldict.update({
            'informatii': [],
            'rezumat1': [],
            'rezumat2': [],
            'serieFacturi': [],
            'lista': [],
            'facturi': [],
            'op1': [],
            'op2': [],
            'luna': int(period.code[:2]),
            'an': int(period.code[3:]),
            'tip_D394': "L",
            'sistemTVA': int(comm_partner.with_context(
                ctx1)._check_vat_on_payment()),
            'caen': company.codcaen.code.zfill(4),
            'cui': comm_partner.vat[2:],
            'den': comm_partner.name,
            'adresa': ', '.join([
                comm_partner.state_id and comm_partner.state_id.name,
                comm_partner.city,
                comm_partner.street,
                comm_partner.zip]),
            'totalPlata_A': 0,
            'tip_intocmit': bool(int_partner.is_company) and 0 or 1,
            'cif_intocmit': int_partner.vat and int_partner.vat[2:] or '',
            'den_intocmit': int_partner.name,
            'optiune': int(self.anaf_cross_opt),
        })
        if int_partner.is_company:
            xmldict.update({
                'calitate_intocmit': int_partner.function or '',
            })
        else:
            xmldict.update({
                'functie_intocmit': int_partner.function or '',
            })

        if self.anaf_cross_new_opt:
            xmldict.update({
                'schimb_optiune': int(self.anaf_cross_new_opt),
            })
        if company.phone:
            xmldict.update({
                'telefon': comm_partner.phone
            })
        if company.fax and company.fax != '-':
            xmldict.update({
                'fax': comm_partner.fax,
            })
        if company.email:
            xmldict.update({
                'mail': comm_partner.email,
            })

        if comm_partner.id != decl_partner.id:
            xmldict.update({
                'cifR': decl_partner.vat[2:],
                'denR': decl_partner.name,
                'functie_reprez': decl_partner.function,
                'adresaR': ', '.join([
                    decl_partner.state_id and decl_partner.state_id.name,
                    decl_partner.city,
                    decl_partner.street,
                    decl_partner.zip]),
                'telefonR': decl_partner.phone,
                'faxR': decl_partner.fax,
                'mailR': decl_partner.email,
            })
        else:
            xmldict.update({
                'denR': comm_partner.name,
                'functie_reprez': comm_partner.function,
                'adresaR': ', '.join([
                    comm_partner.state_id and comm_partner.state_id.name,
                    comm_partner.city,
                    comm_partner.street,
                    comm_partner.zip]),
            })

        invoices = obj_invoice.search([
                    ('state', 'in', ['open', 'paid']),
                    ('period_id', '=', period.id),
                    ('fiscal_receipt', '=', False),
                    '|',
                    ('company_id', '=', self.company_id.id),
                    ('company_id', 'in', self.company_id.child_ids.ids)
                ])
        if invoices:
            xmldict.update({
                'op_efectuate': "1"
            })

        if fields.Date.from_string(self.period_id.date_start) < \
                fields.Date.from_string('2016-10-01'):
            op1 = [d for d in self._get_op1(invoices) if \
                d['tip_partener'] == '1']
        else:
            op1 = self._get_op1(invoices)
        invoices1 = obj_invoice.search([
                    ('type', 'in', ('out_invoice', 'out_refund')),
                    ('fiscal_receipt', '=', True),
                    ('journal_id.fiscal_receipt', '=', True),
                    ('state', 'in', ['open', 'paid']),
                    ('period_id', '=', period.id),
                    '|',
                    ('company_id', '=', self.company_id.id),
                    ('company_id', 'in', self.company_id.child_ids.ids)
                ])
        op2 = self._get_op2(invoices1)
        payments = self._get_payments()
        informatii = self._generate_informatii(invoices, payments, op1, op2)
        rezumat1 = self._generate_rezumat1(invoices, payments, op1, op2)
        rezumat2 = self._generate_rezumat2(invoices1, payments, op1, op2)
        serieFacturi = self._get_inv_series()
        lista = self._generate_lista()
        facturi = self._generate_facturi()
        totalPlataA = 0
        totalPlataA += informatii['nrCui1'] + informatii['nrCui2'] + \
            informatii['nrCui3'] + informatii['nrCui4']
        for line in rezumat2:
            totalPlataA += line['bazaA'] + line['bazaL'] + line['bazaAI']
        xmldict.update({
            'totalPlata_A': int(totalPlataA),
            'informatii': informatii,
            'rezumat1': rezumat1,
            'rezumat2': rezumat2,
            'serieFacturi': serieFacturi,
            'lista': lista,
            'facturi': facturi,
            'op1': op1,
            'op2': op2,
        })
        # Change company option regarding ANAF crosschecking
        if self.anaf_cross_new_opt != self.anaf_cross_opt:
            company.anaf_cross_opt = True
        return xmldict

    @api.multi
    def create_xml(self):
        self.ensure_one()
        #self._update_partners()
        ctx = dict(self._context)
        mod_obj = self.env['ir.model.data']
        xml_data = self._get_datas()
        data_file = """<?xml version="1.0"?>
<declaratie394
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="mfp:anaf:dgti:d394:declaratie:v3 D394.xsd"
xmlns="mfp:anaf:dgti:d394:declaratie:v3" """
        for key, val in xml_data.iteritems():
            if key not in ('informatii', 'rezumat1', 'rezumat2',
                           'serieFacturi', 'lista',
                           'facturi', 'op1', 'op2'):
                data_file += """%s="%s" """ % (key, val)
        data_file += """>"""
        data_file += """
<informatii """
        for key, val in xml_data['informatii'].iteritems():
            data_file += """%s="%s" """ % (key, val)
        data_file += """
/>"""
        for client in xml_data['rezumat1']:
            data_file += """
<rezumat1 """
            for key, val in client.iteritems():
                if key != 'detaliu':
                    data_file += """%s="%s" """ % (key, val)
            if client['detaliu']:
                data_file += """>"""
                for line in client['detaliu']:
                    data_file += """
    <detaliu """
                    for det_key, det_val in line.iteritems():
                        data_file += """%s="%s" """ % (det_key, det_val)
                    data_file += """/>"""
                data_file += """
</rezumat1>"""
            else:
                data_file += """/>"""
        for client in xml_data['rezumat2']:
            data_file += """
<rezumat2 """
            for key, val in client.iteritems():
                data_file += """%s="%s" """ % (key, val)
            data_file += """/>"""
        for client in xml_data['serieFacturi']:
            data_file += """
<serieFacturi """
            for key, val in client.iteritems():
                data_file += """%s="%s" """ % (key, val)
            data_file += """/>"""
        for client in xml_data['lista']:
            data_file += """
<lista """
            for key, val in client.iteritems():
                data_file += """%s="%s" """ % (key, val)
            data_file += """/>"""
        for client in xml_data['facturi']:
            data_file += """
<facturi """
            for key, val in client.iteritems():
                data_file += """%s="%s" """ % (key, val)
            data_file += """/>"""
        for client in xml_data['op1']:
            data_file += """
<op1 """
            for key, val in client.iteritems():
                if key != 'op11':
                    data_file += """%s="%s" """ % (key, val)
            if client['op11']:
                data_file += """>"""
                for line in client['op11']:
                    data_file += """<op11 """
                    for key, val in line.iteritems():
                        data_file += """%s="%s" """ % (key, val)
                    data_file += """/>"""                    
                data_file += """
</op1>"""
            else:
                data_file += """/>"""
        for client in xml_data['op2']:
            data_file += """
<op2 """
            for key, val in client.iteritems():
                data_file += """%s="%s" """ % (key, val)
            data_file += """/>"""
        data_file += """
</declaratie394>"""
        ctx['file_save'] = data_file
        self.file_save = base64.encodestring(data_file.encode('utf8'))
        model_data_ids = mod_obj.search([('model', '=', 'ir.ui.view'),
                                         ('name', '=', 'view_d394_new_save')])
        resource_id = model_data_ids[0]['res_id']
        return {
            'name': _('Save'),
            'context': ctx,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'l10n_ro_account_report_d394.d394_new.report',
            'views': [(resource_id, 'form')],
            'view_id': 'view_d394_new_save',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }
