import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _need_ubl_cii_xml(self, format):
        res = super()._need_ubl_cii_xml(format)

        return res

    def _cron_l10n_ro_edi_auto_send(self):
        """Trimiterea automata a facturilor din ziua precedenta in SPV"""
        _logger.info("Cron job for sending invoices to SPV")
        domain = [
            ("move_type", "in", ("out_invoice", "out_refund")),
            ("state", "=", "posted"),
            ("date", "<", fields.Date.today()),
            ("date", ">=", fields.Date.today() - timedelta(days=1)),
            ("partner_id.country_id.code", "=", "RO"),
        ]

        invoices = self.search(domain)

        _logger.info(f"Count of invoices to send: {len(invoices)}")

        composer_vals = {
            "move_ids": invoices.ids,
            "checkbox_send_mail": False,
        }

        composer = self.env["account.move.send"].create(composer_vals)
        return composer.action_send_and_print()
