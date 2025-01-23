from datetime import timedelta

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _need_ubl_cii_xml(self):
        res = super()._need_ubl_cii_xml()

        return res

    def _cron_l10n_ro_edi_auto_send(self):
        """Trimiterea automata a facturilor din ziua precedenta in SPV"""

        domain = [
            ("move_type", "in", ("out_invoice", "out_refund")),
            ("state", "=", "posted"),
            ("date", "<", fields.Date.today()),
            ("date", ">=", fields.Date.today() - timedelta(days=1)),
            ("partner_id.country_id.code", "=", "RO"),
        ]

        invoices = self.search(domain)
        composer_vals = {
            "move_ids": invoices.ids,
            "checkbox_send_mail": False,
        }
        composer = self.env["account.move.send"].create(composer_vals)
        return composer.action_send_and_print()
