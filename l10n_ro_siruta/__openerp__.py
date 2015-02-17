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
    "name": "Romania - Siruta",
    "version": "1.0",
    "author": "FOREST AND BIOMASS SERVICES ROMANIA SA",
    "category": "Generic Modules/Base",
    "description": """Creates models for storing zones, communes.
Links between country - zone - state - commune - cities.
Partner address fields extended with zone and commune.
City field from partners is related to city_id.name.
Fields are added in partner and partner contact forms.""",
    "depends": ["base", "l10n_ro"],
    "data": ['partner_view.xml',
              'siruta_view.xml',
              'security/ir.model.access.csv',
              'data/res.country.zone.csv',
              'data/res_country_state.xml',
              'data/res.country.commune.csv',
              'data/res.country.city.csv',
             ],
    "installable": True
}
