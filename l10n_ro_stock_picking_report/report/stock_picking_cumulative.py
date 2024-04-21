# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import pytz
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class StockPickingCumulative(models.TransientModel):
    _name = "stock.picking.cumulative"
    _description = "StockPickingCumulative"

    name = fields.Char()
    state = fields.Char()
    date = fields.Char()
    location_id = fields.Many2one("stock.location")
    location_dest_id = fields.Many2one("stock.location")
    partner_id = fields.Many2one("res.partner")
    note = fields.Char()

    date_from = fields.Date("Start Date", required=True, default=fields.Date.today)
    date_to = fields.Date("End Date", required=True, default=fields.Date.today)
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    picking_type_id = fields.Many2one(
        "stock.picking.type", string="Picking Type", required=True
    )
    picking_type_code = fields.Selection(related="picking_type_id.code")
    origin = fields.Char()
    group_id = fields.Char()
    date_done = fields.Datetime()

    report_id = fields.Many2one(
        "ir.actions.report",
        required=True,
        domain=[("model", "=", "stock.picking.cumulative")],
    )

    move_ids = fields.Many2many("stock.move")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        today = fields.Date.context_today(self)
        today = fields.Date.from_string(today)

        from_date = today + relativedelta(day=1, months=0, days=0)
        to_date = today + relativedelta(day=1, months=1, days=-1)

        res["date_from"] = fields.Date.to_string(from_date)
        res["date_to"] = fields.Date.to_string(to_date)
        res["date_done"] = fields.Datetime.to_string(to_date)
        return res

    def button_show(self):
        datetime_from = fields.Datetime.to_datetime(self.date_from)
        datetime_from = fields.Datetime.context_timestamp(self, datetime_from)
        datetime_from = datetime_from.replace(hour=0)
        datetime_from = datetime_from.astimezone(pytz.utc)

        datetime_to = fields.Datetime.to_datetime(self.date_to)
        datetime_to = fields.Datetime.context_timestamp(self, datetime_to)
        datetime_to = datetime_to.replace(hour=23, minute=59, second=59)
        datetime_to = datetime_to.astimezone(pytz.utc)

        domain = [
            ("date", ">=", datetime_from),
            ("date", "<=", datetime_to),
            ("state", "=", "done"),
            ("picking_type_id", "=", self.picking_type_id.id),
        ]
        move_ids = self.env["stock.move"].search(domain)

        self.write({"move_ids": [(6, 0, move_ids.ids)]})

        return self.report_id.report_action(self, config=False)
