# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_ro_extra_stock_move_id = fields.Many2one(
        "stock.move",
        string="Romania - Extra Stock Move",
        readonly=True,
    )
    fifo_neg_origin_move_id = fields.Many2one(
        "stock.move",
        string="Source IN move for negative stock compensation",
        index="btree_not_null",
        readonly=True,
        copy=False,
        help="The incoming stock move that triggered this FIFO negative "
        "stock compensation accounting entry.",
    )
