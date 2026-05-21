# Part of Odoo. See LICENSE file for full copyright and licensing details.


from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models

_interval = {
    "15": lambda count: relativedelta(days=count * 15),
    "30": lambda count: relativedelta(days=count * 30),
    "90": lambda count: relativedelta(days=count * 90),
    "180": lambda count: relativedelta(days=count * 180),
    "365": lambda count: relativedelta(days=count * 365),
}

NUMBER_INTERVALS = 6


class StockAgeReportLocation(models.TransientModel):
    _name = "l10n.ro.stock.age.report.location"
    _description = "Stock Age Report Location"
    _order = "sequence, id"

    sequence = fields.Integer(string="Sequence", default=10)
    location_id = fields.Many2one(
        "stock.location",
        string="Location",
    )
    report_id = fields.Many2one(
        "l10n.ro.stock.age.report",
        string="Report",
    )


class StockAgeReport(models.TransientModel):
    _name = "l10n.ro.stock.age.report"
    _description = "Stock Age Report"
    _check_company_auto = True

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    product_id = fields.Many2one("product.product", "Related product", check_company=True)
    date_ref = fields.Date("Reference Date", default=fields.Date.today)

    interval_days = fields.Selection(
        string="Days",
        selection=[("15", "15 days"), ("30", "30 days"), ("90", "90 days"), ("180", "180 days"), ("365", "365 days")],
        default="15",
    )

    location_ids = fields.One2many(
        "l10n.ro.stock.age.report.location",
        "report_id",
        string="Locations",
        compute="_compute_location_ids",
        store=True,
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        required=True,
        string="Warehouse",
        readonly=False,
        help="Warehouse to consider for the route selection",
    )
    line_ids = fields.One2many(
        "l10n.ro.stock.age.report.line",
        "report_id",
        string="Report Lines",
    )

    def name_get(self):
        res = []
        for rep in self:
            name = "Stock Age Report: {} (interval: {})".format(
                rep.date_ref, dict(self._fields["interval_days"].selection).get(rep.interval_days)
            )
            res.append((rep.id, name))
        return res

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        warehouse = self.env["stock.warehouse"].search([("company_id", "=", self.env.company.id)], limit=1)
        res["warehouse_id"] = warehouse.id
        return res

    @api.depends("warehouse_id")
    def _compute_location_ids(self):
        self.location_ids = [(6, 0, [])]

        locs = self.env["stock.location"].search([("usage", "=", "internal")], order="id")
        locs = locs.filtered(lambda l: l.warehouse_id == self.warehouse_id)
        location_ids = []
        idx = 10
        for loc in locs:
            location_ids.append((0, 0, {"sequence": idx, "location_id": loc.id}))
            idx += 10
        self.location_ids = location_ids

    def do_compute_report(self):
        products = self.product_id or self.env["product.product"].search([])
        locations = self.location_ids.mapped("location_id")

        self._run_aged_inventory(products, locations.ids)

        return True

    def _run_aged_inventory(self, products, locations):
        self = self.sudo()

        def _to_str(date):
            return fields.Date.to_string(date)

        date_ref = self.date_ref

        # Pregătim intervalele
        intervals = []
        for i in range(NUMBER_INTERVALS):
            date_to = date_ref - _interval[self.interval_days](i)
            date_from = date_ref - _interval[self.interval_days](i + 1)

            days = (date_ref - date_to).days
            days_next = (date_ref - date_from).days
            name = f"{days} - {days_next}"
            if i == NUMBER_INTERVALS - 1:
                name += "+"
            name = f"[{i + 1}] {name} " + _("days")

            intervals.append(
                {
                    "date": date_to,
                    "date_from": date_from,
                    "name": name,
                }
            )

        # Căutăm quants
        quants = self.env["stock.quant"].search(
            [("product_id", "in", products.ids), ("location_id", "in", locations), ("quantity", ">", 0)]
        )

        for quant in quants:
            product = quant.product_id
            # Folosim noul câmp, sau in_date, sau create_date ca fallback
            in_date_val = quant.l10n_ro_last_in_date or quant.in_date or quant.create_date
            if not in_date_val:
                in_date = date_ref
            elif isinstance(in_date_val, str):
                in_date = fields.Date.from_string(in_date_val[:10])
            else:
                in_date = in_date_val.date()

            # Găsim intervalul
            target_interval = intervals[NUMBER_INTERVALS - 1]  # default cel mai vechi
            for i in range(NUMBER_INTERVALS - 1):
                if intervals[i]["date"] >= in_date > intervals[i]["date_from"]:
                    target_interval = intervals[i]
                    break

            # Contul de stoc
            account_id = False
            if (
                hasattr(product, "l10n_ro_property_stock_valuation_account_id")
                and product.l10n_ro_property_stock_valuation_account_id
            ):
                account_id = product.l10n_ro_property_stock_valuation_account_id.id
            elif product.categ_id.property_stock_valuation_account_id:
                account_id = product.categ_id.property_stock_valuation_account_id.id

            # Valoarea (calculată pe baza prețului standard dacă nu avem tracking)
            value = quant.quantity * product.standard_price

            # Inserăm linia
            self.env["l10n.ro.stock.age.report.line"].create(
                {
                    "report_id": self.id,
                    "name": target_interval["name"],
                    "date": target_interval["date"],
                    "product_id": product.id,
                    "account_id": account_id,
                    "quantity": quant.quantity,
                    "value": value,
                    "last_out_date": quant.l10n_ro_last_out_date,
                }
            )

    def button_show_sheet(self):
        self.do_compute_report()
        action = self.env["ir.actions.actions"]._for_xml_id("l10n_ro_stock_age_report.action_sheet_age_report_line")

        action["display_name"] = "{} {} ({})".format(action["name"], self.date_ref, self.interval_days)
        action["domain"] = [("report_id", "=", self.id)]
        action["target"] = "main"
        return action


class StockAgeReportLine(models.TransientModel):
    _name = "l10n.ro.stock.age.report.line"
    _description = "Stock Age Report Line"
    _order = "date desc"

    report_id = fields.Many2one("l10n.ro.stock.age.report", readonly=True)
    name = fields.Char(string="Days Range", readonly=True)
    date = fields.Date(readonly=True)
    product_id = fields.Many2one("product.product", readonly=True)
    internal_reference = fields.Char("Internal Reference", related="product_id.default_code", readonly=True)
    product_uom = fields.Many2one("uom.uom", string="UM", related="product_id.uom_id", readonly=True)
    account_id = fields.Many2one("account.account", readonly=True)
    quantity = fields.Float("Quantity", readonly=True)
    value = fields.Float("Value", readonly=True)
    last_out_date = fields.Datetime("Last Out Date", readonly=True)

    def action_show_products(self):
        products = self.mapped("product_id")
        action = self.env["ir.actions.actions"]._for_xml_id("product.product_normal_action_sell")
        action["domain"] = [("id", "in", products.ids)]
        action["context"] = {"default_is_storable": True}
        return action
