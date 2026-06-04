# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _l10n_ro_link_spv_purchase_order(self, purchase_order):
        """Leagă efectiv factura (venită din SPV) de liniile unei comenzi de achiziție.

        Cauza-rădăcină a facturilor duplicate: legătura informativă mesaj→PO nu setează
        niciodată `account.move.line.purchase_line_id`, singurul câmp care alimentează
        `purchase.order.line.qty_invoiced`. Fără el, PO rămâne `invoice_status='to invoice'`
        și fluxul standard „Create Bill" produce o a doua factură.

        Reutilizăm ruta standard `_find_and_set_purchase_orders` (modulul `purchase`), care
        potrivește liniile și setează `purchase_line_id`. Nu reimplementăm logica de matching.

        Metoda este idempotentă și ne-blocantă (semnalează duplicatele în chatter).
        """
        self.ensure_one()
        if not purchase_order or self.move_type not in self.get_purchase_types():
            return False

        # Idempotență: dacă liniile sunt deja legate de acest PO, nu mai facem nimic.
        if any(line.purchase_order_id == purchase_order for line in self.line_ids):
            return False

        # Gardă duplicat: PO are deja o altă factură proprie (linii legate pe alt move).
        other_invoice_lines = self.env["account.move.line"].search(
            [
                ("purchase_line_id", "in", purchase_order.order_line.ids),
                ("move_id", "!=", self.id),
                ("parent_state", "!=", "cancel"),
            ],
            limit=1,
        )
        if other_invoice_lines:
            existing_move = other_invoice_lines.move_id
            warning = self.env._(
                "Atenție duplicat: comanda de achiziție %(po)s are deja factura %(inv)s. "
                "Verificați înainte de a posta factura curentă din SPV.",
                po=purchase_order.name,
                inv=existing_move.display_name,
            )
            self.message_post(body=warning)
            existing_move.message_post(
                body=self.env._(
                    "Atenție duplicat: a fost importată din SPV factura %(inv)s pentru "
                    "aceeași comandă de achiziție %(po)s.",
                    inv=self.display_name,
                    po=purchase_order.name,
                )
            )
            if "l10n_ro_edi_is_duplicate" in self._fields:
                self.l10n_ro_edi_is_duplicate = True
            return False

        # Alimentăm matcher-ul standard cu numărul comenzii și declanșăm legarea liniilor.
        origin_parts = [part for part in (self.invoice_origin or "").split(", ") if part]
        if purchase_order.name not in origin_parts:
            origin_parts.append(purchase_order.name)
            self.invoice_origin = ", ".join(origin_parts)

        try:
            self.with_context(default_move_type=self.move_type)._find_and_set_purchase_orders(
                [purchase_order.name],
                self.partner_id.id,
                self.amount_total,
            )
        except Exception as e:  # pragma: no cover - robustețe import
            _logger.warning(
                "Nu s-a putut lega factura %s de comanda %s: %s",
                self.display_name,
                purchase_order.name,
                e,
            )
            return False

        return True

    def _l10n_ro_flag_cross_stack_duplicate(self):
        """Aliniere cross-stack: semnalează dacă există deja o factură cu aceeași cheie de
        deduplicare, creată de cealaltă stivă SPV (Enterprise l10n_ro_edi vs OCA).

        Cuplaj soft: citim câmpul `l10n_ro_edi_dedup_key` doar prin nume, cu gardă de
        prezență — dacă modulul `l10n_ro_efactura_dedup` nu este instalat, nu facem nimic
        (nicio dependență în manifest, nicio eroare la import). Ne-blocant: doar marcaj +
        notă în chatter, pentru revizuire manuală.
        """
        self.ensure_one()
        if "l10n_ro_edi_dedup_key" not in self._fields:
            return False
        key = self.l10n_ro_edi_dedup_key
        if not key or self.move_type not in self.get_purchase_types():
            return False

        duplicate = self.env["account.move"].search(
            [
                ("l10n_ro_edi_dedup_key", "=", key),
                ("id", "!=", self.id),
                ("company_id", "=", self.company_id.id),
                ("move_type", "in", self.get_purchase_types()),
                ("state", "!=", "cancel"),
            ],
            order="id",
            limit=1,
        )
        if not duplicate:
            return False

        if "l10n_ro_edi_is_duplicate" in self._fields:
            self.l10n_ro_edi_is_duplicate = True
        self.message_post(
            body=self.env._(
                "Posibil duplicat cross-stack SPV: există deja factura %(inv)s cu aceeași "
                "cheie de deduplicare (CUI furnizor + nr + dată + sumă). "
                "Verificați înainte de a posta.",
                inv=duplicate.display_name,
            )
        )
        return True
