# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models


class EtransportActionWizard(models.TransientModel):
    _inherit = "l10n.ro.etransport.action.wizard"

    batch_id = fields.Many2one("stock.picking.batch", string="Transfer Batch", readonly=True)
    picking_id = fields.Many2one(required=False)

    def _get_parent(self):
        self.ensure_one()
        return self.batch_id or self.picking_id

    def _get_event_values(self):
        values = super()._get_event_values()
        if self.batch_id:
            values = {"batch_id": self.batch_id.id, "picking_id": False}
        return values

    @api.depends("batch_id")
    def _compute_uit(self):
        return super()._compute_uit()

    @api.onchange("batch_id")
    def _onchange_batch_vehicle_defaults(self):
        self._onchange_vehicle_defaults()
