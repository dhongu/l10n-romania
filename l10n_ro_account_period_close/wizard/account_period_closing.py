# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2014 FOREST AND BIOMASS SERVICES ROMANIA SA
#    (http://www.forbiom.eu).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _


class account_period_closing_wizard(models.TransientModel):
    _name = "account.period.closing.wizard"
    _description = "Wizard for Account Period Closing"


    @api.model
    def default_get(self, fields):      
        defaults = super(account_period_closing_wizard, self).default_get(fields)
        return defaults



    @api.one
    def do_close(self):
        wizard = self[0]
        if not wizard.done:
            wizard.closing_id.close( wizard.date_move, wizard.period_id.id, wizard.journal_id.id)
        return {'type': 'ir.actions.act_window_close'}

    closing_id = fields.Many2one('account.period.closing',string='Closing Model',required=True,ondelete='cascade' )
    company_id = fields.Many2one('res.company', related='closing_id.company_id', string='Company')
    date_move = fields.Date(string='Closing Move Date', required=True, select=True)
    period_id = fields.Many2one( 'account.period', string='Closing Period', required=True)
    journal_id = fields.Many2one( 'account.journal', string='Closing Journal', required=True)
    done = fields.Boolean(string='Closing Done')



class account_period_close(models.TransientModel):
    _inherit = "account.period.close"

    date_move = fields.Date(string='Closing Move Date', required=True, select=True)
    journal_id = fields.Many2one( 'account.journal', string='Closing Journal', required=True)
  
    @api.one
    def data_save(self):
        for period_id in self.env.context['active_ids']:
            for period_closing in self.env['account.period.closing'].search([]):
                period_closing.close(self.date_move, period_id, self.journal_id.id)
        
        return super(account_period_close,self).data_save()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
