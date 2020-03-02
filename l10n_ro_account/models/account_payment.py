# -*- coding: utf-8 -*-
# ©  2020 Terrabit
# See README.rst file on addons root folder for license details

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError




class account_abstract_payment(models.AbstractModel):
    _inherit = "account.abstract.payment"


    @api.one
    @api.constrains('amount')
    def _check_amount(self):
        super(account_abstract_payment, self)._check_amount()
        #todo: de adaugat in configurare suma limita
        if self.amount > 5000 and self.journal_id.type == 'cash':
            raise ValidationError(_('The payment amount cannot be greater than 5000'))
