import time
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.report import report_sxw
from common_report_header import common_report_header

from account.report import account_partner_balance



class report_partnerbalance(osv.AbstractModel):
    _name = 'report.l10n_ro_account_report.report_partnerbalance'
    _inherit = 'report.abstract_report'
    _template = 'l10n_ro_account_report.report_partnerbalance'
    _wrapped_report_class = partner_balance