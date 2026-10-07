# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _l10n_ro_etransport_declaration_record(self, data):
        """Pe calea de lot, înregistrarea care declară e lotul.

        `l10n_ro_edi_stock_batch` construiește declarația lotului apelând
        `self.env["stock.picking"]._l10n_ro_edi_stock_get_template_data(data)`,
        cu `self` GOL. Override-urile definite pe `stock.picking.batch` nu sunt
        apelate niciodată, iar cele de pe transfer nu au de unde citi greutățile
        cântărite, documentele sau marcajul post-avarie ale lotului: declarația
        pleca tăcut cu greutățile nucleului și un singur aviz.

        Lotul se deduce din mișcările declarate, ca în
        `_l10n_ro_edi_stock_validate_data`. Numele trebuie să coincidă cu
        `refDeclarant` (nucleul batch pune acolo numele lotului), ca să nu
        atribuim lotului o declarație făcută pe un transfer.
        """
        record = super()._l10n_ro_etransport_declaration_record(data)
        if record:
            return record
        batch = data["stock_move_ids"].picking_id.batch_id
        if len(batch) == 1 and batch.name == data.get("name"):
            return batch
        return record
