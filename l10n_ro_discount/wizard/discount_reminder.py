from odoo import models, fields, api, _


class DiscountInvoice(models.TransientModel):
    _name = 'discount.reminder'
    _description = "Discount Reminder"

    invoice_ids = fields.Many2many(
        comodel_name='account.invoice',
        string='Invoice',
        required=True,
        readonly=True)

    @api.model
    def default_get(self, fields):
        defaults = super(DiscountInvoice, self).default_get(fields)

        active_ids = self.env.context.get('active_ids', False)

        defaults['invoice_ids'] = [(6, 0, active_ids)]

        return defaults

    def confirm_discount(self):
        return True