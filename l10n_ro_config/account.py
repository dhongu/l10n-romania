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

from openerp import models, fields, api, _


class account_account(models.Model):
    _name = "account.account"
    _inherit = "account.account"

    uneligible_account_id = fields.Many2one('account.account', 'Unneligible Account (VAT on payment)',
                                            help='Related account used for real registrations on a VAT on payment basis. Set the shadow account here')


class account_tax_code(models.Model):
    _name = "account.tax.code"
    _inherit = "account.tax.code"

    uneligible_tax_code_id = fields.Many2one('account.tax.code', 'Uneligible Tax Code (VAT on payment)',
                                             help='Related tax code used for real registrations on a VAT on payment basis. Set the shadow tax code here')
