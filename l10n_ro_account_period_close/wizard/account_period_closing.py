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
from openerp.exceptions import Warning

class account_period_closing_wizard(models.TransientModel):
    _name = "account.period.closing.wizard"
    _description = "Wizard for Account Period Closing"

    @api.model
    def default_get(self, fields):      
        defaults = super(account_period_closing_wizard, self).default_get(fields)
        return defaults
    
    @api.onchange('period_id')
    def onchange_period(self):      
        if self.period_id:
            self.date_from = self.period_id.date_start
            self.date_to = self.period_id.date_stop
    
    @api.one
    def do_close(self):
        wizard = self[0]
        if wizard.date_from < wizard.period_id.date_start or wizard.date_from > self.period_id.date_stop or \
                wizard.date_to < self.period_id.date_start or wizard.date_to > self.period_id.date_stop:
            raise Warning(_('Dates selected must be in the same period.'))
        if not wizard.done:
            wizard.closing_id.close(
                wizard.date_from, wizard.date_to, wizard.period_id.id, wizard.journal_id.id)
        return {'type': 'ir.actions.act_window_close'}

    closing_id = fields.Many2one(
        'account.period.closing',
        'Closing Model',
        required=True,
        ondelete='cascade'
    )
    company_id = fields.Many2one(
        'res.company', related='closing_id.company_id', string='Company')
    date_from = fields.Date('Closing Date From', required=True, select=True)
    date_to = fields.Date('Closing Date To', required=True, select=True,
                          help='Created moves will have this as a date.')
    period_id = fields.Many2one(
        'account.period', 'Closing Period', required=True)
    journal_id = fields.Many2one(
        'account.journal', 'Closing Journal', required=True)
    done = fields.Boolean('Closing Done')