# © 2026 Terrabit
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class MessageSPV(models.Model):
    _inherit = "l10n.ro.message.spv"

    def _l10n_ro_apply_number_from_message(self):
        """Number the matched draft with the reference from the SPV message.

        Only for journals explicitly flagged for it. The case is self-billing
        (Cod fiscal art. 319 (18)): the customer issues the invoice in our
        name, so the legal number is the one they allocated and the document
        must carry it, not a number from our own sequence. Pulling such a
        document into the regular sales sequence also breaks it, since these
        documents arrive days after the invoices already issued and are dated
        back.
        """
        for message in self:
            invoice = message.invoice_id
            if not invoice or not message.ref:
                continue
            if not invoice.journal_id.l10n_ro_spv_number_from_message:
                continue
            # A posted document is already numbered and its number is part of
            # the ledger; renumbering is not ours to do here.
            if invoice.state != "draft" or invoice.name == message.ref:
                continue
            duplicate = self.env["account.move"].search(
                [
                    ("name", "=", message.ref),
                    ("journal_id", "=", invoice.journal_id.id),
                    ("company_id", "=", invoice.company_id.id),
                    ("id", "!=", invoice.id),
                ],
                limit=1,
            )
            if duplicate:
                # Posting would fail on the unique-number constraint anyway;
                # leave the sequence to assign a number and let the user
                # decide, rather than silently producing an unpostable draft.
                _logger.warning(
                    "SPV message %s: number %s already used in journal %s by "
                    "move %s, keeping the journal sequence on move %s.",
                    message.name,
                    message.ref,
                    invoice.journal_id.code,
                    duplicate.id,
                    invoice.id,
                )
                continue
            invoice.write({"name": message.ref})

    def get_data_from_invoice(self):
        # Runs before the base method: that one writes the message state and
        # the derived data, so the number must already be on the invoice.
        self._l10n_ro_apply_number_from_message()
        return super().get_data_from_invoice()
