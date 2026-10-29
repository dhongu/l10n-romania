# © 2026 Terrabit
# See README.rst file on addons root folder for license details
#
# Capturi de ecran pentru fișa „Tipul documentului justificativ pe notele contabile" —
# generate în timpul testelor, în limba RO, pe planul de conturi RO.
#
# Seedează două note de TVA la import (Dr 4426 / Cr 4462), construite ca nota generată de DVI:
# linia de TVA cu grilele taxei și perechea tehnică pe 473 care duce baza în D300. Una e în ciornă,
# cu tipul implicit „Notă contabilă", cealaltă postată, cu „Import (DVI)" ales de contabil. Lângă
# ele, facturi, o factură furnizor, o încasare prin bancă și o notă de chirie în avans, ca lista
# grupată pe tip să aibă grupuri.
#
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro_account_move_document_type,deltatech_doc_screenshots \
#       --test-tags=fise_screenshots --stop-after-init
import json
import unittest

from dateutil.relativedelta import relativedelta

from odoo import Command, fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

try:
    from odoo.addons.deltatech_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None


@tagged("-at_install", "post_install", "fise_screenshots")
class TestDocumentTypeScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_account_move_document_type"

    # TVA-ul unui import de 10.000 lei la 21%, plătit în vamă
    IMPORT_BASE = 10000.0
    IMPORT_VAT = 2100.0
    DVI_NUMBER = "26ROBU100000012345"  # MRN: 18 caractere

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("deltatech_doc_screenshots indisponibil")
        super().setUpClass()
        cls.prepare_ro_company(name="Demo Import SRL")
        env = cls.env
        company = env.company
        env.ref("base.user_admin").write({"company_ids": [(4, company.id)], "company_id": company.id})

        cls.date = fields.Date.today().replace(day=1) - relativedelta(months=1)
        cls.misc_journal = env["account.journal"].search(
            [("type", "=", "general"), ("company_id", "=", company.id)], limit=1
        )
        cls.acc_4426 = cls._account("4426")
        cls.acc_446 = cls._account("4462")  # 4461 = reluate peste un an
        cls.acc_473 = cls._account("473")
        cls.tax = env["account.chart.template"].ref("tvad_21")
        cls.vendor = env["res.partner"].create({"name": "Furnizor Servicii SRL", "country_id": env.ref("base.ro").id})
        cls.customer = env["res.partner"].create({"name": "Client Demo SRL", "country_id": env.ref("base.ro").id})

        # 1. nota de TVA la import introdusă manual, în ciornă: tipul implicit „Notă contabilă"
        cls.note_draft = cls._import_vat_note("TVA import - DVI în curs de înregistrare")
        # 2. aceeași operațiune, confirmată, cu DVI-ul ales ca document justificativ
        cls.note_dvi = cls._import_vat_note(cls.DVI_NUMBER)
        cls.note_dvi.l10n_ro_document_type = "customs_declaration"
        cls.note_dvi.action_post()

        # 3. documente obișnuite, ca lista grupată să arate mai multe tipuri
        sale_tax = env["account.chart.template"].ref("tvac_21")
        for move_type, partner, price, tax in [
            ("out_invoice", cls.customer, 1500.0, sale_tax),
            ("out_invoice", cls.customer, 2300.0, sale_tax),
            ("in_invoice", cls.vendor, 4000.0, cls.tax),
        ]:
            cls.init_invoice(move_type, partner=partner, invoice_date=cls.date, amounts=[price], taxes=tax, post=True)
        payment = env["account.payment"].create(
            {
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": cls.customer.id,
                "amount": 1815.0,
                "date": cls.date,
                "journal_id": cls.company_data["default_journal_bank"].id,
            }
        )
        payment.action_post()
        # o notă contabilă propriu-zisă: chiria plătită în avans din bancă (Dr 471 / Cr 5121)
        prepaid = env["account.move"].create(
            {
                "move_type": "entry",
                "journal_id": cls.misc_journal.id,
                "date": cls.date,
                "ref": "Chirie plătită în avans",
                "line_ids": [
                    Command.create({"name": "Chirie în avans", "account_id": cls._account("471").id, "debit": 500.0}),
                    Command.create({"name": "Chirie în avans", "account_id": cls._account("5121").id, "credit": 500.0}),
                ],
            }
        )
        prepaid.action_post()

        cls.act_entries = env.ref("account.action_move_journal_line").id

    @classmethod
    def _account(cls, prefix):
        return cls.env["account.account"].search(
            [("code", "=like", f"{prefix}%"), ("company_ids", "in", [cls.env.company.id])], order="code", limit=1
        )

    @classmethod
    def _import_vat_note(cls, ref):
        """Nota de TVA la import cu grilele D300, ca cea generată de `l10n_ro_customs_dvi`."""
        move = cls.env["account.move"].create(
            {"move_type": "entry", "journal_id": cls.misc_journal.id, "date": cls.date, "ref": ref}
        )
        reps = cls.tax.invoice_repartition_line_ids
        tax_rep = reps.filtered(lambda r: r.repartition_type == "tax")[:1]
        base_tags = reps.filtered(lambda r: r.repartition_type == "base").tag_ids
        lines = [
            {
                "name": "TVA import 21%",
                "account_id": cls.acc_4426.id,
                "debit": cls.IMPORT_VAT,
                "tax_repartition_line_id": tax_rep.id,
                "tax_base_amount": cls.IMPORT_BASE,
                "tax_tag_ids": [Command.set(tax_rep.tag_ids.ids)],
            },
            {"name": "TVA import plătit în vamă", "account_id": cls.acc_446.id, "credit": cls.IMPORT_VAT},
            {
                "name": "Bază TVA import",
                "account_id": cls.acc_473.id,
                "debit": cls.IMPORT_BASE,
                "tax_ids": [Command.set(cls.tax.ids)],
                "tax_tag_ids": [Command.set(base_tags.ids)],
            },
            {"name": "Bază TVA import", "account_id": cls.acc_473.id, "credit": cls.IMPORT_BASE},
        ]
        cls.env["account.move.line"].with_context(skip_invoice_sync=True).create(
            [dict(line, move_id=move.id) for line in lines]
        )
        return move

    def test_capture_fise(self):
        posted_moves = [("company_id", "=", self.env.company.id), ("state", "=", "posted")]
        list_view = self.env.ref("account.view_move_tree").id
        self.capture_screenshots(
            [
                # 1. Nota contabilă în ciornă: tipul implicit „Notă contabilă", lângă referință
                dict(
                    self.account_move_shot(self.note_draft, "01_nota_tip_implicit.png"),
                    highlight=["div[name='l10n_ro_document_type']"],
                    settle=2000,
                ),
                # 2. Nota confirmată, cu DVI-ul ales ca document justificativ
                dict(
                    self.account_move_shot(self.note_dvi, "02_nota_tip_dvi.png"),
                    highlight=["div[name='ref']", "div[name='l10n_ro_document_type']"],
                    settle=2000,
                ),
                # 3. Lista notelor contabile grupată după tipul documentului
                {
                    "url": f"action={self.act_entries}",
                    "name": "03_note_grupate_tip.png",
                    "wait": ".o_list_view",
                    # lista din meniu (view_move_tree), doar notele postate, grupate pe tip și
                    # cu coloana opțională „Tip document" afișată din meniul de coloane
                    "eval": (
                        "async () => { const sleep = (ms) => new Promise((r) => setTimeout(r, ms));"
                        "await odoo.__WOWL_DEBUG__.root.env.services.action.doAction({"
                        "type: 'ir.actions.act_window', res_model: 'account.move', "
                        f"domain: {json.dumps(posted_moves)}, views: [[{list_view}, 'list'], [false, 'form']], "
                        "context: {group_by: ['l10n_ro_document_type']}, "
                        "name: 'Note contabile'}, {clearBreadcrumbs: true});"
                        "await sleep(1500);"
                        "document.querySelector('.o_optional_columns_dropdown button, "
                        ".o_optional_columns_dropdown_toggle').click(); await sleep(500);"
                        "const item = [...document.querySelectorAll('.o-dropdown-item, .dropdown-item')]"
                        ".find((el) => el.textContent.trim() === 'Tip document');"
                        "if (item) { (item.querySelector('input') || item).click(); } await sleep(500);"
                        "document.body.click();"
                        "for (const row of document.querySelectorAll('.o_group_header')) {"
                        " row.click(); await sleep(400); } }"
                    ),
                    "eval_wait": 4500,
                    "full": True,
                    "settle": 2000,
                },
            ],
            hide_systray=True,
        )
