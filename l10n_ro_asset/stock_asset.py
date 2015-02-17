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


class account_asset_asset(models.Model):
    _name = 'account.asset.asset'
    _inherit = 'account.asset.asset'

    # Stock History for fixed assets
    stock_move_id = fields.Many2one('stock.move', string='Stock Entry')
    picking_id = fields.Many2one(
        'stock.picking', related='stock_move_id.picking_id', string='Stock Reception')
    prodlot_id = fields.Many2one(
        'stock.production.lot', string='Production Lot')
    inventory_number = fields.Char(string='Inventory Number', store=True, readonly=True, states={
                                   'draft': [('readonly', False)]}, copy=False)
    inventory_value = fields.Float(string='Inventory Value', related='stock_move_id.price_unit',
                                   store=True, readonly=True, states={'draft': [('readonly', False)]}, copy=False)

    @api.one
    @api.constrains('asset_type')
    def _check_method_number(self):
        if self.asset_type == 'fixed' and not self.stock_move_id:
            raise Warning(
                _('You cannot have a fixed asset without a link to the stock move line.'))
        if self.asset_type == 'service' and not self.inv_line_id:
            raise Warning(
                _('You cannot have a service asset without a link to the supplier invoice line.'))


from openerp.osv import osv, fields


class stock_move(osv.osv):
    _name = 'stock.move'
    _inherit = 'stock.move'

    _columns = {
        'location_dest_asset': fields.related('location_dest_id', 'asset_location', type='boolean', string='Destination Asset Location', readonly="1"),
        'location_asset': fields.related('location_id', 'asset_location', type='boolean', string='Source Asset Location', readonly="1"),
        'asset_category_id': fields.many2one('account.asset.category', "Asset Category", domain=[('asset_type', '=', 'fixed')]),
        'asset_id': fields.many2one('account.asset.asset', "Asset"),
        'asset_ids': fields.one2many('account.asset.asset', 'stock_move_id', "Assets", readonly="1"),
    }

    def onchange_picking_type_id(self, cr, uid, ids, picking_type_id=False, context=None):
        if not picking_type_id:
            return {}
        res = {}
        pick_type = self.pool.get('stock.picking.type').browse(
            cr, uid, picking_type_id, context=context)
        res['picking_type_code'] = str(pick_type.code)
        return {'value': res}

    def onchange_location_asset(self, cr, uid, ids, location_id=False, context=None):
        if not location_id:
            return {}
        res = {}
        location = self.pool.get('stock.location').browse(
            cr, uid, location_id, context=context)
        res['location_asset'] = location.asset_location
        return {'value': res}

    def onchange_location_dest_asset(self, cr, uid, ids, location_dest_id=False, context=None):
        if not location_dest_id:
            return {}
        res = {}
        location = self.pool.get('stock.location').browse(
            cr, uid, location_dest_id, context=context)
        res['location_dest_asset'] = location.asset_location
        return {'value': res}

    def onchange_asset_category_id(self, cr, uid, ids, asset_category_id=False, pick_type_id=False, context=None):
        if not asset_category_id:
            return {}
        res = {}
        if pick_type_id:
            pick_type = self.pool.get('stock.picking.type').browse(
                cr, uid, pick_type_id, context=context)
            dest_location_id = pick_type.warehouse_id and pick_type.warehouse_id.wh_asset_loc_id and pick_type.warehouse_id.wh_asset_loc_id.id or False
            res['location_dest_id'] = dest_location_id
        return {'value': res}

    def action_done(self, cr, uid, ids, context=None):
        super(stock_move, self).action_done(cr, uid, ids, context)
        context = context or {}
        asset_obj = self.pool.get('account.asset.asset')
        for move in self.browse(cr, uid, ids, context=context):
            if move.asset_category_id and not move.asset_ids:
                purchase_date = move.date
                partner_id = move.partner_id and move.partner_id.id or False
                purchase_value = move.price_unit
                category_id = move.asset_category_id
                if category_id.prorata:
                    purchase_date = move.date
                else:
                    purchase_date = datetime.strptime(
                        move.date[:10], "%Y-%m-%d") + relativedelta(day=1, months=+1)
                vals = {
                    'name': move.product_id.name,
                    'category_id': category_id.id,
                    'asset_type': category_id.asset_type,
                    'code': move.product_id.name or False,
                    'purchase_value': purchase_value,
                    'inventory_value': purchase_value,
                    'purchase_date': purchase_date,
                    'partner_id': partner_id,
                    'entry_date': move.date,
                    'product_id': move.product_id.id,
                    'stock_move_id': move.id,
                    'picking_id': move.picking_id and move.picking_id.id or False,
                    'state': 'draft',
                }

                if move.quant_ids:
                    for quant in move.quant_ids:
                        lot_id = quant.lot_id and quant.lot_id.id or False
                        vals['prodlot_id'] = lot_id
                        qty = quant.qty
                        while qty > 0:
                            qty -= 1
                            changed_vals = asset_obj.onchange_category_id(
                                cr, uid, [], vals['category_id'], context=context)
                            vals.update(changed_vals['value'])
                            asset_id = asset_obj.create(
                                cr, uid, vals, context=context)
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        """ Try to cancel the assets linked with this stock move if they are in draft state """
        context = context or {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.asset_category_id and move.asset_ids:
                for asset in move.asset_ids:
                    if asset.state != 'draft':
                        raise except_orm(_('Error!'), _(
                            "You cannot cancel a stock move which doesn't have assets in draft state. You need to reset to draft the asset with name %s." % asset.name))
                move.asset_ids.unlink()
        return super(stock_move, self).action_cancel(cr, uid, ids, context=context)

    def action_assign(self, cr, uid, ids, context=None):
        """ Checks the product type and accordingly writes the state.
        """
        context = context or {}
        quant_obj = self.pool.get("stock.quant")
        to_assign_moves = []
        main_domain = {}
        todo_moves = []
        operations = set()
        for move in self.browse(cr, uid, ids, context=context):
            if move.asset_id:
                if move.state not in ('confirmed', 'waiting', 'assigned'):
                    continue
                if move.location_id.usage in ('supplier', 'inventory', 'production'):
                    to_assign_moves.append(move.id)
                    # in case the move is returned, we want to try to find
                    # quants before forcing the assignment
                    if not move.origin_returned_move_id:
                        continue
                if move.product_id.type == 'consu':
                    to_assign_moves.append(move.id)
                    continue
                else:
                    todo_moves.append(move)

                    # we always keep the quants already assigned and try to
                    # find the remaining quantity on quants not assigned only
                    main_domain[move.id] = [
                        ('history_ids', 'in', move.asset_id.stock_move_id.id), ('reservation_id', '=', False), ('qty', '>', 0)]

                    # if the move is preceeded, restrict the choice of quants
                    # in the ones moved previously in original move
                    ancestors = self.find_move_ancestors(
                        cr, uid, move, context=context)
                    if move.state == 'waiting' and not ancestors:
                        # if the waiting move hasn't yet any ancestor (PO/MO
                        # not confirmed yet), don't find any quant available in
                        # stock
                        main_domain[move.id] += [('id', '=', False)]
                    elif ancestors:
                        main_domain[
                            move.id] += [('history_ids', 'in', ancestors)]

                    # if the move is returned from another, restrict the choice
                    # of quants to the ones that follow the returned move
                    if move.origin_returned_move_id:
                        main_domain[
                            move.id] += [('history_ids', 'in', move.origin_returned_move_id.id)]
                    for link in move.linked_move_operation_ids:
                        operations.add(link.operation_id)
                # Check all ops and sort them: we want to process first the
                # packages, then operations with lot then the rest
                operations = list(operations)
                operations.sort(key=lambda x: ((x.package_id and not x.product_id)
                                               and -4 or 0) + (x.package_id and -2 or 0) + (x.lot_id and -1 or 0))
                for ops in operations:
                    # first try to find quants based on specific domains given
                    # by linked operations
                    for record in ops.linked_move_operation_ids:
                        move = record.move_id
                        if move.id in main_domain:
                            domain = main_domain[move.id] + self.pool.get(
                                'stock.move.operation.link').get_specific_domain(cr, uid, record, context=context)
                            qty = record.qty
                            if qty:
                                quants = quant_obj.quants_get_prefered_domain(cr, uid, ops.location_id, move.product_id, qty, domain=domain, prefered_domain_list=[
                                ], restrict_lot_id=move.restrict_lot_id.id, restrict_partner_id=move.restrict_partner_id.id, context=context)
                                quant_obj.quants_reserve(
                                    cr, uid, quants, move, record, context=context)
                for move in todo_moves:
                    move.refresh()
                    # then if the move isn't totally assigned, try to find
                    # quants without any specific domain
                    if move.state != 'assigned':
                        qty_already_assigned = move.reserved_availability
                        qty = move.product_qty - qty_already_assigned
                        quants = quant_obj.quants_get_prefered_domain(cr, uid, move.location_id, move.product_id, qty, domain=main_domain[
                                                                      move.id], prefered_domain_list=[], restrict_lot_id=move.restrict_lot_id.id, restrict_partner_id=move.restrict_partner_id.id, context=context)
                        quant_obj.quants_reserve(
                            cr, uid, quants, move, context=context)

                # force assignation of consumable products and incoming from
                # supplier/inventory/production
                if to_assign_moves:
                    self.force_assign(
                        cr, uid, to_assign_moves, context=context)
            else:
                super(stock_move, self).action_assign(
                    cr, uid, ids, context=context)
