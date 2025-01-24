# Copyright (C) 2024 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import logging

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ["stock.move", "l10n.ro.mixin"]

    @api.model
    def _get_valued_types(self):
        valued_types = super()._get_valued_types()
        if not self.filtered("is_l10n_ro_record"):
            return valued_types

        valued_types += [
            "in_store",
            "out_store",
        ]
        return valued_types

    def _is_in_store(self):
        "Este o intrare in magazie?"
        it_is = (
            self.location_id.l10n_ro_merchandise_type != "store"
            and self.location_dest_id.l10n_ro_merchandise_type == "store"
        )
        return it_is

    def _is_out_store(self):
        "Este o iesire din magazie?"
        it_is = (
            self.location_id.l10n_ro_merchandise_type == "store"
            and self.location_dest_id.l10n_ro_merchandise_type != "store"
        )
        return it_is

    def _create_in_store_svl(self, forced_quantity=None):
        svl_values = self._get_in_svl_vals(self.quantity)
        for svl_value in svl_values:
            svl_value.update(
                {
                    "l10n_ro_valued_type": "in_store",
                    "description": f"Store Evaluation {self.reference} - {self.product_id.name}",
                }
            )
        svls = self.env["stock.valuation.layer"].create(svl_values)
        return svls

    def _create_out_store_svl(self, forced_quantity=None):
        svl_values = self._get_out_svl_vals(self.quantity)
        for svl_value in svl_values:
            svl_value.update(
                {
                    "l10n_ro_valued_type": "out_store",
                    "description": f"Store Evaluation {self.reference} - {self.product_id.name}",
                }
            )
        svls = self.env["stock.valuation.layer"].create(svl_values)
        return svls

    def _account_entry_move(self, qty, description, svl_id, cost):
        am_vals = super()._account_entry_move(qty, description, svl_id, cost)

        svl = self.env["stock.valuation.layer"].browse(svl_id)

        am_val_store = False
        if svl.l10n_ro_valued_type == "in_store":
            am_val_store = self._create_account_entry_in_store(qty, description, svl_id, cost)

        if svl.l10n_ro_valued_type == "out_store":
            am_val_store = self._create_account_entry_out_store(qty, description, svl_id, cost)

        if am_val_store:
            am_vals = [am_val_store]

        return am_vals

    def _create_account_entry_in_store(self, qty, description, svl_id, cost):
        company = self.company_id or self.env.company
        uneligible_tax_account_id = company.l10n_ro_property_uneligible_tax_account_id.id
        account_difference = self.product_id.categ_id.property_account_creditor_price_difference_categ.id

        svl = self.env["stock.valuation.layer"].browse(svl_id)

        if not account_difference:
            raise UserError(
                _("Please define a 'Price Difference Account' on the product category '%s'.")
                % self.product_id.categ_id.name
            )

        prices = self.product_id.taxes_id.compute_all(self.product_id.lst_price, quantity=qty)
        sale_amount = prices["total_excluded"]
        uneligible_tax = prices["total_included"] - prices["total_excluded"]

        # svl_value = prices["total_included"] - cost
        svl.write(
            {
                "value": 0,
                "quantity": 0,
                "remaining_qty": 0,
                "remaining_value": 0,
                "l10n_ro_sale_amount": prices["total_included"],
            }
        )

        (
            journal_id,
            acc_src,
            acc_dest,
            acc_valuation,
        ) = self.with_context(valued_type='internal_transfer')._get_accounting_data_for_valuation()

        am_vals = self._prepare_account_move_vals(
            account_difference,
            acc_dest,
            journal_id,
            0,
            description,
            svl_id,
            (sale_amount - cost),
        )

        move_ids = self._prepare_account_move_line(
            0, uneligible_tax, uneligible_tax_account_id, acc_dest, svl_id, description
        )
        am_vals["line_ids"] += move_ids
        return am_vals

    def _create_account_entry_out_store(self, qty, description, svl_id, cost):
        company = self.company_id or self.env.company
        uneligible_tax_account_id = company.l10n_ro_property_uneligible_tax_account_id.id
        account_difference = self.product_id.categ_id.property_account_creditor_price_difference_categ.id

        if not account_difference:
            raise UserError(
                _("Please define a 'Price Difference Account' on the product category '%s'.")
                % self.product_id.categ_id.name
            )

        prices = self.product_id.taxes_id.compute_all(self.product_id.lst_price, quantity=qty)
        standard_price = self.product_id.standard_price
        sale_amount = prices["total_excluded"]
        uneligible_tax = prices["total_included"] - prices["total_excluded"]

        svl = self.env["stock.valuation.layer"].browse(svl_id)

        # svl_value = prices["total_included"] - standard_price * qty
        svl.write(
            {
                "value": 0,
                "quantity": 0,
                "remaining_qty": 0,
                "remaining_value": 0,
                "l10n_ro_sale_amount": prices["total_included"],
            }
        )

        (
            journal_id,
            acc_src,
            acc_dest,
            acc_valuation,
        ) = self.with_context(valued_type='internal_transfer')._get_accounting_data_for_valuation()

        am_vals = self._prepare_account_move_vals(
            acc_src,
            account_difference,
            journal_id,
            0,
            description,
            svl_id,
            -1 * (sale_amount - standard_price * qty),
        )

        move_ids = self._prepare_account_move_line(
            0, -1 * (uneligible_tax), acc_src, uneligible_tax_account_id, svl_id, description
        )
        am_vals["line_ids"] += move_ids
        return am_vals
