from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_create_voucher(self):
        action = self.env.ref('account_voucher.action_purchase_receipt')
        result = action.read()[0]

        result['context'] = {'default_purchase_id': self.id,
                             'default_date_invoice': self.date_planned[:10],
                             'default_voucher_type': 'purchase'}

        default_journal_id = self.env['account.journal'].search([
            ('type', '=', 'purchase'),
            ('company_id', '=', self.company_id.id)], limit=1)
        if default_journal_id:
            result['context']['default_journal_id'] = default_journal_id.id

        default_payment_journal_id = self.env['account.journal'].search([
            ('type', '=', 'cash'),
            ('company_id', '=', self.company_id.id)], limit=1)
        if default_payment_journal_id:
            result['context']['default_payment_journal_id'] = default_payment_journal_id.id

        result['views'] = [[False, "form"]]
        return result
