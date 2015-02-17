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


import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp


class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(account_invoice, self).line_get_convert(line, part, date)
        res['not_deductible'] = line.get('not_deductible', False)
        return res


class account_tax(models.Model):
    _inherit = "account.tax"

    not_deductible_tax_id = fields.Many2one(
        'account.tax', string='Not Deductible Tax')


class account_move_line(models.Model):
    _inherit = "account.move.line"

    not_deductible = fields.Boolean('Not Deductible')


class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"

    not_deductible = fields.Boolean('Not Deductible')

    @api.model
    def move_line_get(self, invoice_id):
        res = super(account_invoice_line, self).move_line_get(invoice_id)
        tax_obj = self.env['account.tax']
        inv = self.env['account.invoice'].browse(invoice_id)
        currency = inv.currency_id.with_context(date=inv.date_invoice)
        company_currency = inv.company_id.currency_id

        for line in inv.invoice_line:
            if line.not_deductible:
                mres = self.move_line_get_item(line)
                mres['invl_id'] = line.id
                tax_code_found = False
                taxes = line.invoice_line_tax_id.compute_all(
                    (line.price_unit * (1.0 - (line.discount or 0.0) / 100.0)),
                    line.quantity, line.product_id, inv.partner_id)['taxes']
                for tax in taxes:
                    new_tax = tax_obj.browse(tax['id'])
                    if not new_tax.not_deductible_tax_id:
                        raise except_orm(_('Warning!'),
                                         _("You must define a not deductible tax on '%s'!") % (tax.name,))
                    new_tax = new_tax.not_deductible_tax_id
                    if inv.type in ('out_invoice', 'in_invoice'):
                        price = tax['amount'] * tax['base_sign']
                    else:
                        price = tax['amount'] * tax['ref_base_sign']

                    if inv.type in ('out_invoice', 'in_invoice'):
                        tax_code_id = new_tax.base_code_id.id
                        tax_amount = line.price_subtotal * tax['base_sign']
                    else:
                        tax_code_id = new_tax.ref_base_code_id.id
                        tax_amount = line.price_subtotal * tax['ref_base_sign']

                    mres[
                        'account_id'] = inv.company_id.property_undeductible_account_id.id
                    res.append(dict(mres))
                    res[-1]['price'] = price
                    res[-1]['not_deductible'] = True
                    res[-1]['account_analytic_id'] = False
                    res[-1]['tax_code_id'] = tax_code_id
                    res[-
                        1]['tax_amount'] = currency.compute(tax_amount, company_currency)

                    mres['account_id'] = new_tax.account_collected_id.id
                    mres['type'] = 'dest'
                    if inv.type in ('out_invoice', 'in_invoice'):
                        tax_code_id = new_tax.tax_code_id.id
                        tax_amount = price
                    else:
                        tax_code_id = new_tax.ref_tax_code_id.id
                        tax_amount = price

                    res.append(dict(mres))
                    res[-1]['price'] = -1 * price
                    res[-1]['not_deductible'] = True
                    res[-1]['account_analytic_id'] = False

                    res[-1]['tax_code_id'] = tax_code_id
                    res[-
                        1]['tax_amount'] = currency.compute(tax_amount, company_currency)
        return res
