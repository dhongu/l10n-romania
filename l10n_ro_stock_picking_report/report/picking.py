# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Deltatech All Rights Reserved
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
##############################################################################


import time

from odoo import api, models
from odoo.tools import formatLang




class ReportPickingDelivery(models.AbstractModel):
    _name = 'report.abstract_report.delivery_report'
    _template = None


    @api.model
    def get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(self._template)
        return  {
            'doc_ids': docids,
            'doc_model': report.model,
            'data': data,
            'time': time,
            'docs': self.env[report.model].browse(docids),
            'formatLang': self._formatLang,
            'get_line': self._get_line,
            'get_totals': self._get_totals,
        }




    def _formatLang(self, value, **kwargs):
        if 'date' in kwargs:
            return value
        return formatLang(self.env, value, **kwargs)

    def _get_line(self, move_line):
        res = {'price': 0.0, 'amount': 0.0, 'tax': 0.0, 'amount_tax': 0.0}
        if move_line.sale_line_id:
            line = move_line.sale_line_id

            if line.product_uom_qty != 0:
                res['price'] = line.price_subtotal / line.product_uom_qty
            else:
                res['price'] = 0.0


            taxes_sale = line.product_id.taxes_id.compute_all(res['price'],
                                                              quantity=move_line.product_qty,
                                                              product=line.product_id)

            res['tax'] = taxes_sale['total_included'] - taxes_sale['total_excluded']
            res['amount'] = taxes_sale['total_excluded']
            res['amount_tax'] = taxes_sale['total_included']

        return res

    def _get_totals(self, move_lines):
        res = {'amount': 0.0, 'tax': 0.0, 'amount_tax': 0.0}
        for move in move_lines:
            line = self._get_line(move)
            res['amount'] += line['amount']
            res['tax'] += line['tax']
            res['amount_tax'] += line['amount_tax']
        return res





class ReportPickingReception(models.AbstractModel):
    _name = 'report.abstract_report.reception_report'
    _template = None


    @api.model
    def get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(self._template)
        return  {
            'doc_ids': docids,
            'doc_model': report.model,
            'data': data,
            'time': time,
            'docs': self.env[report.model].browse(docids),
            'formatLang': self._formatLang,
            'get_line': self._get_line,
            'get_totals': self._get_totals,
        }



    def _formatLang(self, value, **kwargs):
        #todo: de tratat : formatLang(totals['amount'], currency_obj=res_company.currency_id)
        #todo: de tratat : formatLang(o.date, date=True)
        if 'date' in kwargs:
            return value
        return formatLang(self.env, value, **kwargs)

    def _get_line(self, move_line):
        res = {'price': 0.0, 'amount': 0.0, 'tax': 0.0,
               'amount_tax': 0.0, 'amount_sale': 0.0, 'margin': 0.0}

        if move_line.purchase_line_id:
            # todo: ce fac cu receptii facute ca preturi diferite ????
            line = move_line.purchase_line_id

            # todo: de verificat daca pretul din miscare este actualizat inaiante de confirmarea transferului pentru a se actualiza cursul valutar !!
            res['price'] = move_line.price_unit  # pretul caculat la genereare miscarii
            taxes = line.taxes_id.compute_all(res['price'],
                                              quantity=move_line.product_qty,
                                              product=move_line.product_id,
                                              partner=move_line.partner_id)

            res['tax'] = taxes['total_included'] - taxes['total_excluded']
            res['amount'] = taxes['total_excluded']
            res['amount_tax'] = taxes['total_included']

            taxes_sale = line.product_id.taxes_id.compute_all(line.product_id.list_price,
                                                              quantity=move_line.product_qty,
                                                              product=line.product_id)
            res['amount_sale'] = taxes_sale['total_included']
            res['price'] = res['price'] * line.product_uom._compute_quantity(1, line.product_id.uom_id)
            if res['amount_tax'] != 0.0:
                res['margin'] = 100 * (taxes_sale['total_included'] - res['amount_tax']) / res['amount_tax']
            else:
                res['margin'] = 0.0
        else:
            # receptie fara comanda de aprovizionare

            value = 0.0
            for quant in move_line.quant_ids:
                value += quant.inventory_value

            currency = move_line.company_id.currency_id

            res['amount'] = currency.round(value)
            if move_line.product_uom_qty != 0:
                res['price'] = currency.round(value) / move_line.product_uom_qty
            else:
                res['price'] = 0.0

            taxes = move_line.product_id.supplier_taxes_id.compute_all(res['price'], currency=currency,
                                                                       quantity=move_line.product_uom_qty,
                                                                       product=move_line.product_id,
                                                                       partner=move_line.partner_id)

            res['tax'] = taxes['total_included'] - taxes['total_excluded']
            res['amount_tax'] = taxes['total_included']

            taxes_sale = move_line.product_id.taxes_id.compute_all(move_line.product_id.list_price, currency=currency,
                                                                   quantity=move_line.product_uom_qty,
                                                                   product=move_line.product_id)

            res['amount_sale'] = taxes_sale['total_included']
            if taxes['total_included'] != 0.0:
                res['margin'] = 100 * (taxes_sale['total_included'] - taxes['total_included']) / taxes['total_included']
            else:
                res['margin'] = 0.0
        print res
        return res

    def _get_totals(self, move_lines):
        res = {'amount': 0.0, 'tax': 0.0, 'amount_tax': 0.0}
        for move in move_lines:
            line = self._get_line(move)
            res['amount'] += line['amount']
            res['tax'] += line['tax']
            res['amount_tax'] += line['amount_tax']
        return res


class report_delivery(models.AbstractModel):
    _name = 'report.l10n_ro_stock_picking_report.report_delivery'
    _inherit = 'report.abstract_report.delivery_report'
    _template = 'l10n_ro_stock_picking_report.report_delivery'
    # _wrapped_report_class = picking_delivery


class report_delivery_price(models.AbstractModel):
    _name = 'report.l10n_ro_stock_picking_report.report_delivery_price'
    _inherit = 'report.abstract_report.delivery_report'
    _template = 'l10n_ro_stock_picking_report.report_delivery_price'
    # _wrapped_report_class = picking_delivery


class report_consume_voucher(models.AbstractModel):
    _name = 'report.l10n_ro_stock_picking_report.report_consume_voucher'
    _inherit = 'report.abstract_report.delivery_report'
    _template = 'l10n_ro_stock_picking_report.report_consume_voucher'
    # _wrapped_report_class = picking_delivery


class report_internal_transfer(models.AbstractModel):
    _name = 'report.l10n_ro_stock_picking_report.report_internal_transfer'
    _inherit = 'report.abstract_report.delivery_report'
    _template = 'l10n_ro_stock_picking_report.report_internal_transfer'
    # _wrapped_report_class = picking_delivery


class report_reception(models.AbstractModel):
    _name = 'report.l10n_ro_stock_picking_report.report_reception'
    _inherit = 'report.abstract_report.reception_report'
    _template = 'l10n_ro_stock_picking_report.report_reception'
    # _wrapped_report_class = picking_reception


class report_reception_no_tax(models.AbstractModel):
    _name = 'report.l10n_ro_stock_picking_report.report_reception_no_tax'
    _inherit = 'report.abstract_report.reception_report'
    _template = 'l10n_ro_stock_picking_report.report_reception_no_tax'
    # _wrapped_report_class = picking_reception


class report_reception_sale_price(models.AbstractModel):
    _name = 'report.l10n_ro_stock_picking_report.report_reception_sale_price'
    _inherit = 'report.abstract_report.reception_report'
    _template = 'l10n_ro_stock_picking_report.report_reception_sale_price'
    # _wrapped_report_class = picking_reception


