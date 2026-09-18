# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models


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
