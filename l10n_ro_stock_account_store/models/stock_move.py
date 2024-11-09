# Copyright (C) 2024 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ["stock.move", "l10n.ro.mixin"]

    l10n_ro_sale_price = fields.Float()

    @api.model
    def _get_valued_types(self):
        valued_types = super()._get_valued_types()
        if not self.filtered("is_l10n_ro_record"):
            return valued_types

        valued_types += [
            "reception_store",
            "delivery_store",
        ]
        return valued_types

    def _is_reception_store(self):
        it_is = self._is_in() and self.location_dest_id.l10n_ro_merchandise_type == "store"
        return it_is

    def _is_delivery_store(self):
        it_is = self._is_out() and self.location_id.l10n_ro_merchandise_type == "store"
        return it_is

    def _create_reception_store_svl(self, forced_quantity=None):
        svls = self.env["stock.valuation.layer"]

        return svls

    def _create_delivery_store_svl(self, forced_quantity=None):
        svls = self.env["stock.valuation.layer"]
        return svls

    def _account_entry_move(self, qty, description, svl_id, cost):
        am_vals = super()._account_entry_move(qty, description, svl_id, cost)

        am_val_store = False
        if self._is_reception_store():
            # adaugare nota contabila pentru 378 - adaos comercial
            # adaugare  TVA 4428 - TVA neexigibil
            am_val_store = self._create_account_entry_reception_store(qty, description, svl_id, cost)

        if self._is_delivery_store():
            am_val_store = self._create_account_entry_delivery_store(qty, description, svl_id, cost)

        if am_val_store:
            if am_vals and len(am_vals) == 1:
                am_vals[0]["line_ids"] += am_val_store["line_ids"]
            else:
                am_vals.append(am_val_store)

        return am_vals

    def _create_account_entry_reception_store(self, qty, description, svl_id, cost):
        company = self.company_id or self.env.company
        uneligible_tax_account_id = company.l10n_ro_property_uneligible_tax_account_id.id
        account_difference = self.product_id.categ_id.property_account_creditor_price_difference_categ.id

        if not account_difference:
            raise UserError(
                _("Please define a 'Price Difference Account' on the product category '%s'.")
                % self.product_id.categ_id.name
            )

        prices = self.product_id.taxes_id.compute_all(self.product_id.lst_price, quantity=qty)
        sale_amount = prices["total_excluded"]
        uneligible_tax = prices["total_included"] - prices["total_excluded"]
        self.l10n_ro_sale_price = sale_amount
        (
            journal_id,
            acc_src,
            acc_dest,
            acc_valuation,
        ) = self._get_accounting_data_for_valuation()

        am_vals = self._prepare_account_move_vals(
            account_difference,
            acc_valuation,
            journal_id,
            0,
            description,
            svl_id,
            sale_amount - cost,
        )

        move_ids = self._prepare_account_move_line(
            0, uneligible_tax, uneligible_tax_account_id, acc_valuation, svl_id, description
        )
        am_vals["line_ids"] += move_ids
        return am_vals

    def _create_account_entry_delivery_store(self, qty, description, svl_id, cost):
        company = self.company_id or self.env.company
        uneligible_tax_account_id = company.l10n_ro_property_uneligible_tax_account_id.id
        account_difference = self.product_id.categ_id.property_account_creditor_price_difference_categ.id

        if not account_difference:
            raise UserError(
                _("Please define a 'Price Difference Account' on the product category '%s'.")
                % self.product_id.categ_id.name
            )

        prices = self.product_id.taxes_id.compute_all(self.product_id.lst_price, quantity=qty)
        sale_amount = prices["total_excluded"]
        uneligible_tax = prices["total_included"] - prices["total_excluded"]
        self.l10n_ro_sale_price = sale_amount
        (
            journal_id,
            acc_src,
            acc_dest,
            acc_valuation,
        ) = self._get_accounting_data_for_valuation()

        am_vals = self._prepare_account_move_vals(
            acc_valuation,
            account_difference,
            journal_id,
            0,
            description,
            svl_id,
            sale_amount - cost,
        )

        move_ids = self._prepare_account_move_line(
            0, uneligible_tax, acc_valuation, uneligible_tax_account_id, svl_id, description
        )
        am_vals["line_ids"] += move_ids
        return am_vals
