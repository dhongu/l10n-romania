# -*- coding: utf-8 -*-
# # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import time
from datetime import datetime
from odoo import api, models
from odoo.tools import formatLang


class ReportReportStatement(models.AbstractModel):
    _name = 'report.l10n_ro_account_report.report_statement'
    _template = 'l10n_ro_account_report.report_statement'

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(self._template)
        return  {
            'doc_ids': docids,
            'doc_model': report.model,
            'data': data,
            'time': time,
            'docs': self.env[report.model].browse(docids),
            'formatLang': self._formatLang
        }

    def _formatLang(self, value, *args):
        return formatLang(self.env, value, *args)

