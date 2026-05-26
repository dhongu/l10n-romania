# Copyright (C) 2024 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StorageSheetLine(models.TransientModel):
    _inherit = "l10n.ro.stock.storage.sheet.line"

    valued_type = fields.Selection(
        selection_add=[("dropship", "Dropship")],
        ondelete={"dropship": "cascade"},
    )
