import logging

from odoo import models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class AccountMoveSend(models.AbstractModel):
    _inherit = "account.move.send"

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
