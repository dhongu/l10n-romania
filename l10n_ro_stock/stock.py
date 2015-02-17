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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, api


class stock_warehouse(osv.Model):
    _name = "stock.warehouse"
    _inherit = "stock.warehouse"

    _columns = {
        'wh_consume_loc_id': fields.many2one('stock.location', 'Consume Location'),
        'wh_usage_loc_id': fields.many2one('stock.location', 'Usage Giving Location'),
        'consume_type_id': fields.many2one('stock.picking.type', 'Consume Type'),
        'usage_type_id': fields.many2one('stock.picking.type', 'Usage Giving Type'),
    }

    # Change warehouse methods for create to add the consume and usage giving
    # operations.
    def create_sequences_and_picking_types(self, cr, uid, warehouse, context=None):
        seq_obj = self.pool.get('ir.sequence')
        picking_type_obj = self.pool.get('stock.picking.type')
        # create new sequences
        cons_seq_id = seq_obj.create(cr, SUPERUSER_ID, values={'name': warehouse.name + _(
            ' Sequence consume'), 'prefix': warehouse.code + '/CONS/', 'padding': 5}, context=context)
        usage_seq_id = seq_obj.create(cr, SUPERUSER_ID, values={'name': warehouse.name + _(
            ' Sequence usage'), 'prefix': warehouse.code + '/USAGE/', 'padding': 5}, context=context)

        wh_stock_loc = warehouse.lot_stock_id
        cons_stock_loc = warehouse.wh_consume_loc_id
        usage_stock_loc = warehouse.wh_usage_loc_id

        # order the picking types with a sequence allowing to have the
        # following suit for each warehouse: reception, internal, pick, pack,
        # ship.
        max_sequence = self.pool.get('stock.picking.type').search_read(
            cr, uid, [], ['sequence'], order='sequence desc')
        max_sequence = max_sequence and max_sequence[0]['sequence'] or 0

        # choose the next available color for the picking types of this
        # warehouse
        color = 0
        # put flashy colors first
        available_colors = [c % 9 for c in range(3, 12)]
        all_used_colors = self.pool.get('stock.picking.type').search_read(cr, uid, [(
            'warehouse_id', '!=', False), ('color', '!=', False)], ['color'], order='color')
        # don't use sets to preserve the list order
        for x in all_used_colors:
            if x['color'] in available_colors:
                available_colors.remove(x['color'])
        if available_colors:
            color = available_colors[0]

        consume_type_id = picking_type_obj.create(cr, uid, vals={
            'name': _('Consume'),
            'warehouse_id': warehouse.id,
            'code': 'internal',
            'sequence_id': cons_seq_id,
            'default_location_src_id': wh_stock_loc.id,
            'default_location_dest_id': cons_stock_loc.id,
            'sequence': max_sequence + 1,
            'color': color}, context=context)
        usage_type_id = picking_type_obj.create(cr, uid, vals={
            'name': _('Usage'),
            'warehouse_id': warehouse.id,
            'code': 'internal',
            'sequence_id': usage_seq_id,
            'default_location_src_id': wh_stock_loc.id,
            'default_location_dest_id': usage_stock_loc.id,
            'sequence': max_sequence + 4,
            'color': color}, context=context)
        vals = {
            'consume_type_id': consume_type_id,
            'usage_type_id': usage_type_id,
        }
        super(stock_warehouse, self).write(
            cr, uid, warehouse.id, vals=vals, context=context)
        return super(stock_warehouse, self).create_sequences_and_picking_types(cr, uid, warehouse, context=context)

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals is None:
            vals = {}
        location_obj = self.pool.get('stock.location')
        # create all location
        cons_location_id = location_obj.create(cr, uid, {
            'name': 'Consume',
            'usage': 'consume',
            'active': True,
        }, context=context)
        vals['wh_consume_loc_id'] = cons_location_id
        usage_location_id = location_obj.create(cr, uid, {
            'name': 'Usage Giving',
            'usage': 'usage_giving',
            'active': True,
        }, context=context)
        vals['wh_usage_loc_id'] = usage_location_id
        new_id = super(stock_warehouse, self).create(
            cr, uid, vals=vals, context=context)
        warehouse = self.browse(cr, uid, new_id, context=context)
        location_obj.write(cr, uid, cons_location_id, {
                           'location_id': warehouse.view_location_id.id}, context=context)
        location_obj.write(cr, uid, usage_location_id, {
                           'location_id': warehouse.view_location_id.id}, context=context)
        return new_id


class stock_move(osv.Model):
    _name = "stock.move"
    _inherit = "stock.move"

    _columns = {
        'picking_type_code': fields.related('picking_type_id', 'code', type='char', string='Picking Type Code'),
    }
