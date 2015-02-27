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

from openerp import models, fields, api


class res_partner(models.Model):
    _inherit = "res.partner"
    
    sql_constraints = [
        ('vat_nrc_uniq', 'unique (id)', 'The vat and nrc of the partner must be unique !'),
    ]
    
    def _auto_init(self, cr, context=None):
        result = super(res_partner, self)._auto_init(cr, context=context)
        # Real implementation of the vat/nrc constraints: only "commercial entities" 
        # need to have unique numbers, and the condition for being a commercial entity
        # is "is_company or parent_id IS NULL".
        # Contacts inside a company automatically have a copy of the company's commercial fields
        # (see _commercial_fields()), so they are automatically consistent.
        cr.execute("""
            DROP INDEX IF EXISTS res_partner_vat_nrc_uniq_for_companies;
            DROP INDEX IF EXISTS res_partner_vat_uniq_for_companies;
            DROP INDEX IF EXISTS res_partner_nrc_uniq_for_companies;
            CREATE UNIQUE INDEX res_partner_vat_nrc_uniq_for_companies ON res_partner
                (company_id, vat, nrc) WHERE is_company OR parent_id IS NULL;
        """)
        return result
