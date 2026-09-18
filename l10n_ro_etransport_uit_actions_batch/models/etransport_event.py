# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class EtransportEvent(models.Model):
    """Evenimentul poate aparține unui LOT de transfer, nu doar unui transfer.

    `l10n_ro_edi_stock_batch` emite un singur UIT pentru tot lotul (un camion),
    deci și ștergerea / confirmarea / schimbarea vehiculului se fac pe lot.
    """

    _inherit = "l10n.ro.etransport.event"

    batch_id = fields.Many2one(
        "stock.picking.batch", string="Transfer Batch", ondelete="cascade", index=True, check_company=True
    )
    # obligatoriu în modulul de bază; pe lot nu are sens, cerința se mută în constrângere
    picking_id = fields.Many2one(required=False)

    # `uit` e în listă deliberat: e obligatoriu, deci constrângerea rulează și la
    # un create fără niciun părinte — altfel `constrains` nu s-ar declanșa deloc
    @api.constrains("picking_id", "batch_id", "uit")
    def _check_parent(self):
        for event in self:
            if not event.picking_id and not event.batch_id:
                raise ValidationError(self.env._("The event must belong to a transfer or to a transfer batch."))

    @api.depends("batch_id.company_id")
    def _compute_company_id(self):
        return super()._compute_company_id()

    def _get_parent(self):
        self.ensure_one()
        return self.batch_id or self.picking_id
