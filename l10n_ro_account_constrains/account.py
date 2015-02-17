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

from openerp.osv import fields, osv
from openerp.tools.translate import _


class account_move_line(osv.osv):
    _inherit = "account.move.line"

    def _check_currency(self, cr, uid, ids, context=None):
        return True

    _constraints = [
        (_check_currency, """The selected account of your Journal Entry forces
        to provide a secondary currency. You should remove the secondary
        currency on the account or select a multi-currency view on the
        journal.""",
         ['currency_id']),
    ]


class account_journal(osv.osv):
    _inherit = "account.journal"

    def _check_currency(self, cr, uid, ids, context=None):
        return True

    _constraints = [
        (_check_currency, """Removed Configuration error!\n
        The currency chosen should be shared by the default accounts too.""", [
         'currency', 'default_debit_account_id', 'default_credit_account_id']),
    ]
