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


class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'd394_id': fields.many2one('report.394.code', string='D394 codes'),
    }


class report_394_code(osv.osv):
    _name = "report.394.code"
    _description = "D394 code"
    _columns = {
        'name': fields.char('D394 Code', size=16),
        'description': fields.char('Description', size=64),
        'product_ids': fields.one2many('product.product', 'd394_id', string='Products'),
    }
