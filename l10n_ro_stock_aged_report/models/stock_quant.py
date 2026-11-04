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
        if "quantity" not in vals:
            return super().write(vals)
        # datele se decid per cuantă: un write pe mai multe cuante poate fi intrare pentru
        # unele și ieșire pentru altele, deci nu se pun în `vals`, comun tuturor
        quantity = vals["quantity"]
        incoming = self.filtered(lambda q: quantity > q.quantity)
        outgoing = self.filtered(lambda q: quantity < q.quantity)
        res = super().write(vals)
        now = fields.Datetime.now()
        if incoming:
            super(StockQuant, incoming).write({"l10n_ro_last_in_date": now})
        if outgoing:
            super(StockQuant, outgoing).write({"l10n_ro_last_out_date": now})
        return res
