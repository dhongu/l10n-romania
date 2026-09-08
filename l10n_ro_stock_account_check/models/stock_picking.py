# ©  2015-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def correction_valuation(self):
        for picking in self:
            # Up to 18.0 this called `move_line_ids`, which is stock.move.line
            # and never carried `correction_valuation` - the picking action was
            # a no-op that raised.  The valuation lives on the moves.
            picking.move_ids.correction_valuation()
