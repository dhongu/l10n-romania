# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  dataERP - Vlad Nafureanu (vladnfr@gmail.com)
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
    'name': 'Discount Applied to Invoices',
    'version': '11.0.1.0.0',
    'author': 'dataERP, Vlad Nafureanu',
    'category': 'Account, Warehouse',
    'depends': [
        'account',
        'stock',
        'l10n_ro_config',
        'l10n_ro_stock_account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/discount.xml',
        'views/discount_line.xml',
        'views/account_invoice.xml'
    ],
    'installable': True
}
