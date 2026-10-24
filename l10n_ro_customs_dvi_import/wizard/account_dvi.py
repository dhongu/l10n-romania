# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import re

from markupsafe import Markup, escape

from odoo import api, fields, models
from odoo.exceptions import UserError

from ..tools import SniDviError, parse_pdf


def _normalize_ref(ref):
    return re.sub(r"[\s\-_.]", "", ref or "").upper()


def _normalize_vat(vat):
    return re.sub(r"^RO", "", re.sub(r"\s", "", vat or "").upper())


class AccountInvoiceDVI(models.TransientModel):
    _inherit = "account.invoice.dvi"

    dvi_file = fields.Binary(
        string="DVI PDF (SNI)",
        attachment=False,
        help="Customs import declaration as printed by the National Import System (SNI). When it is "
        "uploaded, the wizard is filled in with the values of the declaration: MRN, acceptance date, "
        "customs regime, customs duty (A00), import VAT and its base (B00). Check them and apply.",
    )
    dvi_filename = fields.Char()
    dvi_import_info = fields.Html(string="Read from the Declaration", readonly=True, sanitize=True)

    def _sni_error_message(self, error):
        params = error.params
        if error.code == "missing_pdfminer":
            return self.env._("The pdfminer.six Python library is required to read the declaration.")
        if error.code == "not_a_pdf":
            return self.env._("The file cannot be read as a PDF: %s", params["error"])
        if error.code == "not_a_declaration":
            return self.env._("The document is not an import customs declaration (DVI) printed by the SNI.")
        if error.code == "missing_mrn":
            return self.env._("The MRN of the declaration was not found.")
        if error.code == "item_count":
            return self.env._(
                "The declaration has %(count)s articles, but %(read)s were read from the document.", **params
            )
        if error.code == "totals":
            return self.env._(
                "The %(code)s amounts of the articles (%(amount)s) do not add up to the total "
                "of the declaration (%(total)s).",
                **params,
            )
        if error.code == "mixed_regimes":
            return self.env._("The articles have different customs regimes (%s).", params["regimes"])
        return error.code

    def _parse_dvi_file(self):
        self.ensure_one()
        try:
            dvi = parse_pdf(base64.b64decode(self.dvi_file))
        except SniDviError as e:
            raise UserError(self.env._("The DVI cannot be imported: %s", self._sni_error_message(e))) from e
        company_vat = _normalize_vat(self.env.company.vat)
        if company_vat and _normalize_vat(dvi.importer_vat) != company_vat:
            raise UserError(
                self.env._(
                    "The importer of the declaration (%(importer)s) is not the current company (%(company)s).",
                    importer=dvi.importer_vat,
                    company=self.env.company.vat,
                )
            )
        existing = self.env["stock.landed.cost"].search(
            [("dvi_number", "=", dvi.mrn), ("company_id", "=", self.env.company.id), ("state", "!=", "cancel")],
            limit=1,
        )
        if existing:
            raise UserError(
                self.env._("The declaration %(mrn)s is already recorded on %(dvi)s.", mrn=dvi.mrn, dvi=existing.name)
            )
        return dvi

    def _find_import_vat_tax(self, rate):
        """Purchase tax with the B00 rate; the one already proposed wins when its rate matches."""
        amount = rate * 100
        taxes = self.env["account.tax"].search(
            [
                ("type_tax_use", "=", "purchase"),
                ("amount_type", "=", "percent"),
                ("amount", "=", amount),
                ("company_id", "parent_of", self.env.company.id),
            ]
        )
        for tax in (self.tax_id, self.env.company.account_purchase_tax_id):
            if tax in taxes:
                return tax
        # an ordinary purchase tax: no reverse-charge repartition line (negative factor)
        plain = taxes.filtered(lambda t: not t.invoice_repartition_line_ids.filtered(lambda r: r.factor_percent < 0))
        return plain[:1]

    def _get_dvi_invoice(self):
        return self.env["account.move"].browse(self.env.context.get("active_id"))

    def _dvi_import_info(self, dvi, warnings):
        rows = [
            (self.env._("LRN"), dvi.lrn),
            (self.env._("Customs Release"), dvi.release_date and fields.Date.to_string(dvi.release_date)),
            (
                self.env._("Invoiced Amount"),
                self.env._(
                    "%(amount)s %(currency)s, exchange rate %(rate)s",
                    amount=f"{dvi.invoiced_amount:g}",
                    currency=dvi.currency,
                    rate=f"{dvi.exchange_rate:g}",
                ),
            ),
            (self.env._("Invoices on the Declaration"), ", ".join(ref.number for ref in dvi.invoice_refs)),
            (self.env._("Articles"), len(dvi.items)),
            (
                self.env._("Payment Method"),
                ", ".join(
                    f"{code} {total['method'] or '-'} ({total['payment_type']})" for code, total in dvi.totals.items()
                ),
            ),
        ]
        html = Markup("<table class='table table-sm mb-1'>%s</table>") % Markup().join(
            Markup("<tr><td>%s</td><td>%s</td></tr>") % (label, value or "") for label, value in rows
        )
        if warnings:
            html += Markup("<div class='alert alert-warning mb-0'>%s</div>") % Markup("<br/>").join(
                escape(warning) for warning in warnings
            )
        return html

    @api.onchange("dvi_file")
    def _onchange_dvi_file(self):
        if not self.dvi_file:
            self.dvi_import_info = False
            return
        dvi = self._parse_dvi_file()
        warnings = []

        self.dvi_number = dvi.mrn
        self.date = dvi.acceptance_date or dvi.release_date or self.date
        self.custom_duty = dvi.duty_total
        self.tax_base = dvi.vat_base

        regime = dvi.regimes[0] if dvi.regimes else ""
        self.customs_regime = regime if regime in ("4000", "4200") else "other"
        if self.customs_regime == "other":
            warnings.append(self.env._("Customs regime %s is not handled: check the declaration.", regime))

        # The amounts are transcribed, never recomputed: the regime only decides where B00 goes.
        self.vat_guarantee_amount = 0.0
        self.tax_value = dvi.vat_total
        if self.customs_regime == "4200":
            # exempt import: the B00 rate is irrelevant, the base module proposes the exempt tax
            self._onchange_customs_regime()
        else:
            if len(dvi.vat_rates) > 1:
                warnings.append(
                    self.env._(
                        "The articles have different VAT rates (%s): a single tax is recorded, "
                        "split the DVI if needed.",
                        ", ".join(f"{rate:.0%}" for rate in dvi.vat_rates),
                    )
                )
            tax = self._find_import_vat_tax(dvi.vat_rates[0]) if dvi.vat_rates else self.tax_id
            if tax:
                self.tax_id = tax
            elif dvi.vat_rates:
                warnings.append(self.env._("No purchase tax with the rate %s was found.", f"{dvi.vat_rates[0]:.0%}"))
            warnings.append(
                self.env._(
                    "Check the tax: VAT paid at customs, or deferred (VAT deferral certificate). "
                    "The declaration does not tell them apart."
                )
            )

        invoice = self._get_dvi_invoice()
        refs = {_normalize_ref(ref.number) for ref in dvi.invoice_refs}
        if invoice.ref and _normalize_ref(invoice.ref) not in refs:
            warnings.append(
                self.env._(
                    "The vendor reference of the bill (%(ref)s) is not among the invoices of the declaration.",
                    ref=invoice.ref,
                )
            )
        self.dvi_import_info = self._dvi_import_info(dvi, warnings)

    def do_create_dvi(self):
        dvi = self._parse_dvi_file() if self.dvi_file else None
        action = super().do_create_dvi()
        if dvi:
            landed_cost = self.env["stock.landed.cost"].browse(action["res_id"])
            attachment = self.env["ir.attachment"].create(
                {
                    "name": self.dvi_filename or f"{dvi.mrn}.pdf",
                    "datas": self.dvi_file,
                    "res_model": landed_cost._name,
                    "res_id": landed_cost.id,
                    "mimetype": "application/pdf",
                }
            )
            landed_cost.message_post(
                body=Markup("<p>%s</p>") % self.env._("Filled in from the SNI declaration %s.", dvi.mrn)
                + self._dvi_import_info(dvi, []),
                attachment_ids=attachment.ids,
            )
        return action
