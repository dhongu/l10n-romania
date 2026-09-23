# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import fields, models


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

    tax_value = fields.Float("VAT paid at customs")
    tax_base = fields.Float("Tax base")
    tax_id = fields.Many2one("account.tax")  # TVA platit in Vama

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

        for cost in self.filtered(lambda c: c.tax_value and c.tax_id):
            accounts_data = custom_duty_product.product_tmpl_id.get_product_accounts()
            if not cost.account_move_id:
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

            name = self.env._("VAT paid at customs - %s", cost.tax_id.name)
            aml = [
                {
                    "name": name,
                    "debit": cost.tax_value,
                    "credit": 0.0,
                    "account_id": tax_values["taxes"][0]["account_id"],
                    "move_id": cost.account_move_id.id,
                    "tax_tag_ids": [(6, 0, tax_values["taxes"][0]["tag_ids"])],
                },
                {
                    "name": name,
                    "debit": 0.0,
                    "credit": cost.tax_value,
                    "account_id": accounts_data["expense"].id,
                    "move_id": cost.account_move_id.id,
                    # Fără tag de bază aici: linia poartă valoarea TVA, nu baza. Tag-ul de bază
                    # merge pe perechea tehnică de mai jos, de valoare `tax_base`.
                },
            ]
            aml += cost._prepare_tax_base_lines(name, tax_values)
            self.env["account.move.line"].create(aml)
        return res

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
        sau de stoc; doar una dintre linii poartă eticheta de bază.

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
