from odoo import api, models
from odoo.tools.safe_eval import safe_eval


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
