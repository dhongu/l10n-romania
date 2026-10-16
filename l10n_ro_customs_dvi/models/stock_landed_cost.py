# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import api, fields, models
from odoo.exceptions import ValidationError

# Regimul vamal din caseta 37 a declarației (primele 4 cifre: regim solicitat + regim anterior).
CUSTOMS_REGIMES = [
    ("4000", "4000 - Release for free circulation, import VAT due"),
    ("4200", "4200 - Release for free circulation, VAT exempt, followed by an intra-Community supply"),
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
    tax_base = fields.Float("Tax base")
    tax_id = fields.Many2one("account.tax")  # TVA la import (plătit în vamă sau cu certificat de amânare)

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

    def _get_move_ref(self):
        """Referința notei contabile: numărul de DVI dacă e completat, altfel secvența internă."""
        self.ensure_one()
        return self.dvi_number or self.name

    def button_validate(self):
        res = super().button_validate()

        # nota principală e creată în super() cu ref = name; o corectăm cu numărul de DVI
        for cost in self.filtered(lambda c: c.dvi_number and c.account_move_id):
            cost.account_move_id.ref = cost.dvi_number

        get_param = self.env["ir.config_parameter"].sudo().get_param

        product_id = get_param("dvi.custom_duty_product_id")

        custom_duty_product = self.env["product.product"].browse(int(product_id)).exists()

        if not custom_duty_product:
            wizard = self.env["account.invoice.dvi"].create({})
            vals = wizard._prepare_custom_duty_product()
            custom_duty_product = self.env["product.product"].create(vals)
            set_param = self.env["ir.config_parameter"].sudo().set_param
            set_param("dvi.custom_duty_product_id", custom_duty_product.id)

        # La 4200 nu există TVA, dar baza importului scutit trebuie să ajungă în decont (rd. 29).
        for cost in self.filtered(lambda c: c.tax_id and (c.tax_value or c.customs_regime == "4200")):
            accounts_data = custom_duty_product.product_tmpl_id.get_product_accounts()
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
            aml = cost._prepare_tax_lines(name, tax_values, accounts_data)
            aml += cost._prepare_tax_base_lines(name, tax_values)
            # Liniile sunt complete (TVA transcris din declaraţie): fără resincronizarea taxelor,
            # care pe o notă în ciornă ar recalcula TVA-ul din bază.
            self.env["account.move.line"].with_context(skip_invoice_sync=True).create(aml)
            if new_move and cost.account_move_id.line_ids:
                cost.account_move_id._post()
        return res

    def _prepare_tax_lines(self, name, tax_values, accounts_data):
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
                    "account_id": accounts_data["expense"].id,
                    "move_id": self.account_move_id.id,
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
