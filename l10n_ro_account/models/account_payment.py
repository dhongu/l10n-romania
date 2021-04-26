# ©  2020 Terrabit
# See README.rst file on addons root folder for license details

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.constrains("amount")
    def _check_amount(self):
        # in 14.0 este facut _sql_constraints  check_amount_not_negative
        # super(AccountPayment, self)._check_amount()
        # todo: de adaugat in configurare suma limita
        for payment in self:
            if (
                payment.payment_type == "inbound"
                and payment.partner_type == "customer"
                and payment.journal_id.type == "cash"
            ):
                if payment.partner_id.is_company:
                    if payment.amount >= 5000:
                        raise ValidationError(_("The payment amount cannot be greater than 5000"))
                else:
                    if payment.amount >= 10000:
                        raise ValidationError(_("The payment amount cannot be greater than 10000"))
