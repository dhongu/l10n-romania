# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2012 Domsense s.r.l. (<http://www.domsense.com>).
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp


class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _default_vat_on_payment(self):
        inv_type = self._context.get('type', 'out_invoice')
        if 'out' in inv_type:
            return self.user_id.company_id.vat_on_payment
        else:
            return self.partner_id.vat_on_payment

    vat_on_payment = fields.Boolean(
        string='Vat on payment', default=_default_vat_on_payment)
    fiscal_receipt = fields.Boolean(
        string='Is a Fiscal Receipt', default=False)

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        """
        Use shadow accounts for journal entry to be generated, according to account and tax code related records
        """
        move_lines = super(
            account_invoice, self).finalize_invoice_move_lines(move_lines)
        acc_pool = self.env['account.account']
        tax_code_pool = self.env['account.tax.code']
        new_move_lines = []
        for line_tup in move_lines:
            if self.vat_on_payment and not line_tup[2].get('not_deductible', False):
                if line_tup[2].get('account_id', False):
                    account = acc_pool.browse(line_tup[2]['account_id'])
                    if account.type != 'receivable' and account.type != 'payable':
                        # if not account.vat_on_payment_related_account_id:
                        #    raise osv.except_osv(_('Error'), _('The invoice is \'VAT on payment\' but account %s does not have a related shadow account') % account.name)
                        line_tup[2]['real_account_id'] = account.id
                        line_tup[2][
                            'account_id'] = account.uneligible_account_id and account.uneligible_account_id.id or account.id
                if line_tup[2].get('tax_code_id', False):
                    tax_code = tax_code_pool.browse(line_tup[2]['tax_code_id'])
                    # if not tax_code.vat_on_payment_related_tax_code_id:
                    #    raise osv.except_osv(_('Error'), _('The invoice is \'VAT on payment\' but tax code %s does not have a related shadow tax code') % tax_code.name)
                    line_tup[2]['real_tax_code_id'] = line_tup[
                        2]['tax_code_id']
                    line_tup[2][
                        'tax_code_id'] = tax_code.uneligible_tax_code_id and tax_code.uneligible_tax_code_id.id or tax_code.id
            new_move_lines.append(line_tup)
        return new_move_lines

    @api.multi
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
                            payment_term=False, partner_bank_id=False, company_id=False):
        result = super(account_invoice, self).onchange_partner_id(
            type, partner_id, date_invoice, payment_term, partner_bank_id, company_id)
        vat_on_payment = False
        if 'out' in type:
            vat_on_payment = self.user_id.company_id.vat_on_payment
        else:
            if partner_id:
                p = self.env['res.partner'].browse(partner_id)
                if p.property_account_position:
                    if 'National' in p.property_account_position.name:
                        vat_on_payment = p.vat_on_payment
                else:
                    vat_on_payment = p.vat_on_payment
        result['value']['vat_on_payment'] = vat_on_payment
        return result

    @api.multi
    def onchange_fiscal_receipt(self, fiscal_receipt=False, vat_on_payment=False):
        result = {'value': {}}
        if fiscal_receipt:
            vat_on_payment = False
        result['value']['vat_on_payment'] = vat_on_payment
        return result
