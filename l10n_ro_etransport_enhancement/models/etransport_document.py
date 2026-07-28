# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models

# Codurile ANAF pentru tipul documentului însoțitor (schema eTransport v2,
# secțiunea `documenteTransport/@tipDocument`).
DOCUMENT_TYPES = [
    ("10", "CMR"),
    ("20", "Factură"),
    ("30", "Aviz de însoțire a mărfii"),
    ("9999", "Altele"),
]


class L10nRoEtransportDocument(models.Model):
    _name = "l10n.ro.etransport.document"
    _description = "Document însoțitor eTransport"
    _order = "date desc, id desc"

    picking_id = fields.Many2one("stock.picking", string="Transfer", required=True, ondelete="cascade", index=True)
    document_type = fields.Selection(DOCUMENT_TYPES, string="Tip document", required=True, default="30")
    name = fields.Char(string="Număr document", required=True)
    date = fields.Date(string="Data documentului", required=True, default=fields.Date.context_today)
    remarks = fields.Char(string="Observații")
    # compute (nu related) ca modulul de batch să poată extinde sursa companiei
    # cu documentele declarate direct pe lotul de transfer
    company_id = fields.Many2one("res.company", string="Companie", compute="_compute_company_id", store=True)

    @api.depends("picking_id.company_id")
    def _compute_company_id(self):
        for doc in self:
            doc.company_id = doc.picking_id.company_id

    @api.depends("document_type", "name")
    def _compute_display_name(self):
        types = dict(DOCUMENT_TYPES)
        for doc in self:
            doc.display_name = f"{types.get(doc.document_type, '')} {doc.name or ''}".strip()
