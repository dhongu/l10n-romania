# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Deltatech All Rights Reserved
#                    Dorin Hongu <dhongu(@)gmail(.)com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################




from odoo import models, fields, api, _
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo import SUPERUSER_ID, api
import odoo.addons.decimal_precision as dp


class res_partner(models.Model):
    _inherit = 'res.partner'
    mean_transp = fields.Char(string='Mean transport')


class stock_location(models.Model):
    _inherit = "stock.location"
    user_id = fields.Many2one('res.users', string='Manager')


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    origin = fields.Char(states={'done': [('readonly', False)]})
    delegate_id = fields.Many2one('res.partner', string='Delegate')
    mean_transp = fields.Char(string='Mean transport')


    '''
    invoice_state = fields.Selection([("invoiced", "Invoiced"),
                                      ("2binvoiced", "To Be Invoiced"),
                                      ("none", "Not Applicable")
                                      ], string="Invoice Control")
    '''

    @api.onchange('delegate_id')
    def on_change_delegate_id(self):
        if self.delegate_id:
            self.mean_transp = self.delegate_id.mean_transp

    # metoda locala sau se poate in 10 are alt nume
    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        res = super(stock_picking, self)._get_invoice_vals(key, inv_type, journal_id, move)
        if inv_type == 'out_invoice':
            res['delegate_id'] = move.picking_id.delegate_id.id
            res['mean_transp'] = move.picking_id.mean_transp
        return res

    """
    @api.multi
    def action_invoice_create(self,   journal_id=False, group=False, type='out_invoice' ):
        invoices = []
        
        if type == 'out_invoice':
            context = {}
            for picking in self :
                context = self._context.copy()
                context['default_delegate_id'] = picking.delegate_id.id
                context['default_mean_transp'] = picking.mean_transp
        picking = self.with_context(context)       
        invoices = super(stock_picking, picking ).action_invoice_create(journal_id, group, type)

        return invoices
    """

    @api.multi
    def do_print_picking(self):
        self.write({'printed': True})
        if self.picking_type_code == 'incoming':
            res = self.env['report'].get_action(self, 'l10n_ro_stock_picking_report.report_reception')
        elif self.picking_type_code == 'outgoing':
            res = self.env['report'].get_action(self, 'l10n_ro_stock_picking_report.report_delivery')
        else:
            res = self.env['report'].get_action(self, 'l10n_ro_stock_picking_report.report_internal_transfer')
        return res

