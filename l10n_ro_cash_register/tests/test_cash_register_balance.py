# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestL10nRoCashRegisterBalance(TransactionCase):
    """Reportul soldurilor trebuie să fie automat, nu condiționat de butonul Refresh.

    OMFP 2634/2015, Anexa 1 pct. 58 lit. e) și n): programul trebuie să asigure reluarea
    automată în calcul a soldurilor obținute anterior, iar orice sold trebuie să rezulte
    dintr-o listă de înregistrări și dintr-un sold anterior.
    """

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.chart_template = "ro"
        cls.cash_journal = cls.env["account.journal"].create(
            {
                "name": "Test Cash Balance",
                "code": "TCBAL",
                "type": "cash",
            }
        )
        cls.cash_account = cls.cash_journal.default_account_id
        cls.counterpart = cls.env["account.account"].search(
            [("company_ids", "in", cls.env.company.id), ("account_type", "=", "income")],
            limit=1,
        )

    # -------------------------
    # Helpers
    # -------------------------
    def _cash_move(self, date, amount, direction="in", ref="Test"):
        """Încasare (debit pe casă) sau plată (credit pe casă), postată."""
        debit = amount if direction == "in" else 0.0
        credit = amount if direction == "out" else 0.0
        move = self.env["account.move"].create(
            {
                "journal_id": self.cash_journal.id,
                "date": date,
                "ref": ref,
                "line_ids": [
                    (0, 0, {"account_id": self.cash_account.id, "debit": debit, "credit": credit, "name": ref}),
                    (0, 0, {"account_id": self.counterpart.id, "debit": credit, "credit": debit, "name": ref}),
                ],
            }
        )
        move.action_post()
        return move

    def _register(self, date):
        return self.env["l10n.ro.cash.register"].create({"journal_id": self.cash_journal.id, "date": date})

    # -------------------------
    # Tests
    # -------------------------
    def test_balances_follow_moves_posted_after_creation(self):
        """Registrul creat pe o zi goală se actualizează când apar operațiunile zilei.

        Este cazul curent în producție: registrul zilei este creat automat la postarea
        primei plăți sau de acțiunea de generare, deci aproape întotdeauna înainte ca
        ziua să fie completă.
        """
        register = self._register("2026-03-12")
        self.assertAlmostEqual(register.balance_end, 0.0, places=2)

        self._cash_move("2026-03-12", 700.0, "in", "Chitanta 001")

        self.assertAlmostEqual(register.balance_end, 700.0, places=2, msg="Soldul final trebuie să includă încasarea")

    def test_carry_over_updates_on_retroactive_move(self):
        """O mișcare retroactivă actualizează și soldul zilelor următoare, nu doar al zilei ei."""
        self._cash_move("2026-03-10", 1000.0, "in", "Chitanta 001")
        self._cash_move("2026-03-10", 250.0, "out", "Dispozitie plata 001")
        day_one = self._register("2026-03-10")
        day_two = self._register("2026-03-11")
        self.assertAlmostEqual(day_two.balance_start, 750.0, places=2)

        # Încasare adăugată în ziua 1 după ce registrul zilei 2 există deja.
        self._cash_move("2026-03-10", 500.0, "in", "Chitanta 002")

        self.assertAlmostEqual(day_one.balance_end, 1250.0, places=2)
        self.assertAlmostEqual(
            day_two.balance_start,
            1250.0,
            places=2,
            msg="Soldul de deschidere trebuie să fie soldul de închidere al zilei precedente",
        )

    def test_carry_over_equals_previous_closing_balance(self):
        """Invariantul de report: sold deschidere zi N == sold închidere zi N-1."""
        self._cash_move("2026-03-10", 1000.0, "in")
        self._cash_move("2026-03-11", 400.0, "in")
        self._cash_move("2026-03-12", 150.0, "out")
        registers = self.env["l10n.ro.cash.register"].create(
            [{"journal_id": self.cash_journal.id, "date": date} for date in ("2026-03-10", "2026-03-11", "2026-03-12")]
        )
        registers = registers.sorted("date")
        for previous, current in zip(registers, registers[1:], strict=False):
            self.assertAlmostEqual(current.balance_start, previous.balance_end, places=2)
        self.assertAlmostEqual(registers[-1].balance_end, 1250.0, places=2)

    def test_balances_updated_when_move_reset_to_draft(self):
        """Anularea unei note postate readuce soldurile la valoarea corectă."""
        move = self._cash_move("2026-03-10", 1000.0, "in")
        register = self._register("2026-03-10")
        self.assertAlmostEqual(register.balance_end, 1000.0, places=2)

        move.button_draft()

        self.assertAlmostEqual(register.balance_end, 0.0, places=2)

    def test_lines_are_listed_chronologically(self):
        """Liniile se listează în ordinea în care s-au petrecut operațiunile.

        Ordinea implicită a liniilor contabile este descrescătoare; folosită ca atare,
        ar produce solduri intermediare care nu au existat.
        """
        first = self._cash_move("2026-03-10", 1000.0, "in", "Chitanta 001")
        second = self._cash_move("2026-03-10", 250.0, "out", "Dispozitie plata 001")
        register = self._register("2026-03-10")

        moves_in_order = register.move_line_ids.mapped("move_id")
        self.assertEqual(moves_in_order[0], first)
        self.assertEqual(moves_in_order[1], second)

    def test_moves_of_other_company_are_excluded(self):
        """Registrul unei companii nu preia mișcări ale altei companii."""
        register = self._register("2026-03-10")
        self._cash_move("2026-03-10", 1000.0, "in")

        other_company = self.env["res.company"].create({"name": "Alta Companie Casa"})
        self.assertFalse(register.move_line_ids.filtered(lambda line: line.company_id == other_company))
        self.assertAlmostEqual(register.balance_end, 1000.0, places=2)

    def test_action_print_returns_report_action(self):
        """Butonul de tipărire din formular returnează raportul registrului."""
        # Pe o companie fără layout de raport, Odoo interpune wizardul de configurare;
        # testăm situația din producție, cu layoutul deja stabilit.
        self.env.company.external_report_layout_id = self.env.ref("web.external_layout_standard")
        register = self._register("2026-03-10")

        action = register.action_print()

        self.assertEqual(action.get("type"), "ir.actions.report")
        self.assertEqual(action.get("report_name"), "l10n_ro_cash_register.report_cash_register")
        self.assertEqual(action.get("context", {}).get("active_ids"), register.ids)
