# ©  2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import _, api, fields, models
from odoo.addons.stock_picking_batch.models.stock_picking_batch import StockPickingBatch as BaseBatch


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    l10n_ro_edi_stock_required = fields.Boolean(string="eTransport Required")
    l10n_ro_edi_carrier_id = fields.Many2one(
        "delivery.carrier",
        string="Delivery",
        compute="_compute_l10n_ro_edi_carrier_id",
        inverse="_inverse_l10n_ro_edi_carrier_id",
    )
    carrier_tracking_ref = fields.Char(string="Tracking Reference", copy=False)

    def _compute_l10n_ro_edi_carrier_id(self):
        for batch in self:
            if self.picking_ids:
                first_carrier = self.picking_ids[0].carrier_id
                batch.l10n_ro_edi_carrier_id = first_carrier

    def _inverse_l10n_ro_edi_carrier_id(self):
        for batch in self:
            for picking in batch.picking_ids:
                picking.carrier_id = batch.l10n_ro_edi_carrier_id

    def _compute_l10n_ro_edi_stock_enable(self):
        res = super()._compute_l10n_ro_edi_stock_enable()
        for picking in self:
            picking.l10n_ro_edi_stock_enable = picking.l10n_ro_edi_stock_required
        return res

    @api.depends("l10n_ro_edi_stock_enable", "state", "l10n_ro_edi_stock_state")
    def _compute_l10n_ro_edi_stock_enable_send(self):
        res = super()._compute_l10n_ro_edi_stock_enable_send()
        for picking in self:
            picking.l10n_ro_edi_stock_enable_send = (
                picking.l10n_ro_edi_stock_enable
                and picking.l10n_ro_edi_stock_state in (False, "stock_sending_failed")
                and not picking._l10n_ro_edi_stock_get_last_document("stock_validated")
            )
        return res

    @api.model
    def _l10n_ro_edi_stock_get_template_data(self, data: dict):
        res = super()._l10n_ro_edi_stock_get_template_data(data)
        for key in ("locStartTraseuRutier", "locFinalTraseuRutier"):
            locatie = res["data"]["notificare"][key].get("locatie", {})
            if locatie and not locatie["alteInfo"]:
                locatie["alteInfo"] = "-"
        transport_partner = data["transport_partner_id"]
        if transport_partner.country_code == "GR":
            res["data"]["notificare"]["dateTransport"]["codTaraOrgTransport"] = "EL"
        if res["data"]["notificare"]["partenerComercial"]["codTara"] == "GR":
            res["data"]["notificare"]["partenerComercial"]["codTara"] = "EL"
        return res

    def action_l10n_ro_edi_stock_fetch_status(self):
        res = super().action_l10n_ro_edi_stock_fetch_status()
        for picking in self:
            if picking.l10n_ro_edi_stock_state == "stock_validated":
                picking.carrier_tracking_ref = picking.l10n_ro_edi_stock_document_uit

        return res

    @api.model
    def _l10n_ro_edi_stock_validate_data(self, data: dict):
        errors = super()._l10n_ro_edi_stock_validate_data(data)

        for error in errors:
            if error == _("The delivery carrier partner has to be located in Romania."):
                errors.remove(error)

        return errors

    #monkey patching action_done
    def action_done(self):
        # EXTENDS 'stock_picking_batch'
        self.ensure_one()
        self._check_company()

        self.picking_ids.with_context(l10n_ro_edi_stock_validate_carrier=True)._l10n_ro_edi_stock_validate_carrier()
    
        if self.l10n_ro_edi_stock_required:
            # Carrier should be the same on all pickings
            first_carrier = self.picking_ids[0].carrier_id
            if any(picking.carrier_id != first_carrier for picking in self.picking_ids):
                raise UserError(_("All Pickings in a Batch Transfer should have the same Carrier"))
    
            # Commercial partner should be the same on all pickings
            first_commercial_partner = self.picking_ids[0].partner_id.commercial_partner_id
            if any(picking.partner_id.commercial_partner_id != first_commercial_partner for picking in self.picking_ids):
                raise UserError(_("All Pickings in a Batch Transfer should have the same Commercial Partner"))

        return BaseBatch.action_done(self)