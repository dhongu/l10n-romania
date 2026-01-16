from odoo import models, fields, _, api

class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _l10n_ro_edi_stock_validate_carrier_filter(self, picking):
        validate_carrier = self.env.context.get('l10n_ro_edi_stock_validate_carrier', False)
        if picking.picking_type_id.code in ['internal', 'mrp_operation']:
            validate_carrier = False
        return picking.company_id.account_fiscal_country_id.code == 'RO' and (picking.l10n_ro_edi_stock_enable or validate_carrier)