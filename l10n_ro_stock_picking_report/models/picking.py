# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import _, api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _prepare_invoice_values(self):
        res = super()._prepare_invoice_values()
        res["delegate_id"] = self.delegate_id.id
        res["mean_transp"] = self.mean_transp
        return res

    def _get_report_base_filename(self):
        self.ensure_one()
        return f"{self.picking_type_id.name} {self.name}"

    delegate_id = fields.Many2one("res.partner", string="Delegate")
    mean_transp = fields.Char(string="Mean transport")

    l10n_ro_notice = fields.Boolean()  # camp definit in modulul de localizare

    @api.onchange("delegate_id")
    def on_change_delegate_id(self):
        if self.delegate_id:
            self.mean_transp = self.delegate_id.mean_transp

    # metoda locala sau se poate in 10 are alt nume
    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        res = super()._get_invoice_vals(key, inv_type, journal_id, move)
        if inv_type == "out_invoice":
            res["delegate_id"] = move.picking_id.delegate_id.id
            res["mean_transp"] = move.picking_id.mean_transp
        return res

    # """
    #
    # def action_invoice_create(self,   journal_id=False, group=False, type='out_invoice' ):
    #     invoices = []
    #
    #     if type == 'out_invoice':
    #         context = {}
    #         for picking in self :
    #             context = self._context.copy()
    #             context['default_delegate_id'] = picking.delegate_id.id
    #             context['default_mean_transp'] = picking.mean_transp
    #     picking = self.with_context(context)
    #     invoices = super(stock_picking, picking ).action_invoice_create(journal_id, group, type)
    #
    #     return invoices
    # """

    def do_print_picking(self):
        self.write({"printed": True})
        report = False
        if self.picking_type_code == "incoming":
            if self.location_dest_id.l10n_ro_merchandise_type == "store":
                report = "l10n_ro_stock_picking_report.action_report_reception_sale_price"

            else:
                report = "l10n_ro_stock_picking_report.action_report_reception"

        elif self.picking_type_code == "outgoing":
            report = "l10n_ro_stock_picking_report.action_report_delivery"

        else:
            report = "l10n_ro_stock_picking_report.action_report_internal_transfer"

        if report:
            res = self.env.ref(report).sudo().report_action(self)
        return res

    def _attach_sign(self):
        """Render the delivery report in pdf and attach it to the picking in `self`."""
        self.ensure_one()
        report = self.env["ir.actions.report"]._render_qweb_pdf("l10n_ro_stock_picking_report.report_delivery", self.id)
        filename = f"{self.name}_signed_delivery_slip"
        if self.partner_id:
            message = _("Order signed by %s", self.partner_id.name)
        else:
            message = _("Order signed")
        self.message_post(
            attachments=[(f"{filename}.pdf", report[0])],
            body=message,
        )
        return True



from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import format_date, formatLang, frozendict


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _create_invoices(self, sale_orders):
        res = super(SaleAdvancePaymentInv, self)._create_invoices(sale_orders)
        for order in sale_orders:
            pickings = order.picking_ids.filtered(lambda p: p.state == 'done')
            if not pickings:
                pickings = order.picking_ids.filtered(lambda p: p.state not in ['cancel'])
            if pickings:
                picking = pickings[0]
                invoices = res.filtered(lambda i: i.invoice_origin == order.name)
                if not invoices:
                    invoices = res
                invoices.write({
                    'delegate_id': picking.delegate_id.id,
                    'mean_transp': picking.mean_transp,
                })
        return res
