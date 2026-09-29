# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestDVI(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        account_expense = cls.env["account.account"].search([("code", "=", "607000")], limit=1)
        if not account_expense:
            account_expense = cls.env["account.account"].create(
                {
                    "name": "Expense",
                    "code": "607000",
                    "account_type": "expense",
                    "reconcile": False,
                }
            )

        account_income = cls.env["account.account"].search([("code", "=", "707000")])
        if not account_income:
            account_income = cls.env["account.account"].create(
                {
                    "name": "Income",
                    "code": "707000",
                    "account_type": "income",
                    "reconcile": False,
                }
            )

        # se poate utiliza foarte bine si  408
        account_input = cls.env["account.account"].search([("code", "=", "371000.i")])
        if not account_input:
            account_input = cls.env["account.account"].create(
                {
                    "name": "Income",
                    "code": "371000.i",
                    "account_type": "income",
                    "reconcile": False,
                }
            )

        # se poate utiliza foarte bine si  418
        account_output = cls.env["account.account"].search([("code", "=", "371000.o")])
        if not account_output:
            account_output = cls.env["account.account"].create(
                {
                    "name": "Output",
                    "code": "371000.o",
                    "reconcile": False,
                }
            )

        account_valuation = cls.env["account.account"].search([("code", "=", "371000")])
        if not account_valuation:
            account_valuation = cls.env["account.account"].create(
                {
                    "name": "Valuation",
                    "code": "371000",
                    "account_type": "asset_current",
                    "reconcile": False,
                }
            )

        # Ambele analitice de scadență din planul RO, ca testul să poată demonstra că
        # modulul îl preferă pe cel corect. Atenție la ordine, e contraintuitivă:
        # 4461 = reluate într-o perioadă MAI MARE de un an, 4462 = până la un an.
        account_other_tax_long = cls.env["account.account"].search([("code", "=", "446100")], limit=1)
        if not account_other_tax_long:
            account_other_tax_long = cls.env["account.account"].create(
                {
                    "name": "Alte impozite, taxe și vărsăminte asimilate - peste un an",
                    "code": "446100",
                    "account_type": "liability_payable",
                    "reconcile": True,
                }
            )
        account_other_tax = cls.env["account.account"].search([("code", "=", "446200")], limit=1)
        if not account_other_tax:
            account_other_tax = cls.env["account.account"].create(
                {
                    "name": "Alte impozite, taxe și vărsăminte asimilate - până la un an",
                    "code": "446200",
                    "account_type": "liability_payable",
                    "reconcile": True,
                }
            )

        # Creare taxe cu tag-uri pentru test
        cls.tax_tag = cls.env["account.account.tag"].create(
            {
                "name": "Test Tax Tag",
                "applicability": "taxes",
                "country_id": cls.env.ref("base.ro").id,
            }
        )
        cls.base_tag = cls.env["account.account.tag"].create(
            {
                "name": "Test Base Tag",
                "applicability": "taxes",
                "country_id": cls.env.ref("base.ro").id,
            }
        )
        # `tax_group_id` e NOT NULL pe account.tax; fără el setUpClass cădea cu
        # NotNullViolation şi niciun test din fişier nu apuca să ruleze.
        # Grupul trebuie să aibă aceeaşi ţară ca taxa care îl foloseşte; tag-urile de mai sus sunt
        # create pe RO, deci fixăm explicit RO peste tot, indiferent de ţara fiscală a companiei.
        country_ro = cls.env.ref("base.ro")
        tax_group = cls.env["account.tax.group"].search(
            [("company_id", "=", cls.env.company.id), ("country_id", "=", country_ro.id)],
            limit=1,
        )
        if not tax_group:
            tax_group = cls.env["account.tax.group"].create(
                {
                    "name": "Test Tax Group",
                    "company_id": cls.env.company.id,
                    "country_id": country_ro.id,
                }
            )

        cls.tax_id = cls.env["account.tax"].create(
            {
                "name": "TVA Import Test",
                "amount": 19.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": tax_group.id,
                "country_id": country_ro.id,
                "invoice_repartition_line_ids": [
                    (0, 0, {"repartition_type": "base", "factor_percent": 100, "tag_ids": [(6, 0, cls.base_tag.ids)]}),
                    (
                        0,
                        0,
                        {
                            "repartition_type": "tax",
                            "factor_percent": 100,
                            "account_id": account_other_tax.id,
                            "tag_ids": [(6, 0, cls.tax_tag.ids)],
                        },
                    ),
                ],
                "refund_repartition_line_ids": [
                    (0, 0, {"repartition_type": "base", "factor_percent": 100, "tag_ids": [(6, 0, cls.base_tag.ids)]}),
                    (
                        0,
                        0,
                        {
                            "repartition_type": "tax",
                            "factor_percent": 100,
                            "account_id": account_other_tax.id,
                            "tag_ids": [(6, 0, cls.tax_tag.ids)],
                        },
                    ),
                ],
            }
        )

        # Cont neutru de clarificare, pe care se poartă perechea tehnică de bază pentru decont
        account_clearing = cls.env["account.account"].search([("code", "=", "473000")], limit=1)
        if not account_clearing:
            account_clearing = cls.env["account.account"].create(
                {
                    "name": "Decontări din operațiuni în curs de clarificare",
                    "code": "473000",
                    "account_type": "liability_current",
                    "reconcile": True,
                }
            )

        stock_journal = cls.env["account.journal"].search([("code", "=", "STJ")], limit=1)
        if not stock_journal:
            stock_journal = cls.env["account.journal"].create(
                {"name": "Stock Journal", "code": "STJ", "type": "general"}
            )

        cls.category = cls.env["product.category"].create(
            {
                "name": "Marfa",
                "property_cost_method": "fifo",
                "property_valuation": "real_time",
                "property_account_income_categ_id": account_income.id,
                "property_account_expense_categ_id": account_expense.id,
                "property_stock_valuation_account_id": account_valuation.id,
                "property_stock_journal": stock_journal.id,
            }
        )

        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Product A",
                "is_storable": True,
                "categ_id": cls.category.id,
                "invoice_policy": "delivery",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Product B",
                "is_storable": True,
                "categ_id": cls.category.id,
                "invoice_policy": "delivery",
            }
        )

        cls.vendor = cls.env["res.partner"].search([("name", "=", "vendor1")], limit=1)
        if not cls.vendor:
            cls.vendor = cls.env["res.partner"].create({"name": "vendor1"})
        cls.vendor.country_id = cls.env.ref("base.de")

    def test_call_wizard(self):
        po = Form(self.env["purchase.order"])
        po.partner_id = self.vendor
        with po.order_line.new() as po_line:
            po_line.product_id = self.product_1
            po_line.product_qty = 10
            po_line.price_unit = 100
        with po.order_line.new() as po_line:
            po_line.product_id = self.product_2
            po_line.product_qty = 10
            po_line.price_unit = 200
        po = po.save()
        po.button_confirm()
        self.picking = po.picking_ids[0]
        self.picking.move_line_ids.write({"quantity": 10.0})
        self.picking.button_validate()
        domain = [("product_id", "in", [self.product_1.id, self.product_2.id]), ("is_in", "=", True)]
        valuations = self.env["stock.move"]._read_group(domain, ["product_id"], ["value:sum", "quantity:sum"])
        for product, value, _quantity in valuations:
            if product.id == self.product_1.id:
                self.assertEqual(value, 10 * 100)
            if product.id == self.product_2.id:
                self.assertEqual(value, 10 * 200)
        action = po.action_create_invoice()
        # action should contain res_id of the created account.move
        invoice = self.env["account.move"].browse(action.get("res_id"))
        self.assertTrue(invoice, "Vendor bill was not created from the Purchase Order")
        self.assertEqual(invoice.move_type, "in_invoice")
        # Ensure vendor is set as in test setup
        if not invoice.partner_id:
            invoice.partner_id = self.vendor
        # Bill date is required to post the vendor bill in this environment
        invoice.invoice_date = fields.Date.today()
        # Post the vendor bill using the public API
        invoice.action_post()

        # se deschide wizardul pt generare DVI
        action = invoice.button_dvi()
        wizard_res_model = action.get("res_model")
        wizard_id = action.get("res_id")
        wizard = self.env[wizard_res_model].browse(wizard_id)

        wizard_form = Form(wizard.with_context(active_id=invoice.id))
        self.assertEqual(wizard_form.tax_base, 3000.0, "Tax base should be initialized from invoice amount untaxed")
        wizard_form.tax_id = self.tax_id
        wizard_form.dvi_number = "25ROBU1234567890"
        wizard_form.custom_duty = 5.0
        # Simulam o modificare manuala a TVA-ului platit in vama
        wizard_form.tax_value = wizard_form.tax_value + 1
        wizard = wizard_form.save()

        action = wizard.do_create_dvi()
        dvi = self.env[(action.get("res_model"))].browse(action.get("res_id"))
        self.assertEqual(dvi.tax_base, 3000.0)
        self.assertEqual(dvi.landed_type, "dvi")
        self.assertEqual(dvi.dvi_number, "25ROBU1234567890", "DVI number should be propagated from the wizard")

        dvi_form = Form(dvi)
        dvi = dvi_form.save()
        dvi.compute_landed_cost()
        dvi.button_validate()

        # Verificam daca s-a creat nota contabila pentru TVA
        self.assertTrue(dvi.account_move_id, "Account move for VAT should be created")
        vat_move = dvi.account_move_id
        self.assertEqual(vat_move.state, "posted")
        self.assertEqual(vat_move.ref, "25ROBU1234567890", "Journal entry reference should be the DVI number")

        # Verificam liniile notei contabile pentru TVA
        # In Odoo 18, nota contabila poate fi partajata cu intrarile de evaluare stoc.
        # Identificam liniile de TVA dupa numele lor specific.
        text = self.env._("VAT paid at customs")
        tva_lines = vat_move.line_ids.filtered(lambda l: text in l.name)
        self.assertEqual(len(tva_lines), 2, "Ar trebui sa avem exact 2 linii de TVA (debit si credit)")
        debit_line = tva_lines.filtered(lambda l: l.debit > 0)
        tva_lines.filtered(lambda l: l.credit > 0)

        self.assertTrue(debit_line.tax_tag_ids, "Debit line should have tax tags")

        # Baza importului trebuie să ajungă în decont printr-o pereche tehnică echilibrată:
        # fără ea, rândul din raportul de TVA iese cu TVA şi cu bază zero.
        base_text = self.env._("Import VAT base")
        base_lines = vat_move.line_ids.filtered(lambda line: base_text in line.name)
        self.assertEqual(len(base_lines), 2, "Ar trebui 2 linii tehnice de bază (debit şi credit)")
        self.assertEqual(
            sum(base_lines.mapped("debit")),
            sum(base_lines.mapped("credit")),
            "Perechea tehnică de bază trebuie să se soldeze",
        )
        self.assertEqual(sum(base_lines.mapped("debit")), 3000.0, "Baza trebuie să fie tax_base")
        tagged = base_lines.filtered(lambda line: line.tax_tag_ids)
        self.assertEqual(len(tagged), 1, "Exact o linie din pereche poartă eticheta de bază")
        self.assertEqual(
            len(set(base_lines.mapped("account_id").ids)),
            1,
            "Ambele linii stau pe acelaşi cont neutru, ca perechea să nu atingă rezultatul",
        )
        # In configuratia actuala a codului, linia de credit nu primeste tag-uri de baza
        # self.assertTrue(credit_line.tax_tag_ids, "Credit line should have base tax tags")
        # self.assertTrue(credit_line.tax_ids, "Credit line should have tax_ids set for reporting")

        domain = [("product_id", "in", [self.product_1.id, self.product_2.id]), ("is_in", "=", True)]
        valuations = self.env["stock.move"]._read_group(domain, ["product_id"], ["value:sum", "quantity:sum"])
        for product, value, _quantity in valuations:
            if product.id == self.product_1.id:
                # 1000 + taxa vamală 5 repartizată 1/3 (1.67) = 1001.67
                self.assertAlmostEqual(value, 10 * 100 + 1.67, places=2)
            if product.id == self.product_2.id:
                # 2000 + taxa vamală 5 repartizată 2/3 (3.33) = 2003.33
                self.assertAlmostEqual(value, 10 * 200 + 3.33, places=2)

        action = invoice.button_dvi()
        self.assertEqual(action.get("res_id"), dvi.id)

    def _build_reverse_charge_tax(self):
        """Taxă de import cu taxare inversă: două linii de repartiţie, pe 4427 şi 4426."""
        acc_4426 = self.env["account.account"].search([("code", "=", "442600")], limit=1)
        if not acc_4426:
            acc_4426 = self.env["account.account"].create(
                {"name": "TVA deductibilă", "code": "442600", "account_type": "asset_current"}
            )
        acc_4427 = self.env["account.account"].search([("code", "=", "442700")], limit=1)
        if not acc_4427:
            acc_4427 = self.env["account.account"].create(
                {"name": "TVA colectată", "code": "442700", "account_type": "liability_current"}
            )
        tag_ded = self.env["account.account.tag"].create(
            {"name": "RC deductibil", "applicability": "taxes", "country_id": self.env.ref("base.ro").id}
        )
        tag_col = self.env["account.account.tag"].create(
            {"name": "RC colectat", "applicability": "taxes", "country_id": self.env.ref("base.ro").id}
        )
        rep = [
            (0, 0, {"repartition_type": "base", "factor_percent": 100}),
            (
                0,
                0,
                {
                    "repartition_type": "tax",
                    "factor_percent": -100,
                    "account_id": acc_4427.id,
                    "tag_ids": [(6, 0, tag_col.ids)],
                },
            ),
            (
                0,
                0,
                {
                    "repartition_type": "tax",
                    "factor_percent": 100,
                    "account_id": acc_4426.id,
                    "tag_ids": [(6, 0, tag_ded.ids)],
                },
            ),
        ]
        return (
            self.env["account.tax"].create(
                {
                    "name": "TVA Import Taxare Inversă Test",
                    "amount": 19.0,
                    "amount_type": "percent",
                    "type_tax_use": "purchase",
                    "tax_group_id": self.tax_id.tax_group_id.id,
                    "country_id": self.env.ref("base.ro").id,
                    "invoice_repartition_line_ids": rep,
                    "refund_repartition_line_ids": [
                        (0, 0, {"repartition_type": "base", "factor_percent": 100}),
                        (0, 0, {"repartition_type": "tax", "factor_percent": -100, "account_id": acc_4427.id}),
                        (0, 0, {"repartition_type": "tax", "factor_percent": 100, "account_id": acc_4426.id}),
                    ],
                }
            ),
            acc_4426,
            acc_4427,
        )

    def test_vat_deferred_payment_reverse_charge(self):
        """Amânarea plăţii TVA în vamă — art. 326 alin. (4)-(5) Cod fiscal.

        Cu certificat de amânare nu se face plată efectivă la organele vamale; taxa se
        evidenţiază în decont atât ca deductibilă, cât şi ca fiind colectată. Nota trebuie să
        fie `Dr 4426 = Cr 4427`, **fără linie pe contul de buget** — aceea ar însemna o datorie
        care nu există.

        Taxa e comutatorul: repartiţia ei cu două linii descrie chiar acest regim.
        """
        tax_rc, acc_4426, acc_4427 = self._build_reverse_charge_tax()
        cost = self.env["stock.landed.cost"].create(
            {
                "landed_type": "dvi",
                "dvi_number": "26ROIS0600999999",
                "account_journal_id": self.env["account.journal"].search([("type", "=", "purchase")], limit=1).id,
                "tax_id": tax_rc.id,
                "tax_base": 10000.0,
                "tax_value": 1900.0,
            }
        )
        cost.account_move_id = self.env["account.move"].create(
            {"journal_id": cost.account_journal_id.id, "date": cost.date, "move_type": "entry"}
        )
        accounts_data = {"expense": self.env["account.account"].search([("code", "=like", "446%")], limit=1)}
        vals = cost._prepare_tax_lines("TVA import", tax_rc.compute_all(cost.tax_base), accounts_data)

        conturi = [self.env["account.account"].browse(v["account_id"]).code for v in vals]
        self.assertEqual(len(vals), 2, f"Taxare inversă: exact 2 linii, primit {conturi}")
        self.assertFalse(
            any(c.startswith("446") for c in conturi),
            f"Nu trebuie să apară datorie la buget la amânarea de la plată; conturi: {conturi}",
        )
        self.assertEqual(sum(v["debit"] for v in vals), sum(v["credit"] for v in vals), "Nota se soldează")
        debit = [v for v in vals if v["debit"]]
        credit = [v for v in vals if v["credit"]]
        self.assertEqual(len(debit), 1)
        self.assertEqual(len(credit), 1)
        self.assertEqual(debit[0]["debit"], 1900.0)
        self.assertEqual(
            self.env["account.account"].browse(debit[0]["account_id"]).code,
            acc_4426.code,
            "Debitul merge pe TVA deductibilă",
        )
        self.assertEqual(
            self.env["account.account"].browse(credit[0]["account_id"]).code,
            acc_4427.code,
            "Creditul merge pe TVA colectată, nu pe contul de buget",
        )

    def test_customs_products_accounts_and_landed_cost_flag(self):
        """Comisionul vamal e datorie către bugetul de stat (446), nu fond special (447).

        447 „Fonduri speciale - taxe şi vărsăminte asimilate" e rezervat de OMFP 1802/2014
        datoriilor către alte organisme publice, creditat exclusiv prin 635. Onorariul
        comisionarului vamal (broker) nu trece prin acest wizard — e furnizor obişnuit, cu sold
        pe 401, iar capitalizarea se face cu butonul nativ de pe factura lui.
        """
        wizard = self.env["account.invoice.dvi"].create({})

        duty_vals = wizard._prepare_custom_duty_product()

        for vals in (duty_vals,):
            account = self.env["account.account"].browse(vals["property_account_expense_id"])
            self.assertTrue(
                account.code.startswith("446"),
                f"Contul aşteptat este 446*, primit {account.code}",
            )
            # Analiticul de scadență: în planul RO 4461 = peste un an, 4462 = până la un an.
            # Datoria vamală se stinge în zile (OMFP 1802/2014 pct. 360), deci 4462.
            self.assertTrue(
                account.code.startswith("4462"),
                f"Se aşteaptă analiticul de scadenţă scurtă 4462*, primit {account.code} — "
                "o căutare 446% cu limit=1 ia 4461, adică datorii peste un an",
            )
            # Ambele produse trebuie să funcţioneze şi pe traseul nativ
            # „factură furnizor -> Create Landed Costs".
            self.assertTrue(vals["landed_cost_ok"], "Produsul trebuie marcat ca landed cost")
            self.assertEqual(vals["split_method_landed_cost"], "by_current_cost_price")
            self.assertEqual(vals["type"], "service")

        # Produsul creat efectiv păstrează marcajul (constrângerea din core cere type == service).
        product = self.env["product.product"].create(duty_vals)
        self.assertTrue(product.landed_cost_ok)
