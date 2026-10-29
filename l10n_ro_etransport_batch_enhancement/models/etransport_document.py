# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class L10nRoEtransportDocument(models.Model):
    """Documentele însoțitoare pot fi declarate și pe BATCH, nu doar pe transfer.

    Cazul real: un batch = un camion = **un CMR** pentru tot transportul, în timp
    ce avizele sunt per transfer. La generarea declarației pentru batch se trimit
    documentele batch-ului + cele ale transferurilor din el.
    """

    _inherit = "l10n.ro.etransport.document"

    batch_id = fields.Many2one("stock.picking.batch", string="Lot de transfer", ondelete="cascade", index=True)
    # `picking_id` era obligatoriu în modulul de bază — pe documentele de batch nu
    # are sens, deci relaxăm cerința și o mutăm în constrângerea de mai jos
    picking_id = fields.Many2one(required=False)

    @api.constrains("picking_id", "batch_id")
    def _check_document_parent(self):
        for doc in self:
            if not doc.picking_id and not doc.batch_id:
                raise ValidationError(
                    self.env._("Documentul însoțitor trebuie legat de un transfer sau de un lot de transfer.")
                )

    @api.depends("picking_id.company_id", "batch_id.company_id")
    def _compute_company_id(self):
        for doc in self:
            doc.company_id = doc.picking_id.company_id or doc.batch_id.company_id
