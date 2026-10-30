# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import api, fields, models
from odoo.exceptions import UserError

from ..models.stock_landed_cost import CUSTOMS_REGIMES


class AccountInvoiceDVILine(models.TransientModel):
    _name = "account.invoice.dvi.line"
    _description = "Article of the customs declaration"
    _order = "number, id"

    wizard_id = fields.Many2one("account.invoice.dvi", required=True, ondelete="cascade")
    currency_id = fields.Many2one(related="wizard_id.currency_id")
    number = fields.Integer("Article")
    taric_code = fields.Char("TARIC Code", required=True)
    customs_value = fields.Monetary("Customs Value")
    custom_duty = fields.Monetary("Customs Duty", help="Customs duty (A00) of the article.")


class AccountInvoiceDVI(models.TransientModel):
    _name = "account.invoice.dvi"
    _description = "account.invoice.dvi"

    customs_office_id = fields.Many2one(
        "res.partner",
        "Customs Office",
        domain=[("l10n_ro_customs_office_code", "!=", False)],
        help="Customs office where the declaration was lodged: the partner of the amounts due at customs.",
    )
    line_ids = fields.One2many(
        "account.invoice.dvi.line",
        "wizard_id",
        "Articles",
        help="Articles of the declaration, with their TARIC code and customs duty. Each article becomes a "
        "line of the landed cost, split only on its own products. Without articles, the customs duty is "
        "split on all the received products.",
    )

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

    customs_regime = fields.Selection(
        CUSTOMS_REGIMES,
        default="4000",
        help="Customs procedure code, the first four digits of box 37 of the declaration.\n\n"
        "- 4000: import VAT due, paid at customs or deferred (see Import VAT);\n"
        "- 4200: import exempt from VAT (art. 293(1)(m) of Law 227/2015), the goods being supplied "
        "to a customer in another Member State. The VAT computed by customs is only held as a "
        "guarantee and is NOT recorded: the import VAT stays empty and only the base goes to "
        "row 29 of the VAT return.",
    )
    vat_guarantee_amount = fields.Monetary(
        string="VAT Held as Guarantee",
        help="Regime 4200: VAT computed by customs and held from the importer's guarantee account, as "
        "shown on the declaration. It is only recorded on the DVI, for the release request after the "
        "confirmed CMR; no journal entry is generated.",
    )
    tax_value = fields.Monetary(
        string="Import VAT Amount",
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
        "for goods at a reduced rate, such as basic foodstuffs.\n\n"
        "THE TAX IS ALSO THE SWITCH between the two regimes of art. 326 of Law 227/2015:\n"
        "- an ordinary purchase tax means the VAT was actually paid at customs, so the entry is "
        "Dr 4426 = Cr 4462 and the debt is settled by payment;\n"
        "- a tax with two repartition lines (collected on 4427, deductible on 4426), such as "
        "'21% IMP AM' from l10n_ro_anaf_d300, means no VAT paid at customs (art. 326(4)-(5): "
        "deferral certificate, centralised clearance, entry in the declarant's records), so the "
        "entry is Dr 4426 = Cr 4427, with no payment and no debt to the budget.",
    )

    @api.onchange("line_ids")
    def _onchange_line_ids(self):
        if self.line_ids:
            self.custom_duty = sum(self.line_ids.mapped("custom_duty"))

    def _get_exempt_import_tax(self):
        """Taxa de achiziție scutită „0% EXEMPT” din planul RO (rd. 29 din D300, SAF-T 308302)."""
        return (
            self.env["account.chart.template"].ref("tvatiscdeda", raise_if_not_found=False) or self.env["account.tax"]
        )

    @api.onchange("customs_regime")
    def _onchange_customs_regime(self):
        if self.customs_regime == "4200":
            # TVA-ul calculat devine garanţie: se propune ca punct de plecare, de confruntat cu declaraţia
            self.vat_guarantee_amount = self.vat_guarantee_amount or self.tax_value
            self.tax_id = self._get_exempt_import_tax()
            self.tax_value = 0.0
        elif self.tax_id and self.tax_id == self._get_exempt_import_tax():
            # revenire de la 4200: se propune din nou TVA-ul de import calculat
            self.tax_id = self.env.company.account_purchase_tax_id
            tax_values = self.tax_id.compute_all(self.tax_base)
            self.tax_value = tax_values["total_included"] - tax_values["total_excluded"]
        if self.customs_regime != "4200":
            self.vat_guarantee_amount = 0.0

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
    def _get_or_create_custom_duty_product(self):
        """Produsul „Taxă vamală”, cu contul de cheltuieli completat pe compania curentă.

        Produsul e unul pe bază (`company_id` gol, id-ul în parametrul de sistem), dar
        `property_account_expense_id` e proprietate pe companie: se setează la creare doar pentru
        compania care l-a creat. Pe celelalte companii îl completăm la prima folosire, ca traseul
        nativ „factură furnizor -> landed cost” să nu cadă pe contul de cheltuieli al categoriei.
        """
        product = self.get_custom_duty_product()
        if not product:
            product = self.env["product.product"].create(self._prepare_custom_duty_product())
            self.env["ir.config_parameter"].sudo().set_param("dvi.custom_duty_product_id", product.id)
        template = product.product_tmpl_id.with_company(self.env.company)
        if not template.property_account_expense_id:
            account = self._get_customs_payable_account()
            if account:
                template.sudo().property_account_expense_id = account
        return product

    @api.model
    def _get_customs_account(self, product):
        """Contul creditat cu drepturile de import (taxa vamală, TVA-ul plătit în vamă).

        Se ia direct contul de decontare cu bugetul al companiei curente, nu proprietatea
        produsului: pe multi-company aceasta putea lipsi și nota se posta tăcut pe 607.
        Fără 446 în plan, rămâne contul de cheltuieli al produsului.
        """
        account = self._get_customs_payable_account()
        if not account:
            account = product.product_tmpl_id.with_company(self.env.company).get_product_accounts()["expense"]
        return account

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

    def _prepare_article_cost_lines(self):
        """O linie de cost pe articol, cu taxa vamală a articolului (și 0, ca produsele să-și primească codul NC)."""
        total = sum(self.line_ids.mapped("custom_duty"))
        if self.currency_id.compare_amounts(total, self.custom_duty):
            raise UserError(
                self.env._(
                    "The customs duty of the articles (%(articles)s) does not add up to the customs duty of the "
                    "declaration (%(total)s).",
                    articles=self.currency_id.format(total),
                    total=self.currency_id.format(self.custom_duty),
                )
            )
        product = self._get_or_create_custom_duty_product()
        account = self._get_customs_account(product)
        return [
            (
                0,
                0,
                {
                    "name": self.env._("%(product)s - art. %(number)s", product=product.name, number=line.number),
                    "product_id": product.id,
                    "price_unit": line.custom_duty,
                    "split_method": "by_current_cost_price",
                    "account_id": account.id,
                    "l10n_ro_dvi_taric_code": line.taric_code,
                },
            )
            for line in self.line_ids
        ]

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
            "customs_regime": self.customs_regime,
            "tax_id": self.tax_id.id,
            "tax_base": self.tax_base,
            "tax_value": self.tax_value,
            "customs_office_id": self.customs_office_id.id,
        }
        if self.customs_regime == "4200" and self.vat_guarantee_amount:
            values.update(vat_guarantee_amount=self.vat_guarantee_amount, vat_guarantee_state="blocked")
        # câmpul nativ „Factură furnizor”; domeniul lui admite doar facturi (nu note de credit)
        if invoice.move_type == "in_invoice":
            values["vendor_bill_id"] = invoice.id
        if self.line_ids:
            values["cost_lines"] += self._prepare_article_cost_lines()
        elif self.custom_duty:
            custom_duty_product = self._get_or_create_custom_duty_product()

            values["cost_lines"] += [
                (
                    0,
                    0,
                    {
                        "name": custom_duty_product.name,
                        "product_id": custom_duty_product.id,
                        "price_unit": self.custom_duty,
                        "split_method": "by_current_cost_price",
                        "account_id": self._get_customs_account(custom_duty_product).id,
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
