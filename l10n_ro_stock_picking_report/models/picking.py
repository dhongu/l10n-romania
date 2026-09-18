# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _get_report_base_filename(self):
        self.ensure_one()
        return f"{self.picking_type_id.name} {self.name}"

    # index=True: vezi nota din deltatech_cmr_document — același câmp e definit în ambele
    # module, deci atributul trebuie pus în amândouă (ultimul modul încărcat dictează).
    delegate_id = fields.Many2one("res.partner", string="Delegate", index=True)
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
    #             context = self.env.context.copy()
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
            if self.location_dest_id.is_store:
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
            message = self.env._("Order signed by %s", self.partner_id.name)
        else:
            message = self.env._("Order signed")
        self.message_post(
            attachments=[(f"{filename}.pdf", report[0])],
            body=message,
        )
        return True
