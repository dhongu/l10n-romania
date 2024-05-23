# ©  2024-now Dan Stoica <danila(@)terrabit(.)ro
# See README.rst file on addons root folder for license details

from odoo import models


class AccountEdiXmlCIUSRO(models.Model):
    _inherit = "account.edi.xml.cius_ro"

    def _export_invoice_vals(self, invoice):
        vals_list = super()._export_invoice_vals(invoice)
        with_discount = any(line.discount for line in invoice.invoice_line_ids)
        if not with_discount:
            return vals_list
        # corectie discount
        if invoice.move_type == "out_invoice":
            # calcul amount fara discount din linii
            line_extension_amount = 0.0
            for line_vals in vals_list["vals"]["invoice_line_vals"]:
                value = round(line_vals["line_extension_amount"], line_vals["currency_dp"])
                line_extension_amount += value
            if vals_list["vals"]["legal_monetary_total_vals"]["line_extension_amount"] != line_extension_amount:
                # aplicare corectie:
                # total fara discount = suma linii fara discount
                vals_list["vals"]["legal_monetary_total_vals"]["line_extension_amount"] = line_extension_amount

                # total fara taxe = total fara discount - total discount
                if vals_list["vals"]["legal_monetary_total_vals"]["allowance_total_amount"]:
                    vals_list["vals"]["legal_monetary_total_vals"]["tax_exclusive_amount"] = (
                        line_extension_amount - vals_list["vals"]["legal_monetary_total_vals"]["allowance_total_amount"]
                    )

                # calcul total taxe
                taxes_total = 0.0
                for tax in vals_list["vals"]["tax_total_vals"]:
                    taxes_total += round(tax["tax_amount"], tax["currency_dp"])

                # total cu taxe = total fara taxe + total taxe
                vals_list["vals"]["legal_monetary_total_vals"]["tax_inclusive_amount"] = (
                    vals_list["vals"]["legal_monetary_total_vals"]["tax_exclusive_amount"] + taxes_total
                )

                # fix taxable
                if len(vals_list["vals"]["tax_total_vals"]) == 1:
                    vals_list["vals"]["tax_total_vals"][0]["tax_subtotal_vals"][0]["taxable_amount"] = vals_list[
                        "vals"
                    ]["legal_monetary_total_vals"]["tax_exclusive_amount"]
                    vals_list["taxes_vals"]["base_amount"] = vals_list["vals"]["legal_monetary_total_vals"][
                        "tax_exclusive_amount"
                    ]
                    vals_list["taxes_vals"]["base_amount_currency"] = vals_list["vals"]["legal_monetary_total_vals"][
                        "tax_exclusive_amount"
                    ]

                # fix payable amount
                vals_list["vals"]["legal_monetary_total_vals"]["payable_amount"] = (
                    vals_list["vals"]["legal_monetary_total_vals"]["tax_inclusive_amount"]
                    - vals_list["vals"]["legal_monetary_total_vals"]["prepaid_amount"]
                )
        elif invoice.move_type == "out_refund":
            # aplicare corectie, deocamdata discount inclus in pret pana vedem de ce da erori ciudate:
            line_extension_amount = 0.0
            for line_vals in vals_list["vals"]["invoice_line_vals"]:
                # includere discount in pret
                if "allowance_charge_vals" in line_vals:
                    if len(line_vals["allowance_charge_vals"]) == 1:
                        charge_vals = line_vals["allowance_charge_vals"][0]
                        line_vals.pop("allowance_charge_vals")
                        line_vals["line_extension_amount"] = line_vals["line_extension_amount"] - charge_vals["amount"]
                        if line_vals["invoiced_quantity"]:
                            price_per_unit = line_vals["line_extension_amount"] / line_vals["invoiced_quantity"]
                        else:
                            price_per_unit = line_vals["price_vals"]["price_amount"]
                        line_vals["price_vals"]["price_amount"] = price_per_unit
                line_extension_amount += round(line_vals["line_extension_amount"], line_vals["currency_dp"])
            vals_list["vals"]["legal_monetary_total_vals"]["line_extension_amount"] = line_extension_amount

            # aplicare restul de corectii pe totaluri
            vals_list["vals"]["legal_monetary_total_vals"]["tax_exclusive_amount"] = line_extension_amount

            # calcul total taxe
            taxes_total = 0.0
            for tax in vals_list["vals"]["tax_total_vals"]:
                taxes_total += round(tax["tax_amount"], tax["currency_dp"])
            vals_list["vals"]["legal_monetary_total_vals"]["tax_inclusive_amount"] = line_extension_amount + taxes_total

            # fix taxable
            if len(vals_list["vals"]["tax_total_vals"]) == 1:
                vals_list["vals"]["tax_total_vals"][0]["tax_subtotal_vals"][0]["taxable_amount"] = line_extension_amount
                vals_list["taxes_vals"]["base_amount"] = line_extension_amount
                vals_list["taxes_vals"]["base_amount_currency"] = line_extension_amount

            # fix payable amount
            vals_list["vals"]["legal_monetary_total_vals"]["payable_amount"] = (
                vals_list["vals"]["legal_monetary_total_vals"]["tax_inclusive_amount"]
                - vals_list["vals"]["legal_monetary_total_vals"]["prepaid_amount"]
            )

        return vals_list
