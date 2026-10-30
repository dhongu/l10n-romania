# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from markupsafe import Markup

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round

# Regimul vamal din caseta 37 a declarației (primele 4 cifre: regim solicitat + regim anterior).
CUSTOMS_REGIMES = [
    ("4000", "4000 - Import VAT due"),
    ("4200", "4200 - VAT exempt, intra-Community supply"),
    ("other", "Other"),
]


class LandedCost(models.Model):
    _inherit = "stock.landed.cost"

    landed_type = fields.Selection([("standard", "Standard"), ("dvi", "DVI")], default="standard")

    # numărul declarației vamale de import (MRN), preluat din documentul emis de vamă
    dvi_number = fields.Char(
        "DVI Number",
        copy=False,
        index=True,
        tracking=True,
        help="Reference number of the customs import declaration (MRN).",
    )

    customs_regime = fields.Selection(
        CUSTOMS_REGIMES,
        default="4000",
        tracking=True,
        help="Customs procedure code (box 37 of the declaration).\n"
        "4200: the import is exempt from VAT (art. 293(1)(m) of Law 227/2015) because the goods are "
        "supplied to another Member State; only the base is reported, on row 29 of the VAT return.",
    )
    tax_value = fields.Float("Import VAT Amount")
    # Regim 4200: TVA-ul calculat de vamă e reţinut din contul de garanţie al importatorului până
    # la proba livrării intracomunitare (CMR confirmat). Evidenţă informativă, fără notă contabilă:
    # garanţia stă pe 2678, iar notele de constituire / restituire / executare se fac manual.
    vat_guarantee_amount = fields.Float(
        "VAT Held as Guarantee",
        tracking=True,
        help="Regime 4200: VAT computed by customs and held from the importer's guarantee account until "
        "the intra-Community supply is proven (CMR confirmed by the customer). Informative only: "
        "no journal entry is generated.",
    )
    vat_guarantee_state = fields.Selection(
        [("blocked", "Blocked"), ("released", "Released")],
        "Guarantee Status",
        tracking=True,
        help="Blocked: customs holds the amount from the guarantee account.\n"
        "Released: customs released it after the confirmed CMR was submitted.",
    )
    tax_base = fields.Float("Tax base")
    tax_id = fields.Many2one("account.tax")  # TVA la import (plătit în vamă sau cu certificat de amânare)

    # Biroul vamal e creditorul drepturilor de import: partenerul liniilor de decontare cu bugetul (446),
    # ca plata din extras să se potrivească cu el, iar DVI-urile şi soldul să se vadă pe contactul lui.
    customs_office_id = fields.Many2one(
        "res.partner",
        "Customs Office",
        tracking=True,
        index="btree_not_null",
        domain=[("l10n_ro_customs_office_code", "!=", False)],
        help="Customs office where the declaration was lodged. It is the partner of the customs duty and "
        "import VAT due on account 446, so that the payment to the Treasury is reconciled with the DVI.",
    )
    customs_amount_due = fields.Monetary(
        "Amount Due at Customs",
        compute="_compute_customs_payment",
        store=True,
        help="Customs duty and import VAT on account 446 not yet reconciled with a payment.",
    )
    customs_payment_state = fields.Selection(
        [("not_paid", "Not Paid"), ("partial", "Partially Paid"), ("paid", "Paid")],
        "Customs Payment",
        compute="_compute_customs_payment",
        store=True,
        help="Payment of the amounts due at customs, from the reconciliation of account 446. Empty when "
        "nothing is due at customs (VAT deferral certificate, regime 4200, no customs duty).",
    )

    def _get_customs_payable_account(self):
        self.ensure_one()
        return self.env["account.invoice.dvi"].with_company(self.company_id)._get_customs_payable_account()

    def _get_customs_payable_lines(self):
        self.ensure_one()
        if not self.account_move_id:
            return self.env["account.move.line"]
        account = self._get_customs_payable_account()
        return self.account_move_id.line_ids.filtered(lambda line: line.account_id == account and line.credit)

    @api.depends("account_move_id.line_ids.amount_residual", "account_move_id.line_ids.account_id")
    def _compute_customs_payment(self):
        for cost in self:
            lines = cost._get_customs_payable_lines() if cost.landed_type == "dvi" else False
            if not lines:
                cost.customs_amount_due = 0.0
                cost.customs_payment_state = False
                continue
            due = -sum(lines.mapped("amount_residual"))
            cost.customs_amount_due = due
            if cost.currency_id.is_zero(due):
                cost.customs_payment_state = "paid"
            elif cost.currency_id.compare_amounts(due, sum(lines.mapped("credit"))) < 0:
                cost.customs_payment_state = "partial"
            else:
                cost.customs_payment_state = "not_paid"

    @api.constrains("customs_regime", "tax_id", "tax_value")
    def _check_customs_regime_exempt(self):
        """La 4200 importul e scutit: nu există TVA de înregistrat, nici deductibil, nici de plată.

        TVA-ul calculat de vamă și reținut ca garanție nu e datorat; dacă scutirea cade, vama îl
        execută din garanție și abia atunci devine TVA de import.
        """
        for cost in self.filtered(lambda c: c.customs_regime == "4200"):
            if cost.tax_value or (cost.tax_id and cost.tax_id.amount):
                raise ValidationError(
                    self.env._(
                        "Under customs regime 4200 the import is exempt from VAT: choose an exempt tax "
                        "(0%) and leave the import VAT amount empty. The VAT held by customs as a "
                        "guarantee is not recorded on the DVI."
                    )
                )

    def action_release_vat_guarantee(self):
        self.write({"vat_guarantee_state": "released"})

    def _get_move_ref(self):
        """Referința notei contabile: numărul de DVI dacă e completat, altfel secvența internă."""
        self.ensure_one()
        return self.dvi_number or self.name

    def compute_landed_cost(self):
        res = super().compute_landed_cost()
        self.filtered(lambda c: c.landed_type == "dvi")._split_cost_by_article()
        return res

    def _get_article_cost_lines(self):
        self.ensure_one()
        return self.cost_lines.filtered("l10n_ro_dvi_taric_code")

    def _split_cost_by_article(self):
        """Taxa vamală a fiecărui articol din DVI merge doar pe produsele articolului.

        Calculul nativ repartizează fiecare linie de cost pe toate produsele recepționate. Taxa vamală
        diferă însă pe cod tarifar: un articol cu cotă 0% nu primește nimic din taxa altui articol. Liniile
        de ajustare native rămân; se refac doar sumele liniilor de articol, cu metoda de repartizare a
        fiecărei linii, aplicată numai pe produsele ei.
        """
        weight_fields = {"by_quantity": "quantity", "by_weight": "weight", "by_volume": "volume"}
        for cost in self:
            currency = cost.currency_id
            for cost_line in cost._get_article_cost_lines():
                adjustments = cost.valuation_adjustment_lines.filtered(lambda a, line=cost_line: a.cost_line_id == line)
                targets = adjustments.filtered(lambda a, line=cost_line: a.product_id in line.l10n_ro_dvi_product_ids)
                if not targets and not currency.is_zero(cost_line.price_unit):
                    without_code = adjustments.product_id.filtered(lambda p: not p._l10n_ro_customs_nc_code())
                    raise UserError(
                        self.env._(
                            "The customs duty of %(article)s (TARIC %(taric)s, %(amount)s) cannot be split: no "
                            "received product matches it.\n\nChoose the products of the article on its line, in "
                            "the Additional Costs tab, or set the commodity code on the product.%(products)s",
                            article=cost_line.name,
                            taric=cost_line.l10n_ro_dvi_taric_code,
                            amount=currency.format(cost_line.price_unit),
                            products=without_code
                            and "\n\n"
                            + self.env._("Received products without commodity code:")
                            + "".join(f"\n- {name}" for name in without_code.mapped("display_name"))
                            or "",
                        )
                    )
                field_name = weight_fields.get(cost_line.split_method)
                if cost_line.split_method == "by_current_cost_price":
                    weights = targets.mapped("former_cost")
                elif field_name:
                    weights = targets.mapped(field_name)
                else:
                    weights = [1.0] * len(targets)
                if not sum(weights):
                    weights = [1.0] * len(targets)
                total_weight = sum(weights)
                values = {adjustment: 0.0 for adjustment in adjustments}
                remaining = cost_line.price_unit
                for adjustment, weight in zip(targets, weights, strict=True):
                    value = float_round(
                        cost_line.price_unit * weight / total_weight, precision_rounding=currency.rounding
                    )
                    values[adjustment] = value
                    remaining -= value
                if targets and not currency.is_zero(remaining):
                    values[targets[-1]] += currency.round(remaining)
                for adjustment, value in values.items():
                    adjustment.additional_landed_cost = value

    def _propagate_article_nc_codes(self):
        """Codul NC din DVI pe produsele articolului care nu au niciunul (câmpul nativ, completat o dată)."""
        for cost in self:
            updated = []
            for cost_line in cost._get_article_cost_lines():
                for product in cost_line.l10n_ro_dvi_product_ids:
                    if product._l10n_ro_customs_set_nc_code(cost_line.l10n_ro_dvi_nc_code):
                        updated.append((product, cost_line.l10n_ro_dvi_nc_code))
            if updated:
                cost.message_post(
                    body=Markup("<p>%s</p><ul>%s</ul>")
                    % (
                        self.env._("Commodity code set from the DVI:"),
                        Markup().join(
                            Markup("<li>%s → %s</li>") % (product.display_name, code) for product, code in updated
                        ),
                    )
                )

    def _log_on_customs_office(self):
        for cost in self.filtered(lambda c: c.landed_type == "dvi" and c.customs_office_id):
            cost.customs_office_id._message_log(
                body=Markup("<p>%s</p>")
                % self.env._(
                    "DVI %(dvi)s posted: MRN %(mrn)s, customs duty %(duty)s, import VAT %(vat)s.",
                    dvi=cost._get_html_link(),
                    mrn=cost.dvi_number or "-",
                    duty=cost.currency_id.format(cost.amount_total),
                    vat=cost.currency_id.format(cost.tax_value),
                )
            )

    def button_validate(self):
        # La validare se reface repartizarea pe articole: produsele unui articol se pot schimba după calcul.
        for cost in self.filtered(lambda c: c.landed_type == "dvi" and c._get_article_cost_lines()):
            if not cost.valuation_adjustment_lines:
                cost.compute_landed_cost()
            else:
                cost._split_cost_by_article()
        res = super().button_validate()

        # nota principală e creată în super() cu ref = name; o corectăm cu numărul de DVI
        for cost in self.filtered(lambda c: c.dvi_number and c.account_move_id):
            cost.account_move_id.ref = cost.dvi_number

        # La 4200 nu există TVA, dar baza importului scutit trebuie să ajungă în decont (rd. 29).
        for cost in self.filtered(lambda c: c.tax_id and (c.tax_value or c.customs_regime == "4200")):
            # Contul de buget al companiei DVI-ului, nu proprietatea produsului „Taxă vamală”
            # (setată doar pe compania care l-a creat; pe celelalte nota cădea tăcut pe 607).
            dvi_wizard = self.env["account.invoice.dvi"].with_company(cost.company_id)
            custom_duty_product = dvi_wizard._get_or_create_custom_duty_product()
            payable_account = dvi_wizard._get_customs_account(custom_duty_product)
            # Fără taxă vamală (ex. preferința UE–MD), super() nu creează nicio notă: o creăm aici
            # și o validăm la final, altfel TVA-ul / baza din DVI rămân într-o notă în ciornă,
            # pe care decontul nu o vede.
            new_move = not cost.account_move_id
            if new_move:
                cost.account_move_id = self.env["account.move"].create(
                    {
                        "journal_id": cost.account_journal_id.id,
                        "date": cost.date,
                        "ref": cost._get_move_ref(),
                        "line_ids": [],
                        "move_type": "entry",
                    }
                )
            tax_values = cost.tax_id.compute_all(cost.tax_base)

            # etichetă neutră: regimul (plătit în vamă / fără plată, „IMP AM") se vede din numele taxei
            name = self.env._("Import VAT - %s", cost.tax_id.name)
            aml = cost._prepare_tax_lines(name, tax_values, payable_account)
            aml += cost._prepare_tax_base_lines(name, tax_values)
            # Liniile sunt complete (TVA transcris din declaraţie): fără resincronizarea taxelor,
            # care pe o notă în ciornă ar recalcula TVA-ul din bază.
            self.env["account.move.line"].with_context(skip_invoice_sync=True).create(aml)
            if new_move and cost.account_move_id.line_ids:
                cost.account_move_id._post()
        self._set_dvi_move_partner()
        self._set_dvi_move_document_type()
        self.filtered(lambda c: c.landed_type == "dvi")._propagate_article_nc_codes()
        self._log_on_customs_office()
        return res

    def _set_dvi_move_document_type(self):
        """DVI-ul e documentul justificativ al notei (TVA la import, taxe vamale), nu o notă contabilă."""
        moves = self.filtered(lambda c: c.landed_type == "dvi").account_move_id
        moves.write({"l10n_ro_document_type": "customs_declaration"})

    def _set_dvi_move_partner(self):
        """Furnizorul extern de pe factură, pe antetul notei DVI.

        Jurnalul de TVA pentru cumpărări înscrie importul pe nota DVI și ia furnizorul din antetul
        ei; fără partener, rândul importului rămânea fără nume și CUI. Doar antetul: liniile de
        TVA și de taxe vamale (446, 4426, 4427) își păstrează partenerul. Poziția fiscală rămâne cea
        a notei: recalculată din furnizorul extern, ar fi una extra-UE, incompatibilă cu taxa de
        import din țară.
        """
        for cost in self.filtered(lambda c: c.vendor_bill_id and c.account_move_id):
            move = cost.account_move_id
            if not move.partner_id:
                with self.env.protecting([move._fields["fiscal_position_id"]], move):
                    move.with_context(skip_readonly_check=True).partner_id = cost.vendor_bill_id.commercial_partner_id

    def _prepare_tax_lines(self, name, tax_values, payable_account):
        """Liniile de TVA ale notei, urmând liniile de repartiţie ale taxei alese.

        Taxa **este** comutatorul între cele două regimuri de la art. 326 Cod fiscal, fiindcă
        repartiţia ei descrie exact tratamentul:

        * **plata efectivă în vamă** (art. 326 alin. (3)) — taxă obişnuită de achiziţie, cu o
          singură linie de repartiţie, pe 4426. Contrapartida e datoria faţă de buget:
          ``Dr 4426 = Cr 4462``, stinsă ulterior prin plată;

        * **fără plata efectivă în vamă** (art. 326 alin. (4)-(5)) — taxă colectată și deductibilă, cu două
          linii de repartiţie, pe 4426 şi 4427. Cele două se soldează între ele, iar taxa se
          evidenţiază în decont atât ca taxă deductibilă, cât şi ca taxă colectată:
          ``Dr 4426 = Cr 4427``, **fără 446 şi fără plată**.

        Nu există niciun câmp de configurare: operatorul alege în wizard taxa care corespunde
        regimului societăţii. Contrapartida pe contul de buget se adaugă doar când repartiţia are
        o singură linie — cu două linii (4426 și 4427) ar dezechilibra nota.

        Sumele urmează `tax_value`, transcris din declaraţie, nu recalculat; din repartiţie se
        preiau contul, eticheta fiscală şi semnul.

        Fiecare linie e legată de repartiţia ei (`tax_repartition_line_id`, deci şi `tax_line_id`):
        fără legătură, SAF-T (D406) nu găseşte taxa şi raportează 000 / 000000, iar închiderea
        TVA nu preia linia.
        """
        self.ensure_one()
        reps = [r for r in tax_values["taxes"] if r.get("account_id")]
        if not reps:
            return []

        lines = []
        for r in reps:
            semn = -1.0 if r["amount"] < 0 else 1.0
            suma = self.tax_value * semn
            lines.append(
                {
                    "name": name,
                    "debit": suma if suma > 0 else 0.0,
                    "credit": -suma if suma < 0 else 0.0,
                    "account_id": r["account_id"],
                    "move_id": self.account_move_id.id,
                    "tax_repartition_line_id": r["tax_repartition_line_id"],
                    "tax_base_amount": self.tax_base,
                    "tax_tag_ids": [(6, 0, r["tag_ids"])],
                }
            )

        if len(reps) == 1:
            # Fără tag de bază aici: linia poartă valoarea TVA, nu baza. Eticheta de bază merge
            # pe perechea tehnică din `_prepare_tax_base_lines`, de valoare `tax_base`.
            lines.append(
                {
                    "name": name,
                    "debit": 0.0,
                    "credit": self.tax_value,
                    "account_id": payable_account.id,
                    "move_id": self.account_move_id.id,
                    "partner_id": self.customs_office_id.id,
                }
            )
        return lines

    def _get_base_clearing_account(self):
        """Contul neutru pe care se poartă perechea tehnică de bază pentru decont."""
        self.ensure_one()
        return self.env["account.account"].search(
            [("code", "=like", "473%"), ("company_ids", "in", [self.company_id.id])],
            order="code",
            limit=1,
        )

    def _prepare_tax_base_lines(self, name, tax_values):
        """Pereche tehnică echilibrată care duce BAZA importului în decontul de TVA.

        Nota de TVA vamal purta eticheta fiscală doar pe linia de taxă (4426). Rândul din
        raportul de TVA — și, mai departe, din D300 — are însă şi expresie de bază, şi
        expresie de taxă: fără eticheta de bază, rândul iese cu TVA şi cu bază zero, iar
        totalul bazei achiziţiilor rămâne subevaluat.

        Baza nu poate fi purtată de nicio linie existentă: ambele au ca valoare TVA-ul, nu
        baza. De aceea se adaugă o pereche debit/credit de valoare `tax_base` pe un cont
        neutru de clarificare (473), care se soldează şi nu atinge niciun cont de rezultat
        sau de stoc; doar una dintre linii poartă eticheta de bază şi taxa (`tax_ids`) — pe ea
        pune SAF-T (D406) informaţia de taxă, ca pe linia de bază a unei facturi.

        Fără cont 473 în plan sau fără etichete de bază pe taxă, nu se adaugă nimic —
        comportamentul rămâne cel dinainte.
        """
        self.ensure_one()
        base_tags = tax_values.get("base_tags")
        account = self._get_base_clearing_account()
        if not base_tags or not account or not self.tax_base:
            return []
        base_name = self.env._("Import VAT base - %s", self.tax_id.name)
        return [
            {
                "name": base_name,
                "debit": self.tax_base,
                "credit": 0.0,
                "account_id": account.id,
                "move_id": self.account_move_id.id,
                "tax_ids": [(6, 0, self.tax_id.ids)],
                "tax_tag_ids": [(6, 0, base_tags)],
            },
            {
                "name": base_name,
                "debit": 0.0,
                "credit": self.tax_base,
                "account_id": account.id,
                "move_id": self.account_move_id.id,
            },
        ]

    def _check_sum(self):
        res = super()._check_sum()
        if not res:
            # prec_digits = self.env.company.currency_id.decimal_places
            for landed_cost in self:
                total_amount = sum(landed_cost.valuation_adjustment_lines.mapped("additional_landed_cost"))
                if abs(total_amount - landed_cost.amount_total) > 1:
                    return False

            res = True

            # val_to_cost_lines = defaultdict(lambda: 0.0)
            # for val_line in landed_cost.valuation_adjustment_lines:
            #     val_to_cost_lines[val_line.cost_line_id] += val_line.additional_landed_cost
            # if any(not tools.float_is_zero(cost_line.price_unit - val_amount, precision_digits=prec_digits)
            #        for cost_line, val_amount in val_to_cost_lines.items()):
            #     return False
        return res


class LandedCostLine(models.Model):
    _inherit = "stock.landed.cost.lines"

    # Un articol din DVI = o linie de cost: taxa vamală a articolului, repartizată doar pe produsele lui.
    l10n_ro_dvi_taric_code = fields.Char(
        "TARIC Code",
        help="TARIC code of the article of the customs declaration. The customs duty of the line is split "
        "only on the products of the article.",
    )
    l10n_ro_dvi_nc_code = fields.Char(
        "NC Code",
        compute="_compute_l10n_ro_dvi_nc_code",
        store=True,
        help="Combined Nomenclature code: the first eight digits of the TARIC code.",
    )
    l10n_ro_dvi_product_ids = fields.Many2many(
        "product.product",
        "l10n_ro_dvi_cost_line_product_rel",
        "cost_line_id",
        "product_id",
        string="Products",
        compute="_compute_l10n_ro_dvi_product_ids",
        store=True,
        readonly=False,
        help="Received products of the article, proposed from their commodity code. A product without "
        "commodity code can be chosen by hand: it gets the code of the article when the DVI is posted.",
    )

    @api.depends("l10n_ro_dvi_taric_code")
    def _compute_l10n_ro_dvi_nc_code(self):
        for line in self:
            line.l10n_ro_dvi_nc_code = (line.l10n_ro_dvi_taric_code or "")[:8] or False

    @api.depends("l10n_ro_dvi_taric_code", "cost_id.picking_ids")
    def _compute_l10n_ro_dvi_product_ids(self):
        for line in self:
            if not line.l10n_ro_dvi_taric_code:
                line.l10n_ro_dvi_product_ids = False
                continue
            products = line.cost_id._get_targeted_move_ids().product_id
            line.l10n_ro_dvi_product_ids = products.filtered(
                lambda p, taric=line.l10n_ro_dvi_taric_code: p._l10n_ro_customs_matches_taric(taric)
            )


class StockValuationAdjustmentLines(models.Model):
    _inherit = "stock.valuation.adjustment.lines"

    def _create_accounting_entries(self, remaining_qty):
        # Produsele altui articol primesc 0 din taxa articolului: fără linii contabile de zero.
        if self.cost_id.landed_type == "dvi" and self.currency_id.is_zero(self.additional_landed_cost):
            return []
        return super()._create_accounting_entries(remaining_qty)

    def _create_account_move_line(self, credit_account_id, debit_account_id, remaining_qty):
        """Biroul vamal ca partener pe linia de taxă vamală datorată (446)."""
        lines = super()._create_account_move_line(credit_account_id, debit_account_id, remaining_qty)
        office = self.cost_id.customs_office_id
        if self.cost_id.landed_type == "dvi" and office:
            for command in lines:
                if command[2].get("account_id") == credit_account_id:
                    command[2]["partner_id"] = office.id
        return lines
