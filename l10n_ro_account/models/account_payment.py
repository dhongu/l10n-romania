# ©  2020 Terrabit
# See README.rst file on addons root folder for license details

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AccountAbstractPayment(models.AbstractModel):
    _inherit = "account.abstract.payment"

    @api.one
    @api.constrains("amount")
    def _check_amount(self):
        super(AccountAbstractPayment, self)._check_amount()
        # todo: de adaugat in configurare suma limita
        if self.payment_type == "inbound" and self.partner_type == "customer" and self.journal_id.type == "cash":
            if self.partner_id.is_company:
                if self.amount >= 5000:
                    raise ValidationError(_("The payment amount cannot be greater than 5000"))
            else:
                if self.amount >= 10000:
                    raise ValidationError(_("The payment amount cannot be greater than 10000"))
