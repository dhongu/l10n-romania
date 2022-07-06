# -*- coding: utf-8 -*-


from odoo import models, fields, api, _



class account_common_report(models.TransientModel):
    _inherit = "account.common.report"

    show_filter = fields.Boolean(string='Show Filter')