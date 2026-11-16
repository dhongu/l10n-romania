# Copyright (C) 2024 NextERP Romania
from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    l10n_ro_last_in_date = fields.Datetime(string="Last In Date", help="Last delivery date")
    l10n_ro_last_out_date = fields.Datetime(string="Last Out Date", help="Last out date")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("quantity", 0) > 0:
                vals["l10n_ro_last_in_date"] = fields.Datetime.now()
            elif vals.get("quantity", 0) < 0:
                vals["l10n_ro_last_out_date"] = fields.Datetime.now()
        return super().create(vals_list)

    def write(self, vals):
        if "quantity" in vals:
            for quant in self:
                if vals["quantity"] > quant.quantity:
                    vals["l10n_ro_last_in_date"] = fields.Datetime.now()
                elif vals["quantity"] < quant.quantity:
                    vals["l10n_ro_last_out_date"] = fields.Datetime.now()
        return super().write(vals)
