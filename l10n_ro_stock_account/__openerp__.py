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
{
    "name": "Romania - Stock Accounting",
    "version": "1.0",
    "author": "FOREST AND BIOMASS SERVICES ROMANIA	",
    "website": "http://www.forbiom.eu",
    "category": "Hidden",
    "depends": ['stock_account', 'account', 'l10n_ro_config', 'l10n_ro_stock', 'purchase'],
    "description": """
Localization - Stock Accounting for Romania
-------------------------------------------

Main features include:
    - Stock accounting for receptions, deliveries, consume, usage_giving,
      inventory, production

    **~*~**
Modulul conține adaptarea mișcărilor contabile bazate pe mișcările de stoc.

    """,

    'data': [
             'stock_view.xml',
             'stock_account_view.xml',
             #'product_view.xml',
              ],
    'installable': True,
    'active': False,
}
