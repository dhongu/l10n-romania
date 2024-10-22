

from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = "account.payment"


    # Adaugare camp pentru a indica tipul de document:
    # chitanta furnizor, chitanta client, dispozitie de plata, dispozitie de incasare

    l10n_ro_payment_type = fields.Selection()


