import logging
from datetime import timedelta

from odoo import _, fields, models
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

    def _cron_l10n_ro_edi_auto_send(self, limit=20, days=1):
        """Trimiterea automata a facturilor din ziua precedenta in SPV"""
        _logger.info("Cron job for sending invoices to SPV")

        need_retrigger = False

        domain = [("l10n_ro_edi_access_token", "!=", False)]
        ro_companies = self or self.env["res.company"].sudo().search(domain)
        for company in ro_companies:
            domain = [
                ("move_type", "in", ("out_invoice", "out_refund")),
                ("state", "=", "posted"),
                ("date", "<", fields.Date.today()),
                ("date", ">=", fields.Date.today() - timedelta(days=days)),
                ("l10n_ro_edi_state", "=", "invoice_sending"),
                ("company_id", "=", company.id),
            ]

            invoices = self.search(domain, limit=limit, order="date")

            if invoices:
                invoices_name = invoices.mapped("name")
                _logger.info(f"Fetch status for invoices: {invoices_name}")
                invoices._l10n_ro_edi_fetch_invoice_sending_documents()
                need_retrigger = True

            domain = [
                ("move_type", "in", ("out_invoice", "out_refund")),
                ("state", "=", "posted"),
                ("date", "<", fields.Date.today()),
                ("date", ">=", fields.Date.today() - timedelta(days=days)),
                ("partner_id.country_id.code", "=", "RO"),
                ("l10n_ro_edi_state", "=", False),
                ("company_id", "=", company.id),
            ]

            invoices = self.search(domain, limit=limit + 1, order="date desc")

            # daca au fost deja generate PDF-uri pentru facturi, le stergem
            invoice_pdf_report_ids = invoices.mapped("invoice_pdf_report_id")
            invoice_pdf_report_ids.unlink()

            if len(invoices) > limit:
                invoices = invoices[:limit]
                need_retrigger = True

            if invoices:
                invoices_name = invoices.mapped("name")
                _logger.info(f"Sending invoices to SPV: {invoices_name}")
                _logger.info(f"Count of invoices to send in SPV: {len(invoices)}")

                composer_vals = {
                    "move_ids": invoices.ids,
                    "checkbox_download": False,
                    "checkbox_send_mail": False,
                    "mode": "invoice_multi",
                }

                composer = self.env["account.move.send"].create(composer_vals)
                action = composer.action_send_and_print()
                self.env.ref("account.ir_cron_account_move_send")._trigger()

            if need_retrigger:
                at = fields.Datetime.now() + timedelta(minutes=5)
                # asteapata ca sa se termine trimiterea facturilor in SPV prin job-ul de mai sus
                self.env.ref("l10n_ro_efactura_enhancement.ir_cron_l10n_ro_edi_auto_send")._trigger(at)

        return action

    def _l10n_ro_edi_send_invoice(self, xml_data):
        return super(AccountMove, self.with_context(active_id=self.id))._l10n_ro_edi_send_invoice(xml_data)
