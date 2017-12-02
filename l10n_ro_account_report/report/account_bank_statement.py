# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time

from datetime import datetime
from datetime import timedelta

from odoo.osv import osv
from odoo.report import report_sxw
from common_report_header import common_report_header

class bank_statement(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(bank_statement, self).__init__(cr, uid, name, context=context)
    
#    self.context=context
    

class report_bank_statement(osv.AbstractModel):
    _name = 'report.l10n_ro_account_report.report_account_bank_statement2'
    _inherit = 'report.abstract_report'
    _template = 'l10n_ro_account_report.report_account_bank_statement2'
    _wrapped_report_class = bank_statement

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
