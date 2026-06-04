# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_create_invoice(self, attachment_ids=False):
        """Semnalează (ne-blocant) dacă există deja o factură din SPV legată de această comandă.

        Previne scenariul de duplicare: o factură a fost deja importată din SPV și
        împerecheată cu comanda, dar utilizatorul apasă „Create Bill" și generează încă una.
        """
        for order in self:
            spv_messages = self.env["l10n.ro.message.spv"].search(
                [("purchase_order_id", "=", order.id), ("invoice_id", "!=", False)]
            )
            existing_invoices = spv_messages.invoice_id.filtered(lambda m: m.state != "cancel")
            if existing_invoices:
                order.message_post(
                    body=self.env._(
                        "Atenție duplicat: pentru această comandă există deja factura/facturile "
                        "din SPV %(inv)s. Verificați înainte de a crea o factură nouă.",
                        inv=", ".join(existing_invoices.mapped("display_name")),
                    )
                )
        return super().action_create_invoice(attachment_ids=attachment_ids)
