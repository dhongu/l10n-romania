# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import api, fields, models


class AccountInvoiceDVI(models.TransientModel):
    _name = "account.invoice.dvi"
    _description = "account.invoice.dvi"

    date = fields.Date(
        string="DVI Date",
        help="Date on which the customs declaration was accepted. It determines the applicable VAT "
        "rate and the date of the generated journal entry.",
    )
    dvi_number = fields.Char(
        "DVI Number",
        help="Reference number of the customs import declaration (MRN), taken from the header of "
        "the declaration.\n\n"
        "It becomes the reference of the journal entry, so that the customs payment can be "
        "reconciled on account 446 per declaration.",
    )
    custom_duty = fields.Monetary(
        string="Customs Duty",
        help="Customs duty due, item A00 of the declaration.\n\n"
        "It is added to the cost of the received goods through a landed cost line: "
        "Dr 371 = Cr 446.",
    )
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)

    tax_value = fields.Monetary(
        string="VAT Paid at Customs",
        help="VAT actually due, the amount of item B00. Copy it from the declaration.\n\n"
        "This is the amount posted to account 4426, as it is. It is NOT recomputed when you change "
        "the base or the rate, so update it yourself whenever you change either.",
    )
    tax_base = fields.Monetary(
        string="Tax Base",
        help="Taxable base on which customs computed the VAT — the base of item B00. Copy it from "
        "the declaration.\n\n"
        "The proposed value is only the untaxed total of the supplier invoice and is NOT the base "
        "defined by art. 289 of Law 227/2015: it leaves out the customs duty, the commission and "
        "the incidental costs (transport, insurance) up to the first place of destination in "
        "Romania. When the customs value already includes the external transport, the base of the "
        "declaration is higher than the invoice total.",
    )
    tax_id = fields.Many2one(
        "account.tax",
        string="Import VAT",
        help="VAT rate applied by customs at the date the declaration was accepted.\n\n"
        "The proposed rate is the company default purchase tax. Check it against the declaration "
        "for goods at a reduced rate, such as basic foodstuffs.",
    )

    def _get_customs_payable_account(self):
        """Contul de decontare cu bugetul pentru drepturile de import.

        Planul RO din `l10n_ro` desparte 446 pe scadențe, iar ordinea e contraintuitivă:
        **4461 = reluate într-o perioadă MAI MARE de un an**, 4462 = până la un an. O căutare
        `446%` cu `limit=1` ia determinist 4461, adică încadrează datoria vamală la datorii
        peste un an în bilanț. Datoria vamală se stinge în zile, deci e datorie curentă —
        OMFP 1802/2014 pct. 360 alin. (1).

        Căutăm întâi 4462 și abia apoi orice 446, ca modulul să funcționeze și pe planuri
        de conturi care nu au defalcarea pe scadențe. Filtrăm pe companie: fără filtru, pe
        multi-company se putea prinde contul altei companii.
        """
        Account = self.env["account.account"]
        company = self.env.company
        for code in ("4462", "446"):
            account = Account.search(
                [("code", "=like", f"{code}%"), ("company_ids", "in", [company.id])],
                order="code",
                limit=1,
            )
            if account:
                return account
        return Account

    def _prepare_custom_duty_product(self):
        # Taxa vamală e datorie faţă de bugetul de stat -> 446 (analiticul de scadenţă îl alege
        # `_get_customs_payable_account`). Nu se foloseşte 447 „Fonduri speciale": funcţiunea din
        # OMFP 1802/2014 îl rezervă datoriilor către alte organisme publice, creditat exclusiv
        # prin 635, niciodată prin conturi de stoc.
        account = self._get_customs_payable_account()
        return {
            "name": self.env._("Custom Duty"),
            "type": "service",
            "invoice_policy": "order",
            "property_account_expense_id": account.id,
            "taxes_id": False,
            "company_id": False,
            # Produsul e utilizabil şi pe traseul nativ „factură furnizor -> landed cost",
            # nu doar din wizardul DVI.
            "landed_cost_ok": True,
            "split_method_landed_cost": "by_current_cost_price",
        }

    @api.model
    def get_custom_duty_product(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        product_id = get_param("dvi.custom_duty_product_id")

        return self.env["product.product"].browse(int(product_id)).exists()

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        active_id = self.env.context.get("active_id", False)
        invoice = self.env["account.move"].browse(active_id)
        defaults["date"] = invoice.invoice_date or fields.Date.today()
        tax_id = self.env.company.account_purchase_tax_id
        defaults["tax_id"] = tax_id.id
        amount_untaxed = abs(invoice.amount_untaxed_signed)
        defaults["tax_base"] = amount_untaxed
        tax_values = tax_id.compute_all(amount_untaxed)
        defaults["tax_value"] = tax_values["total_included"] - tax_values["total_excluded"]

        return defaults

    def do_create_dvi(self):
        active_id = self.env.context.get("active_id", False)
        invoice = self.env["account.move"].browse(active_id)

        pickings = self.env["stock.picking"]

        for line in invoice.invoice_line_ids:
            pickings |= line.purchase_line_id.order_id.picking_ids

        # determinare produse utilizate la landed cost
        values = {
            "date": self.date,
            "landed_type": "dvi",
            "dvi_number": self.dvi_number,
            "picking_ids": [(6, 0, pickings.ids)],
            "cost_lines": [],
            "account_journal_id": invoice.journal_id.id,
            "tax_id": self.tax_id.id,
            "tax_base": self.tax_base,
            "tax_value": self.tax_value,
        }
        set_param = self.env["ir.config_parameter"].sudo().set_param
        if self.custom_duty:
            custom_duty_product = self.get_custom_duty_product()
            if not custom_duty_product:
                vals = self._prepare_custom_duty_product()
                custom_duty_product = self.env["product.product"].create(vals)
                set_param("dvi.custom_duty_product_id", custom_duty_product.id)
            accounts_data = custom_duty_product.product_tmpl_id.get_product_accounts()

            values["cost_lines"] += [
                (
                    0,
                    0,
                    {
                        "name": custom_duty_product.name,
                        "product_id": custom_duty_product.id,
                        "price_unit": self.custom_duty,
                        "split_method": "by_current_cost_price",
                        "account_id": accounts_data["expense"].id,
                    },
                )
            ]

        landed_cost = self.env["stock.landed.cost"].create(values)
        invoice.write({"dvi_id": landed_cost.id})

        action = self.env.ref("stock_landed_costs.action_stock_landed_cost")
        action = action.sudo().read()[0]

        action["views"] = [(False, "form")]
        action["res_id"] = landed_cost.id

        return action
