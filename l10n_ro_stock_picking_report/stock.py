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

 


from openerp import models, fields, api, _
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import SUPERUSER_ID, api
import openerp.addons.decimal_precision as dp



class stock_picking(models.Model):
    _inherit = 'stock.picking'

    delegate_id =  fields.Many2one('res.partner', string='Delegate')
    mean_transp =  fields.Char(string='Mean transport', size=20)



    @api.multi
    def action_invoice_create(self,   journal_id=False, group=False, type='out_invoice' ):
        invoices = []
        context = {}
        if type == 'out_invoice':
            for picking in self :
                context = {}
                context['default_delegate_id'] = picking.delegate_id.id
                context['default_mean_transp'] = picking.mean_transp
        self = self.with_context(context)       
        invoices = super(stock_picking, self).action_invoice_create(journal_id, group, type)

        return invoices


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
