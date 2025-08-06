from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _need_ubl_cii_xml(self, ubl_cii_format):
        res = super()._need_ubl_cii_xml(ubl_cii_format)
        if self.only_fiscal_receipt:
            return False
        return res
