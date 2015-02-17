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
    "name": "Romania - Human Resources",
    "version": "1.0",
    "author": "FOREST AND BIOMASS SERVICES ROMANIA	",
    "website": "http://www.forbiom.eu",
    "category": "Romania Adaptation",
    "depends": ['hr', 'hr_contract', 'l10n_ro_config'],
    "description": """
Romania  - Human Resources
------------------------------------------


    """,

    "data": [
        "data/caen.xml",
            "data/hr_job.xml",
            "data/insurance_type.xml",
            "hr_employee_view.xml",
            "hr_contract_view.xml",
            "res_company_view.xml",
            "security/ir.model.access.csv",
    ],
    "installable": True
}
