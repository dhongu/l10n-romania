# ©  2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
from odoo import api, fields, models


class EfacturaDashboard(models.TransientModel):
    _name = "l10n.ro.efactura.dashboard"
    _description = "eFactura Dashboard"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    count_to_send = fields.Integer(
        string="De trimis",
        compute="_compute_counts",
    )
    count_sent = fields.Integer(
        string="Trimise (în așteptare)",
        compute="_compute_counts",
    )
    count_not_indexed = fields.Integer(
        string="Neindexate",
        compute="_compute_counts",
    )
    count_validated = fields.Integer(
        string="Validate",
        compute="_compute_counts",
    )
    count_refused = fields.Integer(
        string="Refuzate / Eroare",
        compute="_compute_counts",
    )
    count_sending_failed = fields.Integer(
        string="Eroare trimitere",
        compute="_compute_counts",
    )

    @api.depends("company_id")
    def _compute_counts(self):
        for rec in self:
            company = rec.company_id or self.env.company
            Move = self.env["account.move"]

            base_domain = [
                ("move_type", "in", ("out_invoice", "out_refund")),
                ("state", "=", "posted"),
                ("company_id", "=", company.id),
                ("partner_id.country_id.code", "=", "RO"),
            ]

            rec.count_to_send = Move.search_count(base_domain + [("l10n_ro_edi_state", "=", False)])
            rec.count_sent = Move.search_count(base_domain + [("l10n_ro_edi_state", "=", "invoice_sent")])
            rec.count_not_indexed = Move.search_count(base_domain + [("l10n_ro_edi_state", "=", "invoice_not_indexed")])
            rec.count_validated = Move.search_count(base_domain + [("l10n_ro_edi_state", "=", "invoice_validated")])
            rec.count_refused = Move.search_count(base_domain + [("l10n_ro_edi_state", "=", "invoice_refused")])
            rec.count_sending_failed = Move.search_count(
                [
                    ("move_type", "in", ("out_invoice", "out_refund")),
                    ("state", "=", "posted"),
                    ("company_id", "=", company.id),
                    ("l10n_ro_edi_document_ids.state", "=", "invoice_sending_failed"),
                ]
            )

    def action_view_to_send(self):
        return self._action_view_invoices([("l10n_ro_edi_state", "=", False)])

    def action_view_sent(self):
        return self._action_view_invoices([("l10n_ro_edi_state", "=", "invoice_sent")])

    def action_view_not_indexed(self):
        return self._action_view_invoices([("l10n_ro_edi_state", "=", "invoice_not_indexed")])

    def action_view_validated(self):
        return self._action_view_invoices([("l10n_ro_edi_state", "=", "invoice_validated")])

    def action_view_refused(self):
        return self._action_view_invoices([("l10n_ro_edi_state", "=", "invoice_refused")])

    def action_view_sending_failed(self):
        return self._action_view_invoices(
            [("l10n_ro_edi_document_ids.state", "=", "invoice_sending_failed")],
            skip_base=True,
        )

    def _action_view_invoices(self, extra_domain, skip_base=False):
        company = self.company_id or self.env.company
        if skip_base:
            domain = [
                ("move_type", "in", ("out_invoice", "out_refund")),
                ("state", "=", "posted"),
                ("company_id", "=", company.id),
            ] + extra_domain
        else:
            domain = [
                ("move_type", "in", ("out_invoice", "out_refund")),
                ("state", "=", "posted"),
                ("company_id", "=", company.id),
                ("partner_id.country_id.code", "=", "RO"),
            ] + extra_domain
        return {
            "type": "ir.actions.act_window",
            "name": "Facturi eFactura",
            "res_model": "account.move",
            "view_mode": "list,form",
            "domain": domain,
            "context": {"default_move_type": "out_invoice"},
        }

    def action_open_dashboard(self):
        rec = self.env["l10n.ro.efactura.dashboard"].create({"company_id": self.env.company.id})
        return {
            "type": "ir.actions.act_window",
            "name": "eFactura Dashboard",
            "res_model": "l10n.ro.efactura.dashboard",
            "res_id": rec.id,
            "view_mode": "form",
            "target": "main",
        }
