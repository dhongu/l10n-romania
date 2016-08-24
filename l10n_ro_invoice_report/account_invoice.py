# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Deltatech All Rights Reserved
#                    Dorin Hongu <dhongu(@)gmail(.)com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
##############################################################################


from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class res_partner(models.Model):
    _inherit = 'res.partner'
    mean_transp = fields.Char(  string='Mean transport')

class account_invoice(models.Model):
    _inherit = "account.invoice"


    delegate_id = fields.Many2one('res.partner', string='Delegate',
                                  readonly=True, states={'draft': [('readonly', False)]}, domain=[('is_company', '=', False)])
 

    mean_transp = fields.Char(  string='Mean transport', readonly=True,  states={'draft': [('readonly', False)]},)


    @api.onchange('delegate_id')
    def on_change_delegate_id(self):
        if self.delegate_id:
            self.mean_transp =  self.delegate_id.mean_transp

class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_id', 'quantity',
                 'product_id', 'invoice_id.partner_id',
                 'invoice_id.currency_id')
    def _compute_price(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = self.invoice_line_tax_id.compute_all(
            price, self.quantity, product=self.product_id,
            partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total']
        self.price_taxes = taxes['total_included'] - taxes['total']
        taxes_unit = self.invoice_line_tax_id.compute_all(
            price, 1, product=self.product_id,
            partner=self.invoice_id.partner_id)
        self.price_unit_without_taxes = taxes_unit['total']
        # Compute normal taxes in case of Customer Invoices to have the value
        # in Inverse Taxation
        if self.invoice_id.type in ['out_invoice', 'out_refund']:
            normal_taxes = self.product_id.taxes_id.compute_all(
                price, self.quantity, product=self.product_id,
                partner=self.invoice_id.partner_id)
            self.price_normal_taxes = \
                normal_taxes['total_included'] - normal_taxes['total']
        if self.invoice_id:
            self.price_subtotal = self.invoice_id.currency_id.round(
                self.price_subtotal)
            self.price_taxes = self.invoice_id.currency_id.round(
                self.price_taxes)
            self.price_unit_without_taxes = self.invoice_id.currency_id.round(
                self.price_unit_without_taxes)
            self.price_normal_taxes = self.invoice_id.currency_id.round(
                self.price_normal_taxes)

 

    sequence = fields.Integer(string='Sequence', default=1,
        help="Gives the sequence of this line when displaying the invoice.")

    price_unit_without_taxes = fields.Float(string='Unit Price without taxes',
                                            store=True, readonly=True, compute='_compute_price')

    price_taxes = fields.Float(string='Taxes', digits=dp.get_precision('Account'),
                               store=True, readonly=True, compute='_compute_price')
 
    price_normal_taxes = fields.Float(
        string='Normal Taxes', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_price')
 
