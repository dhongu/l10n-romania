# ©  2008-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    mean_transp = fields.Char(string="Mean transport")


class StockMove(models.Model):
    _inherit = "stock.move"

    l10n_ro_sale_price = fields.Float(
        string="Sale Price (at reception)",
        digits="Product Price",
        help="Prețul de vânzare al produsului la momentul validării recepției. "
             "Folosit în raportul NIR pentru a evita modificările ulterioare ale prețului de vânzare.",
    )

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        for move in self:
            if move.picking_id.picking_type_code == "incoming" and not move.l10n_ro_sale_price:
                list_price = move.product_id.list_price
                if move.location_dest_id.store_pricelist_id:
                    list_price = move.location_dest_id.store_pricelist_id._get_product_price(
                        move.product_id, 1, False
                    )
                move.l10n_ro_sale_price = list_price
        return res
