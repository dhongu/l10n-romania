from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_suggested_invoice_edi_format(self):
        # EXTENDS 'account'
        res = super()._get_suggested_invoice_edi_format()
        if self.country_code == "RO":
            return "ciusro"
        else:
            return res
