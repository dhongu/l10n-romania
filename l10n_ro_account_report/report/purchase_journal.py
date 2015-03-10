# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2014 FOREST AND BIOMASS SERVICES ROMANIA SA
#    (http://www.forbiom.eu).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time

from datetime import datetime
from datetime import timedelta

from openerp.osv import osv
from openerp.report import report_sxw

from operator import itemgetter

    
class purchase_journal(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(purchase_journal, self).__init__(cr, uid, name, context=context)

    def set_context(self, object, data, ids, report_type=None):
        """We do the grouping and proccessing of invoices"""
        invoice_obj = self.pool.get('account.invoice')
        period_obj = self.pool.get('account.period')
        currency_obj = self.pool.get('res.currency')

        if data:
            where = [('company_id', '=', data['company_id'][0]), ('state', 'in', ['open', 'paid']), '|', ('period_id', '=', data['periods'][
                0]), ('vat_on_payment', '=', True), ('date_invoice', '<=', period_obj.browse(self.cr, self.uid, data['periods'][0]).date_stop)]
            period_id = data['periods'][0]
            company_id = data['company_id'][0]
            inv_ids = invoice_obj.search(
                self.cr, self.uid, where, order="type desc, date_invoice, number")

        if not isinstance(ids, list):
            inv_ids = [inv_ids]
        # we create temp list that will be used for store invoices by type
        inv = lines = []
        invoices = invoice_obj.browse(self.cr, self.uid, inv_ids)

        period = period_obj.browse(self.cr, self.uid, period_id)
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        if not company_id:
            company_id = user.company_id and user.company_id.id
        company = self.pool.get('res.company').browse(
            self.cr, self.uid, company_id)
        dp = self.pool.get('decimal.precision').precision_get(
            self.cr, self.uid, 'Account')

        if data['journal'] == 'purchase':
            for inv1 in invoices:
                vals = {}
                vals['type'] = inv1.type
                if inv1.vat_on_payment:
                    if inv1.payment_ids:
                        period1 = inv1.payment_ids[0].period_id
                        for payment in inv1.payment_ids:
                            if period1.date_stop < payment.period_id.date_stop:
                                period1 = payment.period_id

                if (inv1.period_id.id == period_id) or (inv1.vat_on_payment and (datetime.strptime(inv1.date_invoice, '%Y-%m-%d') < (datetime.strptime(period.date_start, '%Y-%m-%d'))) and (inv1.state == 'open' or (inv1.state == 'paid' and (period1.date_stop >= period.date_start)))):
                    vals['total_base'] = vals['base_neex'] = vals['base_serv'] = vals['base_exig'] = vals['base_invers'] = vals['base_ded1'] = vals[
                        'base_ded2'] = vals['base_24'] = vals['base_9'] = vals['base_5'] = vals['base_0'] = vals['base_import'] = vals['base_bun'] = 0.00
                    vals['total_vat'] = vals['tva_neex'] = vals['tva_24'] = vals['tva_9'] = vals['tva_5'] = vals[
                        'tva_exig'] = vals['tva_bun'] = vals['tva_invers'] = vals['tva_serv'] = vals['tva_import'] = 0.00
                    vals['neimp'] = vals['scutit'] = 0.00
                    vals['payments'] = []
                    vals['number'] = inv1.supplier_invoice_number and inv1.supplier_invoice_number or inv1.internal_number
                    vals['date'] = inv1.date_invoice
                    vals['partner'] = inv1.partner_id.name
                    vals['vat'] = ''
                    if inv1.partner_id.vat:
                        if inv1.partner_id.vat_subjected:
                            vals['vat'] = inv1.partner_id.vat
                        else:
                            vals['vat'] = inv1.partner_id.vat[2:]
                    vals['total'] = currency_obj.compute(
                        self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, inv1.amount_total, context={'date': inv1.date_invoice})
                    if not inv1.vat_on_payment and not inv1.fiscal_position or (inv1.fiscal_position and ('National' in inv1.fiscal_position.name)):
                        if inv1.tax_line:
                            for tax_line in inv1.tax_line:
                                if ' 0' not in tax_line.name:
                                    vals['total_base'] += currency_obj.compute(
                                        self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.base, context={'date': inv1.date_invoice})
                                    vals['total_vat'] += currency_obj.compute(
                                        self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.amount, context={'date': inv1.date_invoice})
                        else:
                            if inv1.partner_id.vat and 'RO' in inv1.partner_id.vat.upper():
                                vals['base_0'] += currency_obj.compute(
                                    self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, inv1.amount_total, context={'date': inv1.date_invoice}) or 0.00
                            else:
                                vals['scutit'] += currency_obj.compute(
                                    self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, inv1.amount_total, context={'date': inv1.date_invoice}) or 0.00

                    vals['residual'] = currency_obj.compute(
                        self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, inv1.residual, context={'date': inv1.date_invoice})
                    vals['tva_neex_res'] = 0.00
                    if inv1.vat_on_payment:
                        total_base = total_vat = paid = 0.00
                        base_neex = tva_neex = 0.00
                        for payment in inv1.payment_ids:
                            if payment.date <= period.date_stop:
                                paid += payment.credit or payment.debit
                                for line in payment.move_id.line_id:
                                    if (inv1.number in line.name) and (line.account_id.type == 'other') and line.tax_code_id and ((inv1.type in ['out_invoice', 'out_refund'] and ((inv1.amount_total > 0 and line.tax_amount > 0) or (inv1.amount_total < 0 and line.tax_amount < 0))) or (inv1.type in ['in_invoice', 'in_refund'] and ((inv1.amount_total > 0 and line.tax_amount > 0) or (inv1.amount_total < 0 and line.tax_amount < 0)))):
                                        if 'BAZA' in line.tax_code_id.name.upper():
                                            base_neex += inv1.amount_tax != 0.00 and currency_obj.compute(
                                                self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, line.tax_amount, dp, context={'date': inv1.date_invoice}) or 0.00
                                        else:
                                            tva_neex += inv1.amount_tax != 0.00 and currency_obj.compute(
                                                self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, line.tax_amount, dp, context={'date': inv1.date_invoice}) or 0.00

                        if inv1.tax_line:
                            for tax_line in inv1.tax_line:
                                if ' 0' not in tax_line.name:
                                    total_base += currency_obj.compute(
                                        self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.base, dp, context={'date': inv1.date_invoice})
                                    total_vat += currency_obj.compute(
                                        self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.amount, dp, context={'date': inv1.date_invoice})
                        vals['base_neex'] = total_base - base_neex
                        vals['tva_neex'] = total_vat - tva_neex
                        if vals['tva_neex'] < 0.01 and vals['tva_neex'] > -0.01:
                            vals['base_neex'] = vals['tva_neex'] = 0.00

                    if inv1.period_id.id == period_id and inv1.tax_line:
                        for line in inv1.invoice_line:
                            if not line.invoice_line_tax_id:
                                if (inv1.partner_id.vat and 'RO' in inv1.partner_id.vat.upper()) or not inv1.partner_id.vat:
                                    vals['base_0'] += currency_obj.compute(
                                        self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, line.price_subtotal, context={'date': inv1.date_invoice}) or 0.00
                                else:
                                    vals['scutit'] += currency_obj.compute(
                                        self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, line.price_subtotal, context={'date': inv1.date_invoice}) or 0.00
                    base_24 = base_9 = base_5 = base_0 = base_exig = tva_24 = tva_9 = tva_5 = tva_0 = tva_exig = 0.00
                    for tax_line in inv1.tax_line:
                        if not inv1.vat_on_payment:
                            if inv1.partner_id.vat and 'RO' in inv1.partner_id.vat.upper():
                                if inv1.fiscal_position and ('Taxare Inversa' in inv1.fiscal_position.name):
                                    if 'ACH-C' in tax_line.name.upper():
                                        vals['base_invers'] += currency_obj.compute(
                                            self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.base, context={'date': inv1.date_invoice}) or 0.00
                                        vals['tva_invers'] += (-1) * currency_obj.compute(
                                            self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.amount, context={'date': inv1.date_invoice}) or 0.00
                                        if ' 24' in tax_line.name:
                                            base_24 += currency_obj.compute(
                                                self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.base, context={'date': inv1.date_invoice}) or 0.00
                                            tva_24 += (-1) * currency_obj.compute(self.cr, self.uid, inv1.currency_id.id,
                                                                                  company.currency_id.id, tax_line.amount, context={'date': inv1.date_invoice}) or 0.00
                                        if ' 9' in tax_line.name:
                                            base_9 += currency_obj.compute(self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.base, context={
                                                                           'date': inv1.date_invoice}) or 0.00
                                            tva_9 += (-1) * currency_obj.compute(self.cr, self.uid, inv1.currency_id.id,
                                                                                 company.currency_id.id, tax_line.amount, context={'date': inv1.date_invoice}) or 0.00
                                        if ' 5' in tax_line.name:
                                            base_5 += currency_obj.compute(self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.base, context={
                                                                           'date': inv1.date_invoice}) or 0.00
                                            tva_5 += (-1) * currency_obj.compute(self.cr, self.uid, inv1.currency_id.id,
                                                                                 company.currency_id.id, tax_line.amount, context={'date': inv1.date_invoice}) or 0.00
                                        if ' 0' in tax_line.name:
                                            base_0 += currency_obj.compute(self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.base, context={
                                                                           'date': inv1.date_invoice}) or 0.00
                                        if (' 24' in tax_line.name) or (' 9' in tax_line.name) or (' 5' in tax_line.name):
                                            base_exig += currency_obj.compute(
                                                self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.base, context={'date': inv1.date_invoice}) or 0.00
                                            tva_exig += (-1) * currency_obj.compute(self.cr, self.uid, inv1.currency_id.id,
                                                                                    company.currency_id.id, tax_line.amount, context={'date': inv1.date_invoice}) or 0.00
                                else:
                                    if ' 24' in tax_line.name:
                                        vals['base_24'] += currency_obj.compute(
                                            self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.base, context={'date': inv1.date_invoice}) or 0.00
                                        vals['tva_24'] += currency_obj.compute(
                                            self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.amount, context={'date': inv1.date_invoice}) or 0.00
                                    if ' 9' in tax_line.name:
                                        vals['base_9'] += currency_obj.compute(
                                            self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.base, context={'date': inv1.date_invoice}) or 0.00
                                        vals['tva_9'] += currency_obj.compute(
                                            self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.amount, context={'date': inv1.date_invoice}) or 0.00
                                    if ' 5' in tax_line.name:
                                        vals['base_5'] += currency_obj.compute(
                                            self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.base, context={'date': inv1.date_invoice}) or 0.00
                                        vals['tva_5'] += currency_obj.compute(
                                            self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.amount, context={'date': inv1.date_invoice}) or 0.00
                                    if ' 0' in tax_line.name:
                                        vals['base_0'] += currency_obj.compute(
                                            self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.base, context={'date': inv1.date_invoice}) or 0.00
                                    if (' 24' in tax_line.name) or (' 9' in tax_line.name) or (' 5' in tax_line.name):
                                        vals['base_exig'] += currency_obj.compute(
                                            self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.base, context={'date': inv1.date_invoice}) or 0.00
                                        vals['tva_exig'] += currency_obj.compute(
                                            self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.amount, context={'date': inv1.date_invoice}) or 0.00

                            if inv1.fiscal_position and ('Intra-Comunitar Bunuri' in inv1.fiscal_position.name):
                                if 'ACH_C' in tax_line.name.upper():
                                    vals['base_bun'] += currency_obj.compute(
                                        self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.base, context={'date': inv1.date_invoice}) or 0.00
                                    vals['tva_bun'] += (-1) * currency_obj.compute(self.cr, self.uid, inv1.currency_id.id,
                                                                                   company.currency_id.id, tax_line.amount, context={'date': inv1.date_invoice}) or 0.00

                            if inv1.fiscal_position and ('Intra-Comunitar Servicii' in inv1.fiscal_position.name):
                                if 'ACH_C' in tax_line.name.upper():
                                    vals['base_serv'] += currency_obj.compute(
                                        self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.base, context={'date': inv1.date_invoice}) or 0.00
                                    vals['tva_serv'] += (-1) * currency_obj.compute(self.cr, self.uid, inv1.currency_id.id,
                                                                                    company.currency_id.id, tax_line.amount, context={'date': inv1.date_invoice}) or 0.00

                            if inv1.fiscal_position and ('Scutite' in inv1.fiscal_position.name):
                                if 'SCUTIT' in tax_line.name.upper():
                                    vals['scutit'] += currency_obj.compute(
                                        self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.base, context={'date': inv1.date_invoice}) or 0.00

                            if inv1.fiscal_position and ('Neimpozabile' in inv1.fiscal_position.name):
                                if 'NEIMP' in tax_line.name.upper():
                                    vals['neimp'] += currency_obj.compute(
                                        self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.base, context={'date': inv1.date_invoice}) or 0.00

                            if inv1.fiscal_position and ('Extra-Comunitar' in inv1.fiscal_position.name):
                                vals['base_import'] += currency_obj.compute(
                                    self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.base, context={'date': inv1.date_invoice}) or 0.00
                                vals['tva_import'] += currency_obj.compute(
                                    self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, tax_line.amount, context={'date': inv1.date_invoice}) or 0.00

                    if inv1.vat_on_payment:
                        vals['vat_on_payment'] = '1'
                        vals['total_base'] = vals['total_vat'] = 0.00
                        if inv1.payment_ids:
                            for payment in inv1.payment_ids:
                                if payment.period_id.id == period_id:
                                    pay = {}
                                    pay['base_exig'] = pay['tva_exig'] = 0.00
                                    pay['base_24'] = pay[
                                        'base_9'] = pay['base_5'] = 0.00
                                    pay['tva_24'] = pay[
                                        'tva_9'] = pay['tva_5'] = 0.00
                                    pay['number'] = str(
                                        payment.move_id.ref or payment.move_id.name)
                                    pay['date'] = payment.move_id.date
                                    pay['amount'] = currency_obj.compute(
                                        self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, payment.credit or payment.debit, context={'date': inv1.date_invoice})
                                    for line in payment.move_id.line_id:
                                        if inv1.number in line.name:
                                            if line.tax_code_id and ' 24' in line.tax_code_id.name:
                                                if 'BAZA' in line.tax_code_id.name.upper():
                                                    pay['base_24'] += inv1.amount_tax != 0.00 and currency_obj.compute(self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, line.tax_amount, self.pool.get(
                                                        'decimal.precision').precision_get(self.cr, self.uid, 'Account'), context={'date': inv1.date_invoice}) or 0.00
                                                else:
                                                    pay['tva_24'] += inv1.amount_tax != 0.00 and currency_obj.compute(
                                                        self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, line.tax_amount, context={'date': inv1.date_invoice}) or 0.00
                                            if line.tax_code_id and ' 9' in line.tax_code_id.name:
                                                if 'BAZA' in line.tax_code_id.name.upper():
                                                    pay['base_9'] += inv1.amount_tax != 0.00 and currency_obj.compute(self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, line.tax_amount, self.pool.get(
                                                        'decimal.precision').precision_get(self.cr, self.uid, 'Account'), context={'date': inv1.date_invoice}) or 0.00
                                                else:
                                                    pay['tva_9'] += inv1.amount_tax != 0.00 and currency_obj.compute(
                                                        self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, line.tax_amount, context={'date': inv1.date_invoice}) or 0.00
                                            if line.tax_code_id and ' 5' in line.tax_code_id.name:
                                                if 'BAZA' in line.tax_code_id.name.upper():
                                                    pay['base_5'] += inv1.amount_tax != 0.00 and currency_obj.compute(self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, line.tax_amount, self.pool.get(
                                                        'decimal.precision').precision_get(self.cr, self.uid, 'Account'), context={'date': inv1.date_invoice}) or 0.00
                                                else:
                                                    pay['tva_5'] += inv1.amount_tax != 0.00 and currency_obj.compute(
                                                        self.cr, self.uid, inv1.currency_id.id, company.currency_id.id, line.tax_amount, context={'date': inv1.date_invoice}) or 0.00
                                    pay['base_exig'] += pay['base_24'] + \
                                        pay['base_9'] + pay['base_5']
                                    pay['tva_exig'] += pay['tva_24'] + \
                                        pay['tva_9'] + pay['tva_5']
                                    vals['payments'].append(pay)
                                    vals['total_base'] += pay['base_exig']
                                    vals['total_vat'] += pay['tva_exig']
                                    vals['base_24'] += pay['base_24']
                                    vals['tva_24'] += pay['tva_24']
                                    vals['base_9'] += pay['base_9']
                                    vals['tva_9'] += pay['tva_9']
                                    vals['base_5'] += pay['base_5']
                            vals['payments'].sort(
                                key=itemgetter("date", "number"))
                        else:
                            pay = {}
                            pay['number'] = pay['date'] = ''
                            pay['amount'] = 0.00
                            pay['base_exig'] = pay['tva_exig'] = 0.00
                            pay['base_24'] = pay[
                                'base_9'] = pay['base_5'] = 0.00
                            pay['tva_24'] = pay['tva_9'] = pay['tva_5'] = 0.00
                            vals['payments'].append(pay)

                    else:
                        pay = {}
                        pay['number'] = pay['date'] = ''
                        pay['amount'] = 0.00
                        pay['base_exig'] = pay['tva_exig'] = 0.00
                        pay['base_24'] = pay['base_9'] = pay['base_5'] = 0.00
                        pay['tva_24'] = pay['tva_9'] = pay['tva_5'] = 0.00
                        vals['payments'].append(pay)
                if 'number' in vals.keys():
                    inv.append(vals)

        lines = [inv1 for inv1 in inv if inv1[
            'type'] in ['in_invoice', 'in_refund']]
        self.localcontext.update({'lines': lines, 'data': data})
        return True


class report_purchase_journal(osv.AbstractModel):
    _name = 'report.l10n_ro_account_report.report_purchase_journal'
    _inherit = 'report.abstract_report'
    _template = 'l10n_ro_account_report.report_purchase_journal'
    _wrapped_report_class = purchase_journal


class report_purchase_journal_html(osv.AbstractModel):
    _name = 'report.l10n_ro_account_report.report_purchase_journal_html'
    _inherit = 'report.abstract_report'
    _template = 'l10n_ro_account_report.report_purchase_journal_html'
    _wrapped_report_class = purchase_journal

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
