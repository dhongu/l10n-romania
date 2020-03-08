# -*- coding: utf-8 -*-
# # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import time
from datetime import datetime
from odoo import api, models
from odoo.tools import formatLang


class ReportReportStatement(models.AbstractModel):
    _name = 'report.l10n_ro_account_report.report_sale_purchase_journal'
    _template = 'l10n_ro_account_report.report_sale_purchase_journal'
    _description = 'report_sale_purchase_journal'

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(self._template)
        if not docids and data and 'active_ids' in self.env.context:
            docids = self.env.context['active_ids']
        return  {
            'doc_ids': docids,
            'doc_model': report.model,
            'time': time,
            'wizard': self.env['account.report.sale.purchase.journal'].browse(data['wizard_id']),
            'docs': self.env[report.model].browse(docids),

        }



