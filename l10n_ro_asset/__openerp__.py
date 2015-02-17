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
    'name': 'Romania - Assets Management',
    'version': '1.0',
    'depends': ['account', 'account_asset', 'stock', 'l10n_ro_config', 'l10n_ro_stock'],
    'author': 'FOREST AND BIOMASS SERVICES ROMANIA',
    'description': """
Financial and accounting asset management.
==========================================

This Module manages the assets owned by a company or an individual. It will keep
track of depreciation's occurred on those assets. And it allows to create Move's
of the depreciation lines.

    """,
    'website': 'http://www.forbiom.eu',
    'category': 'Romania Adaptation',
    'sequence': 32,
    'data': [
        'security/ir.model.access.csv',
        'account_asset_view.xml',
        'stock_assets_view.xml',
        'stock_view.xml',
        #    'report/account_asset_report_view.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
