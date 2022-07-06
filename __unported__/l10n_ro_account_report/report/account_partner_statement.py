

from odoo import models, fields, api, _


from  odoo.addons.account.report.account_partner_balance import account_aged_partner_balance



class report_partnerstatement(models.AbstractModel):
    _name = 'report.l10n_ro_account_report.report_partnerstatement'
    _inherit = 'report.abstract_report'
    _template = 'l10n_ro_account_report.report_partnerstatement'
    _wrapped_report_class =  account_aged_partner_balance