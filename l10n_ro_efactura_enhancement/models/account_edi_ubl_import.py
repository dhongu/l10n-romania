# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AccountEdiUBL(models.AbstractModel):
    _inherit = "account.edi.ubl"

    @staticmethod
    def _l10n_ro_price_amount_tolerance(price_amount_str, quantity):
        """Toleranța de rotunjire admisă pentru o linie, în valoare absolută.

        BT-146 (cbc:PriceAmount) este transmis rotunjit la numărul de zecimale
        ales de furnizor, deci produsul preț × cantitate poate să difere legitim
        de BT-131 (cbc:LineExtensionAmount) cu până la o jumătate de unitate de
        rotunjire per bucată. Ex. preț "0.30" pe 100 buc. poate acoperi orice
        valoare de linie între 29,50 și 30,50.

        Peste această limită diferența nu mai poate veni din rotunjire, ci
        dintr-un XML inconsistent.
        """
        decimals = 0
        if "." in (price_amount_str or ""):
            decimals = len(price_amount_str.strip().split(".")[1])
        return abs(quantity) * 0.5 * 10**-decimals

    def _import_ubl_invoice_line_add_price_unit_quantity_discount(self, collected_values):
        """EXTINDE account.edi.ubl.

        Core-ul derivă prețul unitar din BT-146 / BT-149
        (cbc:PriceAmount / cac:Price/cbc:BaseQuantity) și suprascrie astfel
        valoarea calculată din BT-131 (cbc:LineExtensionAmount). Când furnizorul
        completează greșit BT-149 — cazul frecvent fiind BaseQuantity egal cu
        InvoicedQuantity în loc de 1 — prețul unitar rezultat este de
        `InvoicedQuantity` ori mai mic, iar diferența ajunge tăcut într-o linie
        "Rounding" fără TVA, deci cu TVA subevaluat pe factură.

        BT-131 este câmp obligatoriu și reprezintă valoarea autoritativă a
        liniei, în timp ce BT-149 este opțional și servește doar la exprimarea
        prețului. Când cele două se contrazic peste toleranța de rotunjire,
        recalculăm linia din BT-131.
        """
        res = super()._import_ubl_invoice_line_add_price_unit_quantity_discount(collected_values)

        line_tree = collected_values["line_tree"]
        currency = collected_values["currency_values"]["currency"]
        file_document_sign = collected_values["file_document_sign"]

        line_extension_amount_str = line_tree.findtext(".//{*}LineExtensionAmount")
        if not line_extension_amount_str:
            return res
        line_extension_amount = float(line_extension_amount_str) * file_document_sign

        to_write = collected_values["to_write"]
        quantity = to_write.get("quantity") or 0.0
        price_unit = to_write.get("price_unit") or 0.0
        discount = to_write.get("discount") or 0.0

        # Invariantul pe care linia importată trebuie să îl respecte: subtotalul
        # calculat de Odoo reproduce exact BT-131.
        imported_subtotal = price_unit * quantity * (1 - discount / 100.0)
        difference = line_extension_amount - imported_subtotal

        price_amount_str = line_tree.findtext(".//{*}Price/{*}PriceAmount")
        tolerance = self._l10n_ro_price_amount_tolerance(price_amount_str, quantity)
        if abs(difference) <= tolerance or currency.is_zero(difference):
            # Diferență explicabilă prin rotunjirea prețului unitar: o lăsăm pe
            # seama liniei de rotunjire din core.
            return res

        invoiced_quantity_str = line_tree.findtext(".//{*}InvoicedQuantity") or line_tree.findtext(
            ".//{*}CreditedQuantity"
        )
        invoiced_quantity = float(invoiced_quantity_str) * file_document_sign if invoiced_quantity_str else 0.0

        total_allowances = sum(allowance["amount"] for allowance in collected_values["allowances"])

        # Reconstruim linia pornind de la BT-131, cu aceeași convenție ca în core:
        # reducerile de pe linie devin procent de discount, iar taxele de pe linie
        # intră în prețul unitar. Core-ul pornește de la
        # `subtotal = BT-131 + reduceri - taxe`, apoi adaugă taxele înapoi în preț,
        # deci taxele se simplifică și rămâne doar termenul cu reducerile.
        new_quantity = invoiced_quantity or 1.0
        new_price_unit = (line_extension_amount + total_allowances) / new_quantity
        gross_subtotal = new_price_unit * new_quantity
        new_discount = (total_allowances * 100 / gross_subtotal) if gross_subtotal else 0.0

        to_write["quantity"] = new_quantity
        to_write["price_unit"] = new_price_unit
        to_write["discount"] = new_discount

        base_quantity_str = line_tree.findtext("./{*}Price/{*}BaseQuantity")
        # `collected_values` este o copie superficială a dicționarului documentului,
        # deci lista de loguri este partajată cu importul — nu o recreăm aici, ca
        # mesajul să ajungă în chatter-ul facturii.
        logs = collected_values.get("logs")
        if isinstance(logs, list):
            logs.append(
                self.env._(
                    "Line %(line)s: the unit price declared by the supplier (BT-146 %(price)s "
                    "for a base quantity BT-149 of %(base_quantity)s) is inconsistent with the line "
                    "net amount (BT-131 %(line_amount)s). The line was recomputed from the line net "
                    "amount, which is the mandatory and authoritative value.",
                    line=line_tree.findtext("./{*}ID") or "",
                    price=price_amount_str or "",
                    base_quantity=base_quantity_str or "1",
                    line_amount=line_extension_amount_str,
                )
            )
        _logger.info(
            "l10n_ro_efactura_enhancement: linie UBL inconsistentă (PriceAmount=%s, BaseQuantity=%s, "
            "InvoicedQuantity=%s, LineExtensionAmount=%s); preț unitar recalculat %s -> %s",
            price_amount_str,
            base_quantity_str,
            invoiced_quantity_str,
            line_extension_amount_str,
            price_unit,
            new_price_unit,
        )
        return res
