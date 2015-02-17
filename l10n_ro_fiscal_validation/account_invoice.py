# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2014 FOREST AND BIOMASS SERVICES ROMANIA SA
#    (http://www.forbiom.eu).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class account_invoice(models.Model):
    _name = "account.invoice"
    _inherit = "account.invoice"

    @api.multi
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
                            payment_term=False, partner_bank_id=False, company_id=False):
        result = super(account_invoice, self).onchange_partner_id(
            type, partner_id, date_invoice, payment_term, partner_bank_id, company_id)
        vat_on_payment = False
        if 'out' in type:
            vat_on_payment = self.user_id.company_id.vat_on_payment
        else:
            partner = self.env['res.partner'].browse(partner_id)
            ctx = dict(self._context)
            if date_invoice:
                ctx.update({'check_date': date_invoice})
            vat_on_payment = partner.with_context(ctx)._check_vat_on_payment()
        result['value']['vat_on_payment'] = vat_on_payment
        return result
