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
        # (e.g. Shopify HU) to the SPV. Exclude invoices whose commercial
        # partner has a country explicitly set to something other than RO.
        # Partners without a country are left untouched to avoid regressions
        # on domestic B2C invoices that lack the country on the contact.
        partner_country = move.commercial_partner_id.country_id
        if partner_country and partner_country.code != "RO":
            return False
        return super()._is_ro_edi_applicable(move)

    def _send_mails(self, moves_data):
        # EXTENDS 'account'
        res = super()._send_mails(moves_data)
        # Mark every invoice that was actually emailed to the customer through
        # account.move.send so the SPV fetch-status cron never emails it a
        # second time after validation. This covers the operator's manual
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

    def _compute_l10n_ro_edi_send_enable(self):
        res = super()._compute_l10n_ro_edi_send_enable()
        for wizard in self:
            wizard.l10n_ro_edi_send_enable = wizard.l10n_ro_edi_send_enable and any(
                move.commercial_partner_id.country_id.code == "RO" for move in wizard.move_ids
            )
        return res

    @api.model
    def _postprocess_invoice_ubl_xml(self, invoice, invoice_data):
        # Adding the PDF to the XML

        get_param = self.env["ir.config_parameter"].sudo().get_param
        embed_pdf = safe_eval(get_param("efactura.embed_pdf", "False"))
        if not embed_pdf:
            return
        return super()._postprocess_invoice_ubl_xml(invoice, invoice_data)
