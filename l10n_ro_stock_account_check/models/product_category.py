# ©  2008-2018 Fekete Mihai <mihai.fekete@forbiom.eu>
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import models


class ProductCategory(models.Model):
    _inherit = "product.category"

    def propagate_account(self):
        for categ in self:
            childs = self.search([("id", "child_of", [categ.id])])

            values = {
                # Cont diferență de preț
                "property_account_creditor_price_difference_categ": self.property_account_creditor_price_difference_categ.id,
                # Cont de cheltuieli
                "property_account_expense_categ_id": self.property_account_expense_categ_id.id,
                # Cont de venituri
                "property_account_income_categ_id": self.property_account_income_categ_id.id,
                #  Cont Intrare Stoc
                "property_stock_account_input_categ_id": self.property_stock_account_input_categ_id.id,
                # Cont ieșire din stoc
                "property_stock_account_output_categ_id": self.property_stock_account_output_categ_id.id,
                # Cont Evaluare  Stoc
                "property_stock_valuation_account_id": self.property_stock_valuation_account_id.id,
                # Jurnal de stoc
                "property_stock_journal": self.property_stock_journal.id,
                # Metodă de cost
                "property_cost_method": self.property_cost_method,
                # property_valuation
                "property_valuation": self.property_valuation,
            }
            childs.write(values)
