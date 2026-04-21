import logging
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    # l10n_ro_edi_state = fields.Selection( selection_add=[ ('invoice_sending_failed', 'Error')])

    def check_partner(self, partner):
        """Check if the partner has a country set, raise UserError if not."""
        if not partner.country_id:
            raise UserError(_("You can not post invoice without country for partner: %s") % partner.name)
        if partner.country_id.code == "RO":
            if not partner.state_id:
                raise UserError(_("You can not post invoice without state for partner: %s") % partner.name)
            if not partner.city:
                raise UserError(_("You can not post invoice without city for partner: %s") % partner.name)
            if not partner.street:
                raise UserError(_("You can not post invoice without street for partner: %s") % partner.name)

    def action_post(self):
        for move in self:
            if move.move_type in ["out_invoice", "out_refund"]:
                move.check_partner(move.partner_id)
                move.check_partner(move.partner_shipping_id)
        return super().action_post()

    def _need_ubl_cii_xml(self, ubl_cii_format=None):
        res = super()._need_ubl_cii_xml(ubl_cii_format)

        return res

    def _cron_l10n_ro_edi_fetch_status(self, limit=20, days=1, delay_days=0):
        need_retrigger = False
        _logger.info("⏱️ Cron job for fetch status from SPV")
        domain = [("l10n_ro_edi_access_token", "!=", False)]
        ro_companies = self or self.env["res.company"].sudo().search(domain)
        for company in ro_companies:
            domain = [
                ("move_type", "in", ("out_invoice", "out_refund")),
                ("state", "=", "posted"),
                ("date", "<", fields.Date.today() - timedelta(days=delay_days)),
                ("date", ">=", fields.Date.today() - timedelta(days=days + delay_days)),
                ("l10n_ro_edi_state", "=", "invoice_sent"),
                ("company_id", "=", company.id),
            ]

            invoices = self.search(domain, limit=limit, order="date")

            if invoices:
                invoices_name = invoices.mapped("name")
                _logger.info(f"🔍 Fetch status for invoices: {invoices_name}")
                invoices._l10n_ro_edi_fetch_invoice_sent_documents()
                need_retrigger = True
            else:
                _logger.info("No invoices to fetch status")

        if need_retrigger:
            at = fields.Datetime.now() + timedelta(minutes=2)
            # asteapata ca sa se termine trimiterea facturilor in SPV prin job-ul de mai sus
            _logger.info("⏳ Retrigger cron scheduled in 2 minutes")
            self.env.ref("l10n_ro_efactura_enhancement.ir_cron_l10n_ro_edi_fetch_status")._trigger(at)

    def _cron_l10n_ro_edi_auto_send(self, limit=20, days=1, delay_days=0):
        """Trimiterea automata a facturilor din ziua precedenta in SPV"""
        _logger.info("⏱️ Cron job for sending invoices to SPV")

        need_retrigger = False
        self._cron_l10n_ro_edi_fetch_status(limit=limit, days=days, delay_days=delay_days)

        domain = [("l10n_ro_edi_access_token", "!=", False)]
        ro_companies = self or self.env["res.company"].sudo().search(domain)
        for company in ro_companies:
            domain = [("l10n_ro_edi_document_ids.state", "=", "invoice_sending_failed")]
            invoice_sending_failed = self.search(domain)
            invoices_name = invoice_sending_failed.mapped("name")
            _logger.info(f"❌ Invoice sending failed: {invoices_name}")

            domain = [
                ("move_type", "in", ("out_invoice", "out_refund")),
                ("state", "=", "posted"),
                ("date", "<", fields.Date.today() - timedelta(days=delay_days)),
                ("date", ">=", fields.Date.today() - timedelta(days=days + delay_days)),
                ("partner_id.country_id.code", "=", "RO"),
                ("l10n_ro_edi_state", "=", False),
                ("company_id", "=", company.id),
            ]
            if invoice_sending_failed:
                domain.append(("id", "not in", invoice_sending_failed.ids))

            invoices = self.search(domain, limit=limit + 1, order="date desc")
            invoices_name = invoices.mapped("name")
            _logger.info(f"📤 Invoices to send to SPV: {invoices_name}")

            # daca au fost deja generate PDF-uri pentru facturi, le stergem
            invoice_pdf_report_ids = invoices.mapped("invoice_pdf_report_id")
            invoice_pdf_report_ids.unlink()

            if len(invoices) > limit:
                invoices = invoices[:limit]
                need_retrigger = True
                _logger.info("🔁 More invoices to send to SPV, retriggering cron...")

            if invoices:
                partner_ids = invoices.mapped("partner_id")
                partner_ids.write({"invoice_sending_method": "manual"})
                invoices_name = invoices.mapped("name")
                _logger.info(f"📨 Sending invoices to SPV: {invoices_name}")
                _logger.info(f"Count of invoices to send in SPV: {len(invoices)}")

                composer_vals = {
                    "move_ids": invoices.ids,
                }

                composer = self.env["account.move.send.batch.wizard"].sudo().create(composer_vals)
                composer.action_send_and_print()

            if need_retrigger:
                at = fields.Datetime.now() + timedelta(minutes=5)
                # asteapata ca sa se termine trimiterea facturilor in SPV prin job-ul de mai sus
                _logger.info("⏳ Retrigger cron scheduled in 5 minutes")
                self.env.ref("l10n_ro_efactura_enhancement.ir_cron_l10n_ro_edi_auto_send")._trigger(at)

    def _l10n_ro_edi_send_invoice(self, xml_data):
        return super(AccountMove, self.with_context(active_id=self.id))._l10n_ro_edi_send_invoice(xml_data)

    @api.model
    def _cron_account_move_send(self, job_count=10):
        domain = [
            ("sending_data", "!=", False),
            ("state", "=", "posted"),
        ]
        limit = job_count + 1

        # fix pt facturile care au fost programate pentru trimitere in 17.0
        # stergem sending_data pentru facturile care nu au author_partner_id (migrate din 17.0)
        invoices = self.env["account.move"].search(domain, limit=limit)
        invalid_moves = invoices.filtered(
            lambda m: m.sending_data and not m.sending_data.get("author_partner_id")
        )
        if invalid_moves:
            _logger.info(
                "🔧 Resetting sending_data for %d invoice(s) missing 'author_partner_id': %s",
                len(invalid_moves),
                invalid_moves.mapped("name"),
            )
            invalid_moves.write({"sending_data": False})
            self.env.cr.flush()
            invalid_moves.invalidate_recordset(["sending_data"])

        return super()._cron_account_move_send(job_count=job_count)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    l10n_ro_label_length = fields.Integer(string="Desc. length", compute="_compute_label_length")
    l10n_ro_product_length = fields.Integer(string="Prod. length", compute="_compute_label_length")

    @api.onchange("product_id", "name")
    def _compute_label_length(self):
        for line in self:
            if line.name:
                line.l10n_ro_label_length = len(line.name)
            else:
                line.l10n_ro_label_length = 0
            if line.product_id:
                line.l10n_ro_product_length = len(line.product_id.display_name)
            else:
                line.l10n_ro_product_length = 0
