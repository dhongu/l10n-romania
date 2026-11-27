# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models
from odoo.exceptions import UserError


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    l10n_ro_etransport_event_ids = fields.One2many("l10n.ro.etransport.event", "batch_id", string="UIT Events")
    l10n_ro_etransport_uit_deleted = fields.Boolean(
        string="UIT Deleted",
        compute="_compute_l10n_ro_etransport_uit_flags",
        help="The current UIT was deleted at ANAF; the notification is no longer valid.",
    )
    l10n_ro_etransport_event_pending = fields.Boolean(
        string="UIT Event Pending", compute="_compute_l10n_ro_etransport_uit_flags"
    )
    l10n_ro_etransport_enable_actions = fields.Boolean(
        string="UIT Actions Enabled", compute="_compute_l10n_ro_etransport_uit_flags"
    )
    l10n_ro_etransport_uit_live = fields.Boolean(
        string="UIT Live",
        compute="_compute_l10n_ro_etransport_uit_flags",
        help="The UIT is validated by ANAF and not deleted: cancelling the batch deletes it first.",
    )

    @api.depends(
        "l10n_ro_etransport_event_ids.state",
        "l10n_ro_etransport_event_ids.event_type",
        "l10n_ro_edi_stock_state",
        "l10n_ro_edi_stock_document_uit",
    )
    def _compute_l10n_ro_etransport_uit_flags(self):
        # aceeași regulă ca pe transfer (vezi `stock.picking` în modulul de bază)
        for batch in self:
            uit = batch.l10n_ro_edi_stock_document_uit
            events = (
                batch.l10n_ro_etransport_event_ids.filtered(lambda e: e.uit == uit)
                if uit
                else batch.env["l10n.ro.etransport.event"]
            )
            batch.l10n_ro_etransport_uit_deleted = any(e.event_type == "DEL" and e.state == "validated" for e in events)
            batch.l10n_ro_etransport_event_pending = any(e.state == "sent" for e in events)
            batch.l10n_ro_etransport_uit_live = batch._l10n_ro_etransport_uit_is_live()
            batch.l10n_ro_etransport_enable_actions = bool(
                uit
                and batch.l10n_ro_edi_stock_state == "stock_validated"
                and not batch.l10n_ro_etransport_uit_deleted
                and not batch.l10n_ro_etransport_event_pending
            )

    def action_l10n_ro_etransport_fetch_event_status(self):
        self.l10n_ro_etransport_event_ids._fetch_status()

    def action_l10n_ro_etransport_open_action_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "l10n.ro.etransport.action.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_batch_id": self.id,
                "default_event_type": self.env.context.get("default_event_type", "DEL"),
            },
        }

    def _l10n_ro_etransport_uit_is_live(self):
        """UIT validat de ANAF și încă neșters: marfa poate circula sub el."""
        self.ensure_one()
        return bool(
            self.l10n_ro_edi_stock_document_uit
            and self.l10n_ro_edi_stock_state == "stock_validated"
            and not self.l10n_ro_etransport_uit_deleted
        )

    def action_l10n_ro_etransport_cancel(self):
        """Butonul *Cancel* din formularul lotului: ca pe transfer, cu UIT viu
        se deschide wizardul de ștergere (DEL), care anulează apoi lotul."""
        live = self.filtered(lambda r: r._l10n_ro_etransport_uit_is_live())
        if not live:
            return self.action_cancel()
        if len(self) > 1:
            raise UserError(
                self.env._(
                    "Delete the UIT of each document before cancelling: %(names)s",
                    names=", ".join(live.mapped("display_name")),
                )
            )
        if self.l10n_ro_etransport_event_pending:
            raise UserError(
                self.env._(
                    "An eTransport event for UIT %(uit)s is still waiting for the ANAF answer. "
                    "Fetch its status before cancelling.",
                    uit=self.l10n_ro_edi_stock_document_uit,
                )
            )
        action = self.with_context(default_event_type="DEL").action_l10n_ro_etransport_open_action_wizard()
        action["context"]["default_cancel_after_send"] = True
        return action
