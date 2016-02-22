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


class account_tax(osv.osv):
    _inherit = "account.tax"

    def _unit_compute(self, cr, uid, taxes, price_unit, product=None, partner=None, quantity=0):
        res = super(account_tax, self)._unit_compute(cr, uid, taxes, price_unit, product, partner, quantity)
        for line in res:
            tax = self.browse(cr, uid, line['id'])
            line['name'] = tax.description and tax.description + " - " + tax.name or tax.name
        return res
