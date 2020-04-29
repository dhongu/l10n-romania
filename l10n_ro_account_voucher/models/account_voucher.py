# -*- coding: utf-8 -*-
# ©  2017 Terrabit
# See README.rst file on addons root folder for license details

from odoo import fields, models, api, _



class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    # @api.multi
    # def first_move_line_get(self, move_id, company_currency, current_currency):
    #     move_line = super(AccountVoucher, self).first_move_line_get(move_id, company_currency, current_currency)
    #     if self.pay_now == 'pay_now' and self.amount > 0:
    #         move_line_411 = dict(move_line)
    #         move_line_411['account_id'] = self.partner_id.property_account_receivable_id.id \
    #             if self.voucher_type == 'sale' else self.partner_id.property_account_payable_id.id
    #         self.env['account.move.line'].create(move_line_411)
    #         move_line_411['debit'], move_line_411['credit'] = move_line_411['credit'], move_line_411['debit']
    #         self.env['account.move.line'].create(move_line_411)
    #
    #     return move_line


class AccountVoucherLine(models.Model):
    _inherit = 'account.voucher.line'


    price_total = fields.Monetary( readonly=False, inverse='_set_subtotal', compute='_compute_subtotal', store=False)


    @api.one
    @api.depends('price_unit', 'tax_ids', 'quantity', 'product_id', 'voucher_id.currency_id')
    def _compute_subtotal(self):
        self.price_subtotal = self.quantity * self.price_unit
        self.price_total = self.quantity * self.price_unit
        if self.tax_ids:
            taxes = self.tax_ids.compute_all(self.price_unit, self.voucher_id.currency_id, self.quantity, product=self.product_id, partner=self.voucher_id.partner_id)
            self.price_subtotal = taxes['total_excluded']
            self.price_total = taxes['total_included']



    @api.onchange('price_total')
    def _set_subtotal(self):
        quantity = self.quantity or 1
        price_unit = self.price_total  /  quantity
        price_subtotal = self.price_total
        if self.tax_ids:
            tva = 1
            for tax in self.tax_ids:
                tva += tax.amount / 100
            price_subtotal = self.price_total / tva
            price_unit = price_subtotal / quantity
        self.price_unit = price_unit
        self.price_subtotal = price_subtotal