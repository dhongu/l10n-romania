# Copyright (C) 2022 NextERP Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    l10n_ro_notice_default = fields.Boolean(
        string="Romania - Is a notice",
        help="Transfers created for this operation type are marked as notice (aviz) by default.",
    )


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def default_get(self, fields_list):
        """Web form: the client sends l10n_ro_notice explicitly, so create() alone
        is not enough; set the flag from the operation type on a new record."""
        res = super().default_get(fields_list)
        if "l10n_ro_notice" in fields_list and "l10n_ro_notice" not in res and res.get("picking_type_id"):
            picking_type = self.env["stock.picking.type"].browse(res["picking_type_id"])
            if picking_type.l10n_ro_notice_default:
                res["l10n_ro_notice"] = True
        return res

    @api.onchange("picking_type_id")
    def _onchange_picking_type_id_l10n_ro_notice(self):
        if self.picking_type_id:
            self.l10n_ro_notice = self.picking_type_id.l10n_ro_notice_default

    @api.model_create_multi
    def create(self, vals_list):
        """Set the notice flag from the operation type, whatever the source of the
        transfer (purchase, sale, manual). The user can change it afterwards."""
        picking_types = self.env["stock.picking.type"]
        for vals in vals_list:
            if "l10n_ro_notice" not in vals and vals.get("picking_type_id"):
                picking_type = picking_types.browse(vals["picking_type_id"])
                if picking_type.l10n_ro_notice_default:
                    vals["l10n_ro_notice"] = True
        return super().create(vals_list)
