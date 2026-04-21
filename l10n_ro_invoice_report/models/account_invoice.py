# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    delegate_id = fields.Many2one(
        "res.partner",
        string="Delegate",
        domain=[("is_company", "=", False)],
    )

    mean_transp = fields.Char(
        string="Mean transport",
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if "delegate_id" not in defaults:
            if "default_delegate_id" in self.env.context:
                defaults["default_delegate_id"] = defaults["default_delegate_id"]
        return defaults

    @api.onchange("delegate_id")
    def on_change_delegate_id(self):
        if self.delegate_id:
            self.mean_transp = self.delegate_id.mean_transp

    # anularea facturilor cu zero

    def action_invoice_cancel(self):
        for invoice in self:
            if invoice.amount_total == 0.0 and invoice.state == "paid":
                invoice.state = "open"
                # invoice.write({'state':'open'})

        return super().action_invoice_cancel()

    def set_origin_with_picking(self):
        for invoice in self:
            pickings = self.env["stock.picking"]
            for line in invoice.invoice_line_ids:
                for sale_line in line.sale_line_ids:
                    for move in sale_line.move_ids:
                        if move.picking_id.state == "done":
                            pickings |= move.picking_id
                if line.purchase_line_id:
                    for move in line.purchase_line_id.move_ids:
                        if move.picking_id.state == "done":
                            pickings |= move.picking_id
            origin = ""
            for picking in pickings:
                origin += " " + picking.name

            if origin:
                invoice.write({"invoice_origin": origin})

    def _compute_payments_widget_reconciled_info(self):
        res = super()._compute_payments_widget_reconciled_info()
        for invoice in self:
            if invoice.invoice_payments_widget:
                for item in invoice.invoice_payments_widget["content"]:
                    move_id = item["move_id"]
                    move = self.env["account.move"].browse(move_id)
                    item["journal_type"] = move.journal_id.type
                    # get payment for POS
                    if (
                        move.journal_id.type == "sale"
                        and "pos_payment_name" in item
                        and invoice.move_type == "out_refund"
                    ):
                        pos_payment_method = (
                            self.env["pos.payment.method"]
                            .sudo()
                            .search([("name", "=", item["pos_payment_name"])], limit=1)
                        )
                        if pos_payment_method:
                            item["journal_type"] = pos_payment_method.journal_id.type
                        item["payment_type"] = "outbound"
                    payment_id = item["account_payment_id"]
                    if payment_id:
                        payment = self.env["account.payment"].browse(payment_id)
                        item["payment_type"] = payment.payment_type
        return res

    @api.depends("bank_partner_id", "commercial_partner_id.payment_bank_id")
    def _compute_partner_bank_id(self):
        res = super()._compute_partner_bank_id()
        for move in self:
            # Check for any payment bank set in partner
            if move.move_type in ["out_invoice", "in_refund"] and move.commercial_partner_id.payment_bank_id:
                move.partner_bank_id = move.commercial_partner_id.payment_bank_id
        return res

    def is_bf_printed(self):
        """Check if the invoice has been printed with BF (Bon Fiscal)"""
        self.ensure_one()
        if hasattr(self, "receipt_print"):
            return self.receipt_print
        return False

    def _get_invoice_pdf_proforma(self):
        self.ensure_one()
        filename = self._get_invoice_proforma_pdf_report_filename()
        content, report_type = self.env['ir.actions.report']._pre_render_qweb_pdf(
            'account.account_invoices', self.ids, data={'proforma': False}
        )
        content_by_id = self.env['ir.actions.report']._get_splitted_report(
            'account.account_invoices', content, report_type
        )
        return {
            'filename': filename,
            'filetype': 'pdf',
            'content': content_by_id[self.id],
        }


#
class account_invoice_line(models.Model):
    _inherit = "account.move.line"

    # def write(self, vals):
    #     if vals.get("name", False):
    #         lines = vals["name"].split("\n")
    #         if len(lines) > 1:
    #             # pe prima line e numele produsului
    #             vals["name"] = "\n".join(lines[1:])
    #     return super().write(vals)


#
#     sequence = fields.Integer(default=1)
#
#     price_unit_without_taxes = fields.Float(string='Unit Price without taxes', store=True, readonly=True,
#                                             compute='_compute_price')
#
#     price_taxes = fields.Float(string='Taxes', digits='Account', store=True, readonly=True,
#                                compute='_compute_price')
#
#     price_normal_taxes = fields.Float(tring='Normal Taxes', digits='Account', store=True,
#                                       readonly=True, compute='_compute_price')
#
#     """
#     # campurile standard
#     price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'))
#     price_subtotal = fields.Monetary(string='Amount',
#         store=True, readonly=True, compute='_compute_price', help="Total amount without taxes")
#     price_total = fields.Monetary(string='Amount',
#         store=True, readonly=True, compute='_compute_price', help="Total amount with taxes")
#     price_subtotal_signed = fields.Monetary(string='Amount Signed', currency_field='company_currency_id',
#         store=True, readonly=True, compute='_compute_price',
#         help="Total amount in the currency of the company, negative for credit note.")
#     """
#
#     @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
#                  'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
#                  'invoice_id.invoice_date', 'invoice_id.date')
#     def _compute_price(self):
#
#         super(account_invoice_line, self)._compute_price()
#         # if self.price_subtotal:
#         #      self.price_unit_without_taxes = self.price_subtotal / self.quantity
#         #      self.price_taxes = (self.price_total - self.price_subtotal ) / self.quantity
#
#         # Versiunea mai complexa
#         price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
#
#         currency = self.invoice_id and self.invoice_id.currency_id or None
#
#         taxes = False
#         if self.invoice_line_tax_ids:
#             taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
#                                                           partner=self.invoice_id.partner_id)
#
#         # de ce se seteaza cele doua valori ? nu au fost setate in
#         if taxes:
#             self.price_subtotal = taxes['total_excluded'] if taxes else self.quantity * price
#             self.price_taxes = taxes['total_included'] - self.price_subtotal
#
#         taxes_unit = self.invoice_line_tax_ids.compute_all(price, currency=currency,
#                                                            quantity=1, product=self.product_id,
#                                                            partner=self.invoice_id.partner_id)
#
#         self.price_unit_without_taxes = taxes_unit['total_excluded']
#         # Compute normal taxes in case of Customer Invoices to have the value
#         # in Inverse Taxation
#         if self.invoice_id.type in ['out_invoice', 'out_refund']:
#             taxes_ids = self.product_id.taxes_id.filtered(lambda r: r.company_id == self.invoice_id.company_id)
#             normal_taxes = taxes_ids.compute_all(price, currency=currency,
#                                                  quantity=self.quantity, product=self.product_id,
#                                                  partner=self.invoice_id.partner_id)
#             self.price_normal_taxes = normal_taxes['total_included'] - normal_taxes['total_excluded']
#         # aplicare rotunjiri . asta nu trebuie facuta in functie de config
#         if self.invoice_id:
#             self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)
#             self.price_taxes = self.invoice_id.currency_id.round(self.price_taxes)
#             self.price_unit_without_taxes = self.invoice_id.currency_id.round(self.price_unit_without_taxes)
#             self.price_normal_taxes = self.invoice_id.currency_id.round(self.price_normal_taxes)
