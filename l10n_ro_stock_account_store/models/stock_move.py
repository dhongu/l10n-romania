# Copyright (C) 2024 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, fields, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    l10n_ro_store_sale_amount = fields.Monetary(
        string="Store Sale Amount",
        currency_field="company_currency_id",
        readonly=True,
        copy=False,
        help="Value at sale price, VAT included, with which the goods entered or left the store.",
    )
    l10n_ro_store_markup_amount = fields.Monetary(
        string="Store Markup",
        currency_field="company_currency_id",
        readonly=True,
        copy=False,
    )
    l10n_ro_store_tax_amount = fields.Monetary(
        string="Store Uneligible VAT",
        currency_field="company_currency_id",
        readonly=True,
        copy=False,
    )
    l10n_ro_store_account_move_id = fields.Many2one(
        "account.move",
        string="Store Journal Entry",
        readonly=True,
        copy=False,
        index="btree_not_null",
    )

    def _l10n_ro_is_store_location(self, location):
        return location.usage == "internal" and (location.l10n_ro_merchandise_type == "store")

    def _l10n_ro_get_store_root_location(self, location):
        """Topmost store location above `location` (shelves of the same store)."""
        while location.location_id and self._l10n_ro_is_store_location(location.location_id):
            location = location.location_id
        return location

    def _l10n_ro_get_store_direction(self):
        """'in' when the goods enter a store, 'out' when they leave it."""
        self.ensure_one()
        src_store = self._l10n_ro_is_store_location(self.location_id)
        dest_store = self._l10n_ro_is_store_location(self.location_dest_id)
        if dest_store and not src_store:
            return "in"
        if src_store and not dest_store:
            return "out"
        return False

    def _l10n_ro_should_create_store_move(self):
        self.ensure_one()
        return (
            self.is_l10n_ro_record
            and self.state == "done"
            and self.product_id.is_storable
            and self.product_id.valuation == "real_time"
            and not self.product_uom.is_zero(self.quantity)
            and not self.l10n_ro_store_account_move_id
            and bool(self._l10n_ro_get_store_direction())
        )

    def _l10n_ro_get_store_reference_move(self):
        """Move whose sale price values the goods of this move in the store.

        A return takes the move it returns. A move leaving the store takes the
        last entry of the product in that store, so the markup and the VAT
        booked at entry are released at the same price. Otherwise there is no
        reference and the current sale price of the product is used.
        """
        self.ensure_one()
        origin = self.origin_returned_move_id
        if origin.l10n_ro_store_account_move_id and origin.product_qty:
            return origin
        if self._l10n_ro_get_store_direction() == "out":
            return self.search(
                [
                    ("product_id", "=", self.product_id.id),
                    (
                        "location_dest_id",
                        "child_of",
                        self._l10n_ro_get_store_root_location(self.location_id).id,
                    ),
                    ("state", "=", "done"),
                    ("l10n_ro_store_account_move_id", "!=", False),
                    ("product_qty", "!=", 0),
                    ("company_id", "=", self.company_id.id),
                    ("id", "!=", self.id),
                ],
                order="date desc, id desc",
                limit=1,
            )
        return self.browse()

    def _l10n_ro_get_store_sale_price(self):
        """Unit sale price, in the product UoM, of goods entering the store.

        The same price as the reception note at sale price (NIR) of
        `l10n_ro_stock_picking_report`, when installed: the price frozen on the move
        at reception, else the store pricelist of the location, else the product price.
        """
        self.ensure_one()
        if "l10n_ro_sale_price" in self._fields and self.l10n_ro_sale_price:
            return self.l10n_ro_sale_price
        location = self.location_dest_id
        if "store_pricelist_id" in location._fields and location.store_pricelist_id:
            return location.store_pricelist_id._get_product_price(self.product_id, 1)
        return self.product_id.lst_price

    def _l10n_ro_compute_store_amounts(self):
        """Return (sale amount VAT included, markup, uneligible VAT)."""
        self.ensure_one()
        currency = self.company_id.currency_id
        qty = self.product_qty
        ref_move = self._l10n_ro_get_store_reference_move()
        if ref_move:
            ratio = qty / ref_move.product_qty
            sale_amount = currency.round(ref_move.l10n_ro_store_sale_amount * ratio)
            tax_amount = currency.round(abs(ref_move.l10n_ro_store_tax_amount) * ratio)
        else:
            taxes = self.product_id.taxes_id.filtered(lambda t: t.company_id in self.company_id.parent_ids)
            res = taxes.compute_all(
                self._l10n_ro_get_store_sale_price(),
                currency=currency,
                quantity=qty,
                product=self.product_id,
            )
            sale_amount = res["total_included"]
            tax_amount = currency.round(res["total_included"] - res["total_excluded"])
        markup = currency.round(sale_amount - tax_amount - self.value)
        return sale_amount, markup, tax_amount

    def _l10n_ro_get_store_account_list(self):
        """List of (debit_key, credit_key, amount_field, sign).

        Entry: 371 = 378 (markup) and 371 = 4428 (uneligible VAT).
        Exit: 378 = 371 and 4428 = 371.
        A return reverses, in red (storno), the entry of the move it returns.
        """
        self.ensure_one()
        direction = self._l10n_ro_get_store_direction()
        entry = [
            ("stock_valuation", "l10n_ro_store_markup", "markup", 1),
            ("stock_valuation", "l10n_ro_uneligible_tax", "tax", 1),
        ]
        release = [
            ("l10n_ro_store_markup", "stock_valuation", "markup", 1),
            ("l10n_ro_uneligible_tax", "stock_valuation", "tax", 1),
        ]
        if self.origin_returned_move_id:
            # storno of the original document
            base = release if direction == "in" else entry
            return [(d, c, f, -1) for d, c, f, _s in base]
        return entry if direction == "in" else release

    def _l10n_ro_get_store_move_line_vals(self, amounts):
        self.ensure_one()
        accounts = self.product_id.product_tmpl_id.with_context(l10n_ro_stock_move=self).get_product_accounts()
        if not accounts.get("l10n_ro_store_markup"):
            raise UserError(
                self.env._(
                    "Please define a 'Store Markup Account' on the product category '%(categ)s'.",
                    categ=self.product_id.categ_id.display_name,
                )
            )
        if amounts["tax"] and not accounts.get("l10n_ro_uneligible_tax"):
            raise UserError(
                self.env._(
                    "Please define the 'Not Eligible Tax Account' on the company %(company)s.",
                    company=self.company_id.display_name,
                )
            )
        name = self.env._("%(ref)s - Store valuation", ref=self.reference)
        vals_list = []
        for debit_key, credit_key, amount_field, sign in self._l10n_ro_get_store_account_list():
            value = sign * amounts[amount_field]
            if self.company_id.currency_id.is_zero(value):
                continue
            common = {
                "name": name,
                "product_id": self.product_id.id,
                "quantity": self.product_qty,
                "is_storno": value < 0,
            }
            vals_list += [
                dict(
                    common,
                    account_id=accounts[debit_key].id,
                    debit=value,
                    credit=0,
                ),
                dict(
                    common,
                    account_id=accounts[credit_key].id,
                    debit=0,
                    credit=value,
                ),
            ]
        return vals_list

    def _l10n_ro_create_store_account_move(self):
        account_moves = self.env["account.move"]
        for move in self:
            if not move._l10n_ro_should_create_store_move():
                continue
            sale_amount, markup, tax = move._l10n_ro_compute_store_amounts()
            sign = -1 if move._l10n_ro_get_store_direction() == "out" else 1
            move.write(
                {
                    "l10n_ro_store_sale_amount": sale_amount,
                    "l10n_ro_store_markup_amount": sign * markup,
                    "l10n_ro_store_tax_amount": sign * tax,
                }
            )
            line_vals = move._l10n_ro_get_store_move_line_vals({"markup": markup, "tax": tax})
            if not line_vals:
                continue
            account_move = (
                self.env["account.move"]
                .sudo()
                .create(
                    {
                        "ref": move.reference,
                        "l10n_ro_extra_stock_move_id": move.id,
                        "journal_id": move.company_id.account_stock_journal_id.id,
                        "line_ids": [Command.create(vals) for vals in line_vals],
                        "date": self.env.context.get("force_period_date") or fields.Date.context_today(self),
                    }
                )
            )
            account_move._post()
            move.l10n_ro_store_account_move_id = account_move
            account_moves |= account_move
        return account_moves

    def _create_account_move_ro_extra(self):
        res = super()._create_account_move_ro_extra()
        res |= self._l10n_ro_create_store_account_move()
        return res
