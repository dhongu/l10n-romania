from odoo import models, fields, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    purchase_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Add Purchase Order',
        readonly=True, states={'draft': [('readonly', False)]},
        help='Encoding help. When selected, the associated purchase order lines are added to the voucher. Several PO can be selected.')

    @api.depends('company_id', 'pay_now', 'account_id')
    def _compute_payment_journal_id(self):
        for voucher in self:
            if voucher.pay_now != 'pay_now':
                continue
            domain = [
                ('type', '=', 'cash'), # search only for cash journals
                ('company_id', '=', voucher.company_id.id)]
            if voucher.account_id:
                field = 'default_debit_account_id' if voucher.voucher_type == 'sale' else 'default_credit_account_id'
                domain.append((field, '=', voucher.account_id.id))
            voucher.payment_journal_id = self.env['account.journal'].search(domain, limit=1)

    @api.onchange('state', 'partner_id', 'line_ids')
    def _onchange_allowed_purchase_ids_domain(self):
        result = {}
        purchase_line_ids = self.line_ids.mapped('purchase_line_id')
        purchase_ids = self.line_ids.mapped('purchase_id').filtered(lambda r: r.order_line <= purchase_line_ids)

        domain = [('invoice_status', '=', 'to invoice')]
        if self.partner_id:
            domain += [('partner_id', 'child_of', self.partner_id.id)]
        if purchase_ids:
            domain += [('id', 'not in', purchase_ids.ids)]
        result['domain'] = {'purchase_id': domain}
        return result

    def _prepare_voucher_line_from_po_line(self, line):
        AccountInvoiceLine = self.env['account.invoice.line']
        if line.product_id.purchase_method == 'purchase':
            qty = line.product_qty - line.qty_invoiced
        else:
            qty = line.qty_received - line.qty_invoiced
        taxes = line.taxes_id
        invoice_line_tax_ids = line.order_id.fiscal_position_id.map_tax(taxes)
        data = {
            'purchase_line_id': line.id,
            'name': line.order_id.name+': '+line.name,
            'origin': line.order_id.origin,
            'uom_id': line.product_uom.id,
            'product_id': line.product_id.id,
            'account_id': AccountInvoiceLine.with_context({'journal_id': self.journal_id.id, 'type': 'in_invoice'})._default_account(),
            'price_unit': line.order_id.currency_id.with_context(date=self.date).compute(line.price_unit, self.currency_id, round=False),
            'quantity': qty,
            'account_analytic_id': line.account_analytic_id.id,
            'tax_ids': invoice_line_tax_ids.ids
        }
        account = AccountInvoiceLine.get_invoice_line_account('in_invoice', line.product_id, line.order_id.fiscal_position_id, self.env.user.company_id)
        if account:
            data['account_id'] = account.id
        return data

    # Load all unsold PO lines
    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.purchase_id.partner_id.id

        vendor_ref = self.purchase_id.partner_ref
        if vendor_ref and (not self.name or (
                vendor_ref + ", " not in self.name and not self.name.endswith(vendor_ref))):
            self.name = ", ".join([self.name, vendor_ref]) if self.name else vendor_ref

        new_lines = self.env['account.voucher.line']
        for line in self.purchase_id.order_line - self.line_ids.mapped('purchase_line_id'):
            data = self._prepare_voucher_line_from_po_line(line)
            new_lines += new_lines.new(data)

        self.line_ids += new_lines
        self.purchase_id = False
        return {}

    @api.multi
    def proforma_voucher(self):
        res = super(AccountVoucher, self).proforma_voucher()
        for voucher in self:
            for line in voucher.line_ids:
                line.modify_stock_move_value(line.price_subtotal)
        return res
