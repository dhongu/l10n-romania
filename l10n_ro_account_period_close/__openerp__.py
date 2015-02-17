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
    'name': 'Romania - Account Period Close',
    'version': '1.0',
    'author': 'FOREST AND BIOMASS SERVICES ROMANIA',
    'website': 'http://www.forbiom.eu',
    'category': 'Romania Adaptation',
    'description': """
    Account Period Close - The module allows to close periodically accounts
    based on templates defines.
    Usefull for Income / Expense / VAT closing at the end of every month""",
    'depends': ['base', 'account'],
    'data': [
            'security/ir.model.access.csv',
        'security/account_security.xml',
        'account_period_close_view.xml',
        'wizard/account_period_closing.xml',
    ],
    'installable': True,
}
