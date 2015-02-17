# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2014 FOREST AND BIOMASS SERVICES ROMANIA SA
#    (http://www.forbiom.eu).
#    Modified account.voucher module
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
    'name': 'Partner Compensation',
    'version': '1.0',
    'author': 'FOREST AND BIOMASS SERVICES ROMANIA SA',
    'summary': 'Compensate partners credits and debits',
    'description': """Accounting Compensation
This module manages:

* Compensation Entry
    """,
    'category': 'Accounting & Finance',
    'sequence': 4,
    'depends': ['account'],
    'demo': [],
    'data': [
        'account_compensation_workflow.xml',
        'account_compensation_view.xml',
        'security/ir.model.access.csv',
        'security/account_voucher_security.xml',
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
