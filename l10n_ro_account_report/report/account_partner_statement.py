import time
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.report import report_sxw
from common_report_header import common_report_header

from   openerp.addons.account.report.account_partner_balance import partner_balance



class report_partnerstatement(osv.AbstractModel):
    _name = 'report.l10n_ro_account_report.report_partnerstatement'
    _inherit = 'report.abstract_report'
    _template = 'l10n_ro_account_report.report_partnerstatement'
    _wrapped_report_class =  partner_balance