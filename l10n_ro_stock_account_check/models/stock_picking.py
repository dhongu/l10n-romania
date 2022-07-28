# ©  2015-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    notice = fields.Boolean(
        "Is a notice",
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
        default=False,
        help="With this field the reception/delivery is set as a notice. "
        "The generated account move will contain accounts 408/418.",
    )

    def correction_valuation(self):
        for picking in self:
            picking.move_lines.correction_valuation()


