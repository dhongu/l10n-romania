# -*- coding: utf-8 -*-
# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import time
from odoo.report import report_sxw
from odoo.osv import osv
# from odoo.addons.l10n_ro_invoice_report.report.amount_to_text_ro  import *

from odoo.addons.l10n_ro_invoice_report.report.account_invoice import report_invoice_print

"""
class report_invoice_print(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_invoice_print, self).__init__( cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'convert': self._convert,
            'with_discount':self._with_discount,
        })
        
    def _convert(self, amount):
        amt_ro = amount_to_text_ro(amount)
        return amt_ro

    def _with_discount(self,invoice):
        res = False
        for line in invoice.invoice_line:
            if line.discount <> 0.0:
                res = True
        return  res
"""


class report_invoice_intrastat(osv.AbstractModel):
    _name = 'report.report_intrastat.report_intrastatinvoice'
    _inherit = 'report.abstract_report'
    _template = 'report_intrastat.report_intrastatinvoice'
    _wrapped_report_class = report_invoice_print


