# -*- encoding: utf-8 -*-
##############################################################################
#
#     Romanian accounting localization for OpenERP V7
#        @author -  Fekete Mihai, Tatár Attila <atta@nvm.ro>
#     Copyright (C) 2011-2013 TOTAL PC SYSTEMS (http://www.www.erpsystems.ro).
#     Copyright (C) 2013 Tatár Attila
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
from openerp.osv import fields, osv


class res_partner(osv.Model):
    _inherit = "res.partner"

    _columns = {
        'vat_on_payment': fields.boolean('VAT on payment treatment'),
    }
