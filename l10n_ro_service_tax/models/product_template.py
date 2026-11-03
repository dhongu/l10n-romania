# © 2026 Terrabit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.onchange("type")
    def _onchange_type(self):
        res = super()._onchange_type()
        company = self.company_id or self.env.company
        sale_tax = company.l10n_ro_account_serv_sale_tax_id
        purchase_tax = company.l10n_ro_account_serv_purchase_tax_id
        if self.type == "service":
            if sale_tax:
                self.taxes_id = sale_tax
            if purchase_tax:
                self.supplier_taxes_id = purchase_tax
        else:
            # la ieșirea din serviciu, taxele de serviciu revin la cele implicite ale companiei;
            # în onchange, x2many conține înregistrări noi: se compară după _origin
            if sale_tax and self.taxes_id._origin == sale_tax:
                self.taxes_id = company.account_sale_tax_id
            if purchase_tax and self.supplier_taxes_id._origin == purchase_tax:
                self.supplier_taxes_id = company.account_purchase_tax_id
        return res
