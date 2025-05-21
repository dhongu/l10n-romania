import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _need_ubl_cii_xml(self, format):
        res = super()._need_ubl_cii_xml(format)

        return res

    def _cron_l10n_ro_edi_auto_send(self, limit=20):
        """Trimiterea automata a facturilor din ziua precedenta in SPV"""
        _logger.info("Cron job for sending invoices to SPV")
        domain = [
            ("move_type", "in", ("out_invoice", "out_refund")),
            ("state", "=", "posted"),
            ("date", "<", fields.Date.today()),
            ("date", ">=", fields.Date.today() - timedelta(days=1)),
            ("partner_id.country_id.code", "=", "RO"),
        ]

        invoices = self.search(domain, limit=limit + 1, order="date desc")
        need_retrigger = False
        if len(invoices) > limit:
            invoices = invoices[:limit]
            need_retrigger = True

        if not invoices:
            return False

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
            self.env.ref("l10n_ro_efactura_enhancement.ir_cron_l10n_ro_edi_auto_send")._trigger()

        return action

    def _l10n_ro_edi_send_invoice(self, xml_data):
        return super(AccountMove, self.with_context(active_id=self.id))._l10n_ro_edi_send_invoice(xml_data)
