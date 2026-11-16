# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
# Capturi pentru fișa consultant, pe planul de conturi RO. Trei produse, câte unul pe scenariu
# (FIFO nu amestecă stocul): fluxul complet, stoc rezervat și stoc deja vândut.
#
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d test19 -i l10n_ro_stock_account_landed_cost_account,l10n_ro_doc_screenshots \
#       --test-tags=fise_screenshots --stop-after-init --http-port=8170
import unittest

from odoo import Command, fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import ScreenshotCase
except ImportError:
    ScreenshotCase = None


@tagged("-at_install", "post_install", "fise_screenshots")
class TestLandedCostScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_stock_account_landed_cost_account"

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        cls.prepare_ro_company(name="RO Company")
        company = cls.env.company
        company.l10n_ro_accounting = True
        cls.env.ref("base.user_admin").write({"company_ids": [(4, company.id)], "company_id": company.id})
        env = cls.env
        warehouse = env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1)
        warehouse.write({"name": "Magazin central", "code": "MC"})
        cls.account_valuation = cls._ro_account("371%", "Mărfuri", "371000", "asset_current")
        cls.account_transport = cls._ro_account("624%", "Cheltuieli cu transportul", "624000", "expense")
        cls.account_408 = cls._ro_account("408%", "Furnizori - facturi nesosite", "408000", "liability_current")
        company.l10n_ro_property_stock_picking_payable_account_id = cls.account_408
        cls.account_inter = env["account.account"].create(
            {"name": "Costuri de repartizat (analitic tehnic)", "code": "473900", "account_type": "asset_current"}
        )
        cls.stock_journal = env["account.journal"].create(
            {"name": "Stoc - Magazin central", "code": "STMC", "type": "general", "company_id": company.id}
        )
        categ = env["product.category"].create(
            {
                "name": "Mărfuri",
                "property_valuation": "real_time",
                "property_cost_method": "fifo",
                "property_stock_valuation_account_id": cls.account_valuation.id,
                "property_stock_journal": cls.stock_journal.id,
            }
        )
        cls.products = {
            key: env["product.product"].create(
                {"name": name, "is_storable": True, "categ_id": categ.id, "standard_price": 100.0}
            )
            for key, name in (
                ("flow", "Marfă - flux complet"),
                ("reserved", "Marfă - rezervată"),
                ("sold", "Marfă - vândută"),
                ("notice", "Marfă - recepție cu aviz"),
            )
        }
        cls.cost_product = env["product.product"].create(
            {"name": "Transport marfă", "type": "service", "landed_cost_ok": True}
        )
        payable = env["account.account"].create(
            {"name": "Furnizori", "code": "401900", "account_type": "liability_payable", "reconcile": True}
        )
        cls.vendor = env["res.partner"].create({"name": "Furnizor Demo SRL", "property_account_payable_id": payable.id})
        cls.carrier = env["res.partner"].create(
            {"name": "Transportator Demo SRL", "property_account_payable_id": payable.id}
        )

        # scenariul 1: comandă -> recepție -> factura mărfii -> factura transportatorului -> cost adițional
        cls.po, cls.receipt = cls._purchase("flow")
        cls.po.action_create_invoice()
        cls.goods_bill = cls.po.invoice_ids
        cls.goods_bill.write({"invoice_date": fields.Date.today(), "ref": "FF-1001"})
        cls.goods_bill.action_post()
        cls.carrier_bill = cls._carrier_bill("FT-2001")
        cls.landed_standard = cls._landed(cls.carrier_bill, cls.receipt)
        company.account_storno = True
        company.write(
            {
                "l10n_ro_landed_cost_method": "intermediary",
                "l10n_ro_landed_cost_intermediary_account_id": cls.account_inter.id,
            }
        )
        cls.landed_routed = cls._landed(cls._carrier_bill("FT-2002"), cls.receipt)
        company.l10n_ro_landed_cost_method = "standard"

        # scenariul 2: 4 din 10 buc. rezervate pe o livrare nevalidată
        __, cls.receipt_reserved = cls._purchase("reserved")
        cls.delivery_reserved = cls._delivery("reserved", validate=False)
        cls.landed_reserved = cls._landed(cls._carrier_bill("FT-2003"), cls.receipt_reserved)

        # scenariul 3: 4 din 10 buc. livrate înainte de costul adițional
        __, cls.receipt_sold = cls._purchase("sold")
        cls.delivery_sold = cls._delivery("sold", validate=True)
        cls.landed_sold = cls._landed(cls._carrier_bill("FT-2004"), cls.receipt_sold)

        # același cost, prin cont intermediar cu Storno accounting (a doua pereche în roșu)
        company.write(
            {
                "l10n_ro_landed_cost_method": "intermediary",
                "l10n_ro_landed_cost_intermediary_account_id": cls.account_inter.id,
            }
        )
        cls.landed_reserved_routed = cls._landed(cls._carrier_bill("FT-2007"), cls.receipt_reserved)
        cls.landed_sold_routed = cls._landed(cls._carrier_bill("FT-2008"), cls.receipt_sold)
        company.l10n_ro_landed_cost_method = "standard"

        # recepție pe bază de aviz: 371 / 408 la recepție, 408 / 401 la factura mărfii
        cls.po_notice, cls.receipt_notice = cls._purchase("notice", notice=True)
        cls.po_notice.action_create_invoice()
        cls.goods_bill_notice = cls.po_notice.invoice_ids
        cls.goods_bill_notice.write({"invoice_date": fields.Date.today(), "ref": "FF-1002"})
        cls.goods_bill_notice.action_post()
        cls.landed_notice = cls._landed(cls._carrier_bill("FT-2005"), cls.receipt_notice)
        # factura transportatorului încă fără cost adițional (butonul de pe ea)
        cls.carrier_bill_pending = cls._carrier_bill("FT-2006")

    @classmethod
    def _purchase(cls, key, notice=False):
        po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.vendor.id,
                "order_line": [
                    Command.create({"product_id": cls.products[key].id, "product_qty": 10.0, "price_unit": 100.0})
                ],
            }
        )
        po.button_confirm()
        receipt = po.picking_ids[0]
        receipt.l10n_ro_notice = notice
        receipt.move_line_ids.write({"quantity": 10.0})
        receipt.with_context(demo_mode=True).button_validate()
        return po, receipt

    @classmethod
    def _delivery(cls, key, validate):
        warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.env.company.id)], limit=1)
        stock = warehouse.lot_stock_id
        customers = cls.env.ref("stock.stock_location_customers")
        picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": warehouse.out_type_id.id,
                "location_id": stock.id,
                "location_dest_id": customers.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": cls.products[key].id,
                            "product_uom_qty": 4.0,
                            "product_uom": cls.products[key].uom_id.id,
                            "location_id": stock.id,
                            "location_dest_id": customers.id,
                        }
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        if validate:
            picking.move_line_ids.write({"quantity": 4.0})
            picking.with_context(demo_mode=True).button_validate()
        return picking

    @classmethod
    def _carrier_bill(cls, ref):
        bill = cls.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": cls.carrier.id,
                "invoice_date": fields.Date.today(),
                "ref": ref,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.cost_product.id,
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "account_id": cls.account_transport.id,
                            "is_landed_costs_line": True,
                        }
                    )
                ],
            }
        )
        bill.action_post()
        return bill

    @classmethod
    def _landed(cls, bill, receipt):
        """Ca operatorul: butonul de pe factura transportatorului, apoi recepția în Transferuri."""
        landed = cls.env["stock.landed.cost"].browse(bill.button_create_landed_costs()["res_id"])
        landed.write({"picking_ids": [Command.set(receipt.ids)], "account_journal_id": cls.stock_journal.id})
        landed.cost_lines.split_method = "by_quantity"
        landed.compute_landed_cost()
        landed.button_validate()
        return landed

    @classmethod
    def _ro_account(cls, code_like, name, code, account_type):
        account = cls.env["account.account"].search(
            [("code", "=like", code_like), ("company_ids", "in", [cls.env.company.id])], order="code", limit=1
        )
        return account or cls.env["account.account"].create({"name": name, "code": code, "account_type": account_type})

    def _dr_cr(self, move):
        return sorted((line.account_id.code[:6], round(line.debit, 2), round(line.credit, 2)) for line in move.line_ids)

    def _form(self, record, name, **kw):
        return {
            "path": f"/web?debug=0#id={record.id}&model={record._name}&view_type=form",
            "name": name,
            "wait": ".o_form_view",
            "settle": 2500,
            **kw,
        }

    def _shots(self):
        action = self.env.ref("account.action_account_config").id
        return [
            {
                "path": f"/web?debug=0#action={action}&view_type=form",
                "name": "01_settings_landed_cost.png",
                "wait": ".o_form_view",
                "eval": (
                    "const tab = [...document.querySelectorAll('.settings_tab .tab')]"
                    ".find((el) => /Rom[aâ]nia/.test(el.textContent)); if (tab) { tab.click(); } "
                    "setTimeout(() => document.querySelector('[name=l10n_ro_landed_cost_method]')"
                    "?.scrollIntoView({block: 'center'}), 800)"
                ),
                "highlight": ["div[name='l10n_ro_landed_cost_method']"],
                "settle": 4500,
            },
            self._form(self.po, "02_purchase_order.png"),
            self._form(self.receipt, "03_receipt.png"),
            self._form(self.goods_bill, "04_goods_bill.png"),
            self._form(
                self.carrier_bill_pending,
                "05_transport_bill_button.png",
                highlight=["button[name='button_create_landed_costs']"],
            ),
            self._form(self.landed_standard, "06_landed_cost_form.png"),
            self.account_move_shot(self.landed_standard.account_move_id, "07_note_standard.png"),
            self.account_move_shot(self.landed_routed.account_move_id, "08_note_intermediary.png"),
            self._form(self.delivery_reserved, "09_delivery_reserved.png"),
            self.account_move_shot(self.landed_reserved.account_move_id, "10_note_reserved.png"),
            self._form(self.delivery_sold, "11_delivery_sold.png"),
            self._form(self.landed_sold, "12_landed_cost_sold.png"),
            self.account_move_shot(self.landed_sold.account_move_id, "13_note_sold.png"),
            self.account_move_shot(self.carrier_bill, "14_transport_bill_note.png"),
            self.account_move_shot(self.delivery_sold.move_ids.account_move_id, "15_delivery_sold_note.png"),
            self.account_move_shot(self.receipt_notice.move_ids.account_move_id, "16_receipt_note_notice.png"),
            self.account_move_shot(self.goods_bill_notice, "17_goods_bill_notice.png"),
            self.account_move_shot(self.landed_notice.account_move_id, "18_note_notice.png"),
            {
                "path": f"/web?debug=0#action={action}&view_type=form",
                "name": "19_settings_storno.png",
                "wait": ".o_form_view",
                "eval": (
                    "const tab = [...document.querySelectorAll('.settings_tab .tab')]"
                    ".find((el) => /Factur|Invoic/.test(el.textContent)); if (tab) { tab.click(); } "
                    "setTimeout(() => document.querySelector('[name=account_storno]')"
                    "?.scrollIntoView({block: 'center'}), 800)"
                ),
                "highlight": ["div[name='account_storno']"],
                "settle": 4500,
            },
            self.account_move_shot(self.landed_reserved_routed.account_move_id, "20_note_reserved_storno.png"),
            self.account_move_shot(self.landed_sold_routed.account_move_id, "21_note_sold_storno.png"),
        ]

    def test_capture_fise(self):
        # notele din capturi trebuie să fie cele descrise în fișă
        self.assertEqual(
            self._dr_cr(self.landed_standard.account_move_id), [("371000", 100.0, 0.0), ("624000", 0.0, 100.0)]
        )
        self.assertEqual(
            self._dr_cr(self.landed_routed.account_move_id),
            [("371000", 100.0, 0.0), ("473900", 0.0, -100.0), ("473900", 0.0, 100.0), ("624000", -100.0, 0.0)],
        )
        self.assertEqual(
            self._dr_cr(self.landed_reserved.account_move_id), [("371000", 100.0, 0.0), ("624000", 0.0, 100.0)]
        )
        self.assertEqual(self.delivery_reserved.state, "assigned")
        self.assertEqual(self._dr_cr(self.landed_sold.account_move_id), [("371000", 60.0, 0.0), ("624000", 0.0, 60.0)])
        self.assertEqual(
            self._dr_cr(self.receipt_notice.move_ids.account_move_id),
            sorted([("371000", 1000.0, 0.0), (self.account_408.code[:6], 0.0, 1000.0)]),
        )
        self.assertEqual(
            self._dr_cr(self.landed_notice.account_move_id), [("371000", 100.0, 0.0), ("624000", 0.0, 100.0)]
        )
        self.assertEqual(
            self._dr_cr(self.landed_reserved_routed.account_move_id),
            [("371000", 100.0, 0.0), ("473900", 0.0, -100.0), ("473900", 0.0, 100.0), ("624000", -100.0, 0.0)],
        )
        self.assertEqual(
            self._dr_cr(self.landed_sold_routed.account_move_id),
            [("371000", 60.0, 0.0), ("473900", 0.0, -60.0), ("473900", 0.0, 60.0), ("624000", -60.0, 0.0)],
        )
        self.capture_screenshots(self._shots())

    def test_capture_usage(self):
        self.capture_screenshots(self._shots(), lang="en_US")
