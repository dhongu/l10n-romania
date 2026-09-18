# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models

# Codurile ANAF pentru tipul documentului însoțitor (schema eTransport v2,
# secțiunea `documenteTransport/@tipDocument`).
DOCUMENT_TYPES = [
    ("10", "CMR"),
    ("20", "Invoice"),
    ("30", "Delivery Note"),
    ("9999", "Other"),
]


class L10nRoEtransportDocument(models.Model):
    _name = "l10n.ro.etransport.document"
    _description = "eTransport Accompanying Document"
    _order = "date desc, id desc"

    picking_id = fields.Many2one("stock.picking", string="Transfer", required=True, ondelete="cascade", index=True)
    document_type = fields.Selection(DOCUMENT_TYPES, string="Document Type", required=True, default="30")
    name = fields.Char(string="Document Number", required=True, help="Number printed on the accompanying document.")
    date = fields.Date(string="Document Date", required=True, default=fields.Date.context_today)
    remarks = fields.Char(
        string="Remarks", help="Optional information about this document. Leave empty if not applicable."
    )
    # compute (nu related) ca modulul de batch să poată extinde sursa companiei
    # cu documentele declarate direct pe lotul de transfer
    company_id = fields.Many2one("res.company", string="Company", compute="_compute_company_id", store=True)

    @api.depends("picking_id.company_id")
    def _compute_company_id(self):
        for doc in self:
            doc.company_id = doc.picking_id.company_id

    @api.depends("document_type", "name")
    @api.depends_context("lang")
    def _compute_display_name(self):
        types = dict(self._fields["document_type"]._description_selection(self.env))
        for doc in self:
            doc.display_name = f"{types.get(doc.document_type, '')} {doc.name or ''}".strip()
