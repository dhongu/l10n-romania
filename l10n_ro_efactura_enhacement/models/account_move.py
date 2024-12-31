from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _need_ubl_cii_xml(self):
        res = super()._need_ubl_cii_xml()

        return res
