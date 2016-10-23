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
from odoo.report import report_sxw
from odoo.osv import osv


class picking_delivery(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(picking_delivery, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_line': self._get_line,
            'get_totals': self._get_totals
        })

    def _get_line(self, move_line):
        res = {'price': 0.0, 'amount': 0.0, 'tax': 0.0, 'amount_tax': 0.0}
        if move_line.procurement_id.sale_line_id:
            line = move_line.procurement_id.sale_line_id

            res['tax'] = line.price_tax
            res['amount'] = line.price_subtotal
            res['amount_tax'] = line.price_total

            if move_line.product_uom_qty <> 0:
                res['price'] = line.order_id.pricelist_id.currency_id.round(res['amount']) / move_line.product_uom_qty
            else:
                res['price'] = 0.0


        return res

    def _get_totals(self, move_lines):
        res = {'amount': 0.0, 'tax': 0.0, 'amount_tax': 0.0}
        for move in move_lines:
            line = self._get_line(move)
            res['amount'] += line['amount']
            res['tax'] += line['tax']
            res['amount_tax'] += line['amount_tax']
        return res


class picking_reception(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(picking_reception, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_line': self._get_line,
            'get_totals': self._get_totals,
        })

    def _get_line(self, move_line):
        res = {'price': 0.0, 'amount': 0.0, 'tax': 0.0,
               'amount_tax': 0.0, 'amount_sale': 0.0, 'margin': 0.0}

        if not move_line.quant_ids  and  move_line.purchase_line_id:
            line = move_line.purchase_line_id

            res['tax'] = line.price_tax
            res['amount'] = line.price_subtotal
            res['amount_tax'] = line.price_total

            currency = line.currency_id


            if move_line.product_uom_qty != 0.0:
                res['price'] = currency.round(res['amount']) / move_line.product_uom_qty
            else:
                res['price'] = 0.0


            taxes_sale = line.product_id.taxes_id.compute_all(line.product_id.list_price, currency=currency,
                                                              quantity=move_line.product_uom_qty,
                                                              product=line.product_id)
            res['amount_sale'] = currency.round(taxes_sale['total_included'])
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

            res['tax'] = currency.round(taxes['total_included'] - taxes['total_excluded'])
            res['amount_tax'] = currency.round(taxes['total_included'])

            taxes_sale = move_line.product_id.taxes_id.compute_all(move_line.product_id.list_price, currency=currency,
                                                                   quantity=move_line.product_uom_qty,
                                                                   product=move_line.product_id)

            res['amount_sale'] = currency.round(taxes_sale['total_included'])
            if taxes['total_included'] != 0.0:
                res['margin'] = 100 * (taxes_sale['total_included'] - taxes['total_included']) / taxes['total_included']
            else:
                res['margin'] = 0.0
        return res

    def _get_totals(self, move_lines):
        res = {'amount': 0.0, 'tax': 0.0, 'amount_tax': 0.0}
        for move in move_lines:
            line = self._get_line(move)
            res['amount'] += line['amount']
            res['tax'] += line['tax']
            res['amount_tax'] += line['amount_tax']
        return res


class report_delivery(osv.AbstractModel):
    _name = 'report.l10n_ro_stock_picking_report.report_delivery'
    _inherit = 'report.abstract_report'
    _template = 'l10n_ro_stock_picking_report.report_delivery'
    _wrapped_report_class = picking_delivery


class report_delivery_price(osv.AbstractModel):
    _name = 'report.l10n_ro_stock_picking_report.report_delivery_price'
    _inherit = 'report.abstract_report'
    _template = 'l10n_ro_stock_picking_report.report_delivery_price'
    _wrapped_report_class = picking_delivery


class report_consume_voucher(osv.AbstractModel):
    _name = 'report.l10n_ro_stock_picking_report.report_consume_voucher'
    _inherit = 'report.abstract_report'
    _template = 'l10n_ro_stock_picking_report.report_consume_voucher'
    _wrapped_report_class = picking_delivery


class report_internal_transfer(osv.AbstractModel):
    _name = 'report.l10n_ro_stock_picking_report.report_internal_transfer'
    _inherit = 'report.abstract_report'
    _template = 'l10n_ro_stock_picking_report.report_internal_transfer'
    _wrapped_report_class = picking_delivery


class report_reception(osv.AbstractModel):
    _name = 'report.l10n_ro_stock_picking_report.report_reception'
    _inherit = 'report.abstract_report'
    _template = 'l10n_ro_stock_picking_report.report_reception'
    _wrapped_report_class = picking_reception


class report_reception_no_tax(osv.AbstractModel):
    _name = 'report.l10n_ro_stock_picking_report.report_reception_no_tax'
    _inherit = 'report.abstract_report'
    _template = 'l10n_ro_stock_picking_report.report_reception_no_tax'
    _wrapped_report_class = picking_reception


class report_reception_sale_price(osv.AbstractModel):
    _name = 'report.l10n_ro_stock_picking_report.report_reception_sale_price'
    _inherit = 'report.abstract_report'
    _template = 'l10n_ro_stock_picking_report.report_reception_sale_price'
    _wrapped_report_class = picking_reception

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
