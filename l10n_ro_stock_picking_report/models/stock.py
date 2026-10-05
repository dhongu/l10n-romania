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
        copy=False,
        help="Prețul de vânzare al produsului la momentul validării recepției. "
        "Folosit în raportul NIR pentru a evita modificările ulterioare ale prețului de vânzare.",
    )

    def _l10n_ro_get_reception_sale_price(self):
        """Prețul de vânzare (pe unitatea produsului) cu care marfa intră în locație: din lista
        de prețuri a locației (`store_pricelist_id`), altfel prețul produsului (al variantei)."""
        self.ensure_one()
        pricelist = self.location_dest_id.store_pricelist_id
        if pricelist:
            return pricelist._get_product_price(self.product_id, 1)
        return self.product_id.lst_price

    def _l10n_ro_freeze_sale_price(self):
        for move in self:
            if move.picking_id.picking_type_code == "incoming" and not move.l10n_ro_sale_price:
                move.l10n_ro_sale_price = move._l10n_ro_get_reception_sale_price()

    def _action_done(self, cancel_backorder=False):
        # Prețul se fixează înainte de super(): notele contabile ale recepției se creează acolo,
        # inclusiv adaosul și TVA neexigibilă ale magazinului (`l10n_ro_stock_account_store`),
        # care trebuie să folosească același preț ca NIR-ul. După super(), pentru mișcările
        # create la validare.
        self._l10n_ro_freeze_sale_price()
        res = super()._action_done(cancel_backorder=cancel_backorder)
        res._l10n_ro_freeze_sale_price()
        return res
