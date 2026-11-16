# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import Command, api, fields, models
from odoo.exceptions import UserError


class L10nRoStoreRevaluation(models.Model):
    """Revaluation of the goods kept at sale price in a store, when their sale price changes.

    One record per product and store: the stock on hand is brought from the sale value
    booked so far (entries - exits - previous revaluations) to the new sale price, with
    the entry 371 = 378 / 4428 (or its reverse in black for a price cut).
    """

    _name = "l10n.ro.store.revaluation"
    _description = "Romania - Store Revaluation"
    _order = "datetime desc, id desc"
    _check_company_auto = True

    name = fields.Char(required=True, readonly=True, default="/", copy=False, index="trigram")
    datetime = fields.Datetime(required=True, readonly=True, default=fields.Datetime.now, index=True)
    date = fields.Date(required=True, readonly=True, default=fields.Date.context_today)
    company_id = fields.Many2one("res.company", required=True, readonly=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id")
    product_id = fields.Many2one("product.product", required=True, readonly=True, index=True, ondelete="restrict")
    location_id = fields.Many2one(
        "stock.location",
        string="Store",
        required=True,
        readonly=True,
        index=True,
        ondelete="restrict",
        check_company=True,
    )
    quantity = fields.Float(readonly=True, digits="Product Unit")
    old_price = fields.Float(
        "Old Sale Price",
        readonly=True,
        digits="Product Price",
        help="Unit sale price, without VAT, at which the stock was booked before the revaluation.",
    )
    new_price = fields.Float(
        "New Sale Price", readonly=True, digits="Product Price", help="Unit sale price, without VAT."
    )
    old_sale_amount = fields.Monetary("Old Sale Value", readonly=True, help="Booked sale value, VAT included.")
    new_sale_amount = fields.Monetary("New Sale Value", readonly=True, help="Quantity x new sale price, VAT included.")
    old_tax_amount = fields.Monetary("Old Uneligible VAT", readonly=True)
    new_tax_amount = fields.Monetary("New Uneligible VAT", readonly=True)
    markup_amount = fields.Monetary("Markup Difference", compute="_compute_differences", store=True)
    tax_amount = fields.Monetary("VAT Difference", compute="_compute_differences", store=True)
    sale_amount = fields.Monetary("Sale Value Difference", compute="_compute_differences", store=True)
    account_move_id = fields.Many2one("account.move", string="Journal Entry", readonly=True, copy=False)
    user_id = fields.Many2one("res.users", string="Changed by", readonly=True, default=lambda self: self.env.user)
    origin_move_id = fields.Many2one(
        "stock.move",
        string="Origin Move",
        readonly=True,
        help="Return that brought the stock back to the store price at another price.",
    )

    @api.depends("old_sale_amount", "new_sale_amount", "old_tax_amount", "new_tax_amount")
    def _compute_differences(self):
        for revaluation in self:
            revaluation.sale_amount = revaluation.new_sale_amount - revaluation.old_sale_amount
            revaluation.tax_amount = revaluation.new_tax_amount - revaluation.old_tax_amount
            revaluation.markup_amount = revaluation.sale_amount - revaluation.tax_amount

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                company = self.env["res.company"].browse(vals.get("company_id")) or self.env.company
                vals["name"] = (
                    self.env["ir.sequence"].with_company(company).next_by_code("l10n.ro.store.revaluation") or "/"
                )
        return super().create(vals_list)

    @api.ondelete(at_uninstall=False)
    def _unlink_if_no_entry(self):
        if self.filtered("account_move_id"):
            raise UserError(self.env._("A store revaluation with a journal entry cannot be deleted."))

    # ------------------------------------------------------------------
    # Booked sale value of a product in a store
    # ------------------------------------------------------------------

    @api.model
    def _get_store_balance(self, product, store, company):
        """(quantity, sale value VAT included, uneligible VAT) booked for `product` in `store`.

        Only the goods booked at sale price count: stock entered before the store valuation
        (or while the product was not valued in real time) has no markup to revalue.
        """
        Move = self.env["stock.move"]
        moves = Move.search(
            [
                ("product_id", "=", product.id),
                ("company_id", "=", company.id),
                ("state", "=", "done"),
                ("l10n_ro_store_account_move_id", "!=", False),
                "|",
                ("location_dest_id", "child_of", store.id),
                ("location_id", "child_of", store.id),
            ]
        )
        quantity = sale_amount = tax_amount = 0.0
        for move in moves:
            direction = move._l10n_ro_get_store_direction()
            if direction == "in" and move._l10n_ro_get_store_root_location(move.location_dest_id) == store:
                quantity += move.product_qty
                sale_amount += move.l10n_ro_store_sale_amount
                tax_amount += move.l10n_ro_store_tax_amount
            elif direction == "out" and move._l10n_ro_get_store_root_location(move.location_id) == store:
                quantity -= move.product_qty
                sale_amount -= move.l10n_ro_store_sale_amount
                tax_amount += move.l10n_ro_store_tax_amount  # already negative for an exit
        revaluations = self.search(
            [("product_id", "=", product.id), ("location_id", "=", store.id), ("company_id", "=", company.id)]
        )
        sale_amount += sum(revaluations.mapped("sale_amount"))
        tax_amount += sum(revaluations.mapped("tax_amount"))
        return quantity, sale_amount, tax_amount

    @api.model
    def _get_store_price(self, product, store):
        """Unit sale price, without VAT, of `product` in `store`: the store pricelist, else the product price."""
        if "store_pricelist_id" in store._fields and store.store_pricelist_id:
            return store.store_pricelist_id._get_product_price(product, 1)
        return product.lst_price

    # ------------------------------------------------------------------
    # Revaluation
    # ------------------------------------------------------------------

    @api.model
    def _l10n_ro_revaluate_products(self, products):
        """Revaluate the stock of `products` in every store where the sale price changed."""
        products = products.filtered(lambda p: p.is_storable)
        if not products:
            return self.browse()
        Move = self.env["stock.move"]
        quants = (
            self.env["stock.quant"]
            .sudo()
            .search(
                [
                    ("product_id", "in", products.ids),
                    ("location_id.usage", "=", "internal"),
                    ("location_id.l10n_ro_merchandise_type", "=", "store"),
                ]
            )
        )
        stores = set()
        for quant in quants:
            store = Move._l10n_ro_get_store_root_location(quant.location_id)
            stores.add((quant.product_id, store, quant.company_id))
        revaluations = self.browse()
        for product, store, company in stores:
            revaluations |= self._l10n_ro_revaluate_store(product, store, company)
        return revaluations

    @api.model
    def _l10n_ro_revaluate_store(self, product, store, company, origin_move=None):
        """Bring the stock of `product` booked in `store` to the current store price.

        Called on a sale price change and after a return, which enters or leaves the store
        at the price of the move it returns.
        """
        if not company.l10n_ro_accounting or product.with_company(company).valuation != "real_time":
            return self.browse()
        return self.sudo().with_company(company)._l10n_ro_revaluate(product, store, company, origin_move)

    def _l10n_ro_revaluate(self, product, store, company, origin_move=None):
        currency = company.currency_id
        product = product.with_company(company)
        quantity, old_sale, old_tax = self._get_store_balance(product, store, company)
        if product.uom_id.compare(quantity, 0.0) <= 0:
            # nothing booked at sale price to revaluate
            return self.browse()
        new_price = self._get_store_price(product, store)
        taxes = product.taxes_id.filtered(lambda t: t.company_id in company.parent_ids)
        res = taxes.compute_all(new_price, currency=currency, quantity=quantity, product=product)
        new_sale = currency.round(res["total_included"])
        new_tax = currency.round(res["total_included"] - res["total_excluded"])
        if currency.is_zero(new_sale - old_sale) and currency.is_zero(new_tax - old_tax):
            return self.browse()
        if not origin_move and currency.compare_amounts(new_sale, old_sale) < 0:
            cost = currency.round(quantity * product.standard_price)
            if currency.compare_amounts(new_sale - new_tax, cost) < 0:
                raise UserError(
                    self.env._(
                        "The new sale price without VAT of %(product)s (%(price)s) is below its unit cost "
                        "(%(cost)s) in the store %(store)s. A price cut below cost is not booked as a store "
                        "revaluation: use the impairment procedure (6814 = 397).",
                        product=product.display_name,
                        price=new_price,
                        cost=product.standard_price,
                        store=store.display_name,
                    )
                )
        revaluation = self.create(
            {
                "company_id": company.id,
                "product_id": product.id,
                "location_id": store.id,
                "quantity": quantity,
                "old_price": currency.round((old_sale - old_tax) / quantity),
                "new_price": new_price,
                "origin_move_id": origin_move and origin_move.id,
                # a realignment after a return keeps the date of the return entry
                "date": (
                    origin_move.l10n_ro_store_account_move_id.date
                    if origin_move and origin_move.l10n_ro_store_account_move_id
                    else fields.Date.context_today(self)
                ),
                "old_sale_amount": old_sale,
                "new_sale_amount": new_sale,
                "old_tax_amount": old_tax,
                "new_tax_amount": new_tax,
            }
        )
        revaluation._l10n_ro_create_account_move()
        return revaluation

    def _l10n_ro_get_move_line_vals(self):
        """Lines of the entry: 371 = 378 / 4428 for an increase, 378 / 4428 = 371 in black for a decrease."""
        self.ensure_one()
        accounts = self.product_id.product_tmpl_id.get_product_accounts()
        if not accounts.get("l10n_ro_store_markup"):
            raise UserError(
                self.env._(
                    "Please define a 'Store Markup Account' on the product category '%(categ)s'.",
                    categ=self.product_id.categ_id.display_name,
                )
            )
        if not self.currency_id.is_zero(self.tax_amount) and not accounts.get("l10n_ro_uneligible_tax"):
            raise UserError(
                self.env._(
                    "Please define the 'Not Eligible Tax Account' on the company %(company)s.",
                    company=self.company_id.display_name,
                )
            )
        name = self.env._("%(ref)s - Store revaluation", ref=self.name)
        vals_list = []
        for counterpart, amount in (
            ("l10n_ro_store_markup", self.markup_amount),
            ("l10n_ro_uneligible_tax", self.tax_amount),
        ):
            if self.currency_id.is_zero(amount):
                continue
            debit_key, credit_key = ("stock_valuation", counterpart) if amount > 0 else (counterpart, "stock_valuation")
            common = {"name": name, "product_id": self.product_id.id, "quantity": self.quantity}
            vals_list += [
                dict(common, account_id=accounts[debit_key].id, debit=abs(amount), credit=0.0),
                dict(common, account_id=accounts[credit_key].id, debit=0.0, credit=abs(amount)),
            ]
        return vals_list

    def _l10n_ro_create_account_move(self):
        for revaluation in self:
            line_vals = revaluation._l10n_ro_get_move_line_vals()
            if not line_vals:
                continue
            journal = revaluation.company_id.account_stock_journal_id
            if not journal:
                raise UserError(
                    self.env._(
                        "Please define the stock journal on the company %(company)s.",
                        company=revaluation.company_id.display_name,
                    )
                )
            account_move = self.env["account.move"].create(
                {
                    "ref": revaluation.name,
                    "journal_id": journal.id,
                    "date": revaluation.date,
                    "company_id": revaluation.company_id.id,
                    "line_ids": [Command.create(vals) for vals in line_vals],
                }
            )
            # Odoo would move the entry silently after a lock date; the revaluation keeps
            # the date of the price change, so a locked period refuses it instead.
            if account_move._get_violated_lock_dates(account_move.date, account_move._affect_tax_report()):
                raise UserError(
                    self.env._(
                        "The sale price of %(product)s cannot be changed on %(date)s: the period is locked, "
                        "and the stock of the store %(store)s would need a revaluation entry on that date.",
                        product=revaluation.product_id.display_name,
                        date=revaluation.date,
                        store=revaluation.location_id.display_name,
                    )
                )
            account_move._post()
            revaluation.account_move_id = account_move
