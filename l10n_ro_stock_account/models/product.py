# -*- coding: utf-8 -*-
# ©  2008-2018 Fekete Mihai <mihai.fekete@forbiom.eu>
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _convert_prepared_anglosaxon_line(self, line, partner):
        res = super(ProductProduct, self)._convert_prepared_anglosaxon_line( line, partner)
        res['stock_location_id'] = line.get('stock_location_id', False)
        return res



    @api.multi
    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        if 'list_price' in vals:
            self.do_change_list_price(vals['list_price'])
        return res

    @api.multi
    def do_change_list_price(self, new_price):
        """ Changes the Standard Price of Product and creates an account move accordingly."""
        AccountMove = self.env['account.move']

        quant_locs = self.env['stock.quant'].sudo().read_group([('product_id', 'in', self.ids)], ['location_id'],
                                                               ['location_id'])
        quant_loc_ids = [loc['location_id'][0] for loc in quant_locs]
        locations = self.env['stock.location'].search(
            [('usage', '=', 'internal'), ('company_id', '=', self.env.user.company_id.id), ('id', 'in', quant_loc_ids)])


        product_accounts = {product.id: product.product_tmpl_id.get_product_accounts() for product in self}
        ref = self.env.context.get('ref',_('Price changed'))
        to_date = fields.Date.today()
        for location in locations.filtered(lambda r: r.merchandise_type == 'store'):
            for product in self.with_context(location=location.id, compute_child=False, to_date=to_date).filtered(
                    lambda r: r.valuation == 'real_time'):

                if not product_accounts[product.id].get('stock_valuation', False):
                    raise UserError(_(
                        'You don\'t have any stock valuation account defined on your product category. You must define one before processing this operation.'))

                account_id = product.property_account_creditor_price_difference
                if not account_id:
                    account_id = product.categ_id.property_account_creditor_price_difference_categ
                if not account_id:
                    raise UserError(_(
                        'Configuration error. Please configure the price difference account on the product or its category to process this operation.'))
                qty_available = product.qty_available
                if qty_available:
                    # Accounting Entries
                    old_price = abs( product.stock_value / qty_available )
                    diff = old_price - new_price
                    if diff * qty_available > 0:
                        debit_account_id = account_id
                        credit_account_id = product_accounts[product.id]['stock_valuation'].id
                    else:
                        debit_account_id = product_accounts[product.id]['stock_valuation'].id
                        credit_account_id = account_id

                    move_vals = {
                        'journal_id': product_accounts[product.id]['stock_journal'].id,
                        'company_id': location.company_id.id,
                        'ref':ref,
                        'line_ids': [(0, 0, {
                            'name': _('Standard Price changed  - %s') % (product.display_name),
                            'account_id': debit_account_id,
                            'debit': abs(diff * qty_available),
                            'credit': 0,
                            'stock_location_id':location.id,
                        }), (0, 0, {
                            'name': _('Standard Price changed  - %s') % (product.display_name),
                            'account_id': credit_account_id,
                            'debit': 0,
                            'credit': abs(diff * qty_available),
                            'stock_location_id': location.id,
                        })],
                    }
                    move = AccountMove.create(move_vals)
                    move.post()

        self.write({'standard_price': new_price})
        return True
