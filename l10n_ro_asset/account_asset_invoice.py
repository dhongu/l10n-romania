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
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp
from openerp.osv import osv


class account_asset_asset(models.Model):
    _name = 'account.asset.asset'
    _inherit = 'account.asset.asset'

    # Invoice History for Service Assets
    inv_line_id = fields.Many2one(
        'account.invoice.line', string='Invoice Line', readonly=True, states={'draft': [('readonly', False)]})
    invoice_id = fields.Many2one('account.invoice', related='inv_line_id.invoice_id',
                                 string='Invoice', readonly=True, states={'draft': [('readonly', False)]})


class account_invoice_line(models.Model):
    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'

    asset_category_id = fields.Many2one(
        'account.asset.category', string='Asset Category', domain=[('asset_type', '=', 'service')])
    asset_ids = fields.One2many(
        'account.asset.asset', 'inv_line_id', string="Assets")

    def asset_create(self, cr, uid, lines, context=None):
        context = context or {}
        asset_obj = self.pool.get('account.asset.asset')
        currency_obj = self.pool.get('res.currency')
        for line in lines:
            if line.asset_category_id:
                ctx1 = context.copy()
                ctx1.update({'date': line.invoice_id.date_invoice})
                price = currency_obj.compute(
                    cr, uid, line.invoice_id.currency_id.id, line.invoice_id.company_id.currency_id.id, line.price_subtotal, context=ctx1)
                if line.asset_category_id.prorata:
                    new_date = line.invoice_id.date_invoice
                else:
                    new_date = datetime.strptime(
                        line.invoice_id.date_invoice, "%Y-%m-%d") + relativedelta(day=1, months=+1)
                vals = {
                    'name': line.name,
                    'code': line.invoice_id.number or False,
                    'category_id': line.asset_category_id.id,
                    'asset_type': line.asset_category_id.asset_type,
                    'purchase_value': round(price / line.quantity, 2),
                    'partner_id': line.invoice_id.partner_id.id,
                    'company_id': line.invoice_id.company_id.id,
                    'currency_id': line.invoice_id.company_id.currency_id.id,
                    'purchase_date': new_date,
                    'entry_date': line.invoice_id.date_invoice,
                    'product_id': line.product_id.id,
                    'inv_line_id': line.id,
                }
                changed_vals = asset_obj.onchange_category_id(
                    cr, uid, [], vals['category_id'], context=context)
                vals.update(changed_vals['value'])
                qty = line.quantity
                while qty > 0:
                    qty -= 1
                    asset_id = asset_obj.create(cr, uid, vals, context=context)
                    if line.asset_category_id.open_asset:
                        asset_obj.validate(
                            cr, uid, [asset_id], context=context)
        return True


class account_invoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    @api.multi
    def action_cancel(self):
        asset_obj = self.env['account.asset.asset']
        for inv in self:
            for inv_line in inv.invoice_line:
                if inv_line.asset_category_id and inv_line.asset_ids:
                    for asset in inv_line.asset_ids:
                        if asset.state != 'draft':
                            raise except_orm(_('Error!'), _(
                                "You cannot cancel an invoice which doesn't have assets in draft state. You need to reset to draft the asset with name %s." % asset.name))
                    inv_line.asset_ids.unlink()
        return super(account_invoice, self).action_cancel()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
