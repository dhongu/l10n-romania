# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2016 FOREST AND BIOMASS SERVICES ROMANIA SA
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
    "name": "Contacts Detailed Address",
    "summary": "Introduces separate fields for street name and number, block, staircase and apartment number.",
    "version": "8.0.1.0.0",
    "author": "Forest and Biomass Services Romania,Odoo Community Association (OCA)",
    "website": "https://forbiom.eu",
    "category": 'Tools',
    "depends": [
        'base',
        'web_readonly_bypass',
        ],
    "data": [
        'views/res_partner.xml',
        ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3'
}
