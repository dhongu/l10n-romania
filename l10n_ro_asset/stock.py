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

from openerp.osv import osv, fields


class stock_warehouse(osv.osv):
    _name = "stock.warehouse"
    _inherit = "stock.warehouse"

    _columns = {
        'wh_asset_loc_id': fields.many2one('stock.location', 'Asset Location', domain=[('usage', '=', 'internal')]),
    }


class stock_location(osv.osv):
    _name = "stock.location"
    _inherit = "stock.location"

    _columns = {
        'asset_location': fields.boolean('Is a Assets Location?', help='Check this box to allow using this location to put assets goods.'),
    }
