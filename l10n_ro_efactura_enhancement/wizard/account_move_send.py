import logging

from odoo import api, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class AccountMoveSend(models.AbstractModel):
    _inherit = "account.move.send"

    @api.model
    def _is_ro_edi_applicable(self, move):
        # EXTENDS 'l10n_ro_edi'
        # The core check only verifies the issuing company is Romanian
        # (``move.country_code == 'RO'``), so the standard "Send & Print"
        # wizard would also upload invoices issued to foreign customers
        # (e.g. Shopify HU) to the SPV. Delegate the destination decision to
        # ``_l10n_ro_is_spv_target``, shared with the manual SPV button, the
        # auto-send cron and the dashboard KPIs.
        # In O19 the wizard builds its checkboxes from
        # ``_get_default_extra_edis`` (which filters on ``is_applicable``), so
        # this single override also hides the "Send E-Factura to SPV" checkbox.
        if not move._l10n_ro_is_spv_target():
            return False
        return super()._is_ro_edi_applicable(move)

    def _send_mails(self, moves_data):
        # EXTENDS 'account'
        res = super()._send_mails(moves_data)
        # Mark every invoice that was actually emailed to the customer through
        # account.move.send so the validated-invoice cron
        # (_cron_l10n_ro_spv_send_validated_emails) never emails it a second
        # time after the SPV validates it. This covers the operator's manual
        # "Send & Print" (email at posting time) as well as our own
        # post-validation email. The SPV upload path uses
        # sending_methods={"manual"} (no email), so it never reaches here and
        # the cron still emails those invoices once, after validation.
        # We mirror the recipient condition used by the core loop above so we
        # only flag invoices that truly had an email sent.
        emailed = self.env["account.move"].browse(
            move.id
            for move, move_data in moves_data.items()
            if move.move_type in ("out_invoice", "out_refund")
            and (move.partner_id.email or move_data.get("mail_partner_ids"))
        )
        emailed = emailed.filtered(lambda m: not m.l10n_ro_spv_validated_email_sent)
        if emailed:
            emailed.l10n_ro_spv_validated_email_sent = True
        return res

    def _get_alerts(self, moves, moves_data):
        alerts = super()._get_alerts(moves, moves_data)
        _logger.info(f"alerts: {alerts}")

        account_missing_email = alerts.get("account_missing_email", {})
        if account_missing_email:
            action = account_missing_email.get("action", {})
            if action:
                context = action.get("context", {})
                context.pop("lastcall", None)

        return alerts

    def _postprocess_invoice_ubl_xml(self, invoice, invoice_data):
        # EXTENDS account_edi_ubl_cii
        # În O19 metoda trăiește pe modelul abstract account.move.send (nu pe
        # wizard, ca în 18.0), iar fluxul de trimitere o apelează de pe acesta.
        # Override-ul de pe account.move.send.wizard nu se mai declanșa, deci
        # parametrul efactura.embed_pdf era ignorat. Îl mutăm aici ca să rămână
        # funcțional: dacă embed_pdf e False, nu atașăm PDF-ul în XML-ul UBL.
        get_param = self.env["ir.config_parameter"].sudo().get_param
        embed_pdf = safe_eval(get_param("efactura.embed_pdf", "False"))
        if not embed_pdf:
            return
        return super()._postprocess_invoice_ubl_xml(invoice, invoice_data)


class AccountMoveSendWizard(models.TransientModel):
    _inherit = "account.move.send.wizard"

    # todo: de gasit cum se poate face in 18.0
    # l10n_ro_edi_resend_enable = fields.Boolean(compute="_compute_l10n_ro_edi_resend_enable")

    # @api.depends("l10n_ro_edi_send_enable")
    # def _compute_l10n_ro_edi_resend_enable(self):
    #     for wizard in self:
    #         wizard.l10n_ro_edi_resend_enable = any(
    #             not move._need_ubl_cii_xml("ciusro") and move.country_code == "RO" and move.invoice_pdf_report_id
    #             for move in wizard.move_ids
    #         )

    def action_resend(self):
        self.ensure_one()
        invoice_pdf_report_ids = self.move_ids.mapped("invoice_pdf_report_id")
        invoice_pdf_report_ids.unlink()

        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "views": [(False, "form")],
            "target": "new",
        }

    # _compute_l10n_ro_edi_send_enable nu mai exista in v19 standard
