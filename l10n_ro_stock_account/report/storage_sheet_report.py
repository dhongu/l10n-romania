# -*- coding: utf-8 -*-
# ©  2008-2018 Fekete Mihai <mihai.fekete@forbiom.eu>
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class StorageSheetReport(models.TransientModel):
    _name = 'l10n_ro.storage_sheet_report'
    _description = 'Storage sheet'

    # Filters fields, used for data computation

    location_id = fields.Many2one('stock.location', domain="[('usage','=','internal'),('company_id','=',company_id)]",
                                  required=True)

    date_range_id = fields.Many2one('date.range', string='Date range')
    date_from = fields.Date('Start Date', required=True, default=fields.Date.today)
    date_to = fields.Date('End Date', required=True, default=fields.Date.today)

    product_id = fields.Many2one('product.product', string='Product', required=True,
                                 domain=[('type', '=', 'product')] )

    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id)

    line_product_ids = fields.One2many('l10n_ro.storage_sheet_report.line', 'report_id')

    @api.model
    def default_get(self, fields_list):
        defaults = super(StorageSheetReport, self).default_get(fields_list)

        active_model = self.env.context.get('active_model', False)
        active_ids = self.env.context.get('active_ids', False)
        active_id = self.env.context.get('active_id', False)
        if active_model == 'product.template':
            product = self.env['product.product'].search([('product_tmpl_id', 'in', active_ids)], limit=1)
            defaults['product_id'] = product.id
        elif active_model == 'product.product':
            defaults['product_id'] = active_id


        # today = fields.Date.context_today(self)
        # today = fields.Date.from_string(today)
        #
        # from_date = (today + relativedelta(day=1, months=0, days=0))
        # to_date = (today + relativedelta(day=1, months=1, days=-1))
        #
        # defaults['date_from'] = fields.Date.to_string(from_date)
        # defaults['date_to'] = fields.Date.to_string(to_date)
        return defaults

    @api.onchange('date_range_id')
    def onchange_date_range_id(self):
        """Handle date range change."""
        if self.date_range_id:
            self.date_from = self.date_range_id.date_start
            self.date_to = self.date_range_id.date_end

    @api.multi
    def do_compute(self):
        self.env['account.move.line'].check_access_rights('read')
        if not self.product_id.categ_id.property_stock_valuation_account_id:
            raise ValidationError(_("You should have defined an 'Valuation Account' on category %s") % self.product_id.categ_id.name)


        valuations = [self.product_id.categ_id.property_stock_valuation_account_id.id]
        if self.location_id.valuation_in_account_id.id and \
                self.location_id.valuation_in_account_id.id not in valuations:
            valuations.append(self.location_id.valuation_in_account_id.id)
        if self.location_id.valuation_out_account_id.id and \
                self.location_id.valuation_out_account_id.id not in valuations:
            valuations.append(self.location_id.valuation_out_account_id.id)


        lines = self.env['l10n_ro.storage_sheet_report.line'].search([('report_id', '=', self.id)])
        lines.unlink()

        to_date = self.date_from
        query = """SELECT aml.product_id, aml.account_id, sum(aml.debit) - sum(aml.credit), 
                    sum(CASE WHEN stock_location_dest_id = %(location)s THEN -1*quantity
                        ELSE quantity
                        END), 
                    array_agg(aml.id)
                        FROM  account_move_line AS aml 
                            WHERE 
                                aml.account_id in %(valuations)s and
                                aml.product_id= %(product)s AND 
                                    aml.company_id=%(company)s AND 
                                    aml.date < %(date)s AND 
                                   ( stock_location_id = %(location)s OR stock_location_dest_id = %(location)s) 
                            GROUP BY aml.product_id, aml.account_id """

        params = {
            'location': self.location_id.id,
            'product': self.product_id.id,
            'company': self.company_id.id,
            'date': to_date,
            'valuations':tuple(valuations)
        }

        self.env.cr.execute(query, params=params)

        res = self.env.cr.fetchall()
        for row in res:
            values = {
                'report_id': self.id,
                'product_id': row[0],
                'account_id': row[1],
                'amount': row[2],
                'quantity': row[3],
                'type': 'balance',
                'aml_ids': [(6, 0, list(row[4]))]
            }
            self.env['l10n_ro.storage_sheet_report.line'].create(values)
        if not res:
            values = {
                'report_id': self.id,
                'product_id': self.product_id.id,
                'date': self.date_from,
                'type': 'balance',
            }
            self.env['l10n_ro.storage_sheet_report.line'].create(values)

        query = """SELECT  aml.product_id, aml.account_id, sum(aml.debit) - sum(aml.credit), 
                        sum(CASE WHEN stock_location_dest_id = %(location)s THEN -1*quantity
                            ELSE quantity
                            END),  aml.date,
                        array_agg(aml.id), COALESCE(aml.ref, aml.name) 
                         FROM account_move_line AS aml
                              WHERE 
                              aml.account_id in %(valuations)s and
                              aml.product_id =%(product)s AND 
                                       aml.company_id=%(company)s AND 
                                       aml.date >= %(date_from)s AND aml.date  <= %(date_to)s AND
                                        ( stock_location_id = %(location)s OR stock_location_dest_id = %(location)s) AND
                                       (aml.debit  -  aml.credit) >= 0 
                              GROUP BY aml.date, aml.product_id, aml.account_id, aml.ref, aml.name"""

        params = {
            'location': self.location_id.id,
            'product': self.product_id.id,
            'company': self.company_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'valuations': tuple(valuations)
        }


        self.env.cr.execute(query, params=params)

        res = self.env.cr.fetchall()
        for row in res:
            values = {
                'report_id': self.id,
                'product_id': row[0],
                'account_id': row[1],
                'amount': row[2],
                'quantity': row[3],
                'date': row[4],
                'type': 'in',
                'aml_ids': [(6, 0, list(row[5]))],
                'ref':row[6]
            }
            self.env['l10n_ro.storage_sheet_report.line'].create(values)
        if not res:
            values = {
                'report_id': self.id,
                'product_id': self.product_id.id,
                'date':self.date_from,
                'type': 'in',
            }
            self.env['l10n_ro.storage_sheet_report.line'].create(values)

        query = """SELECT  aml.product_id, aml.account_id, sum(aml.debit) - sum(aml.credit), 
                        sum(CASE WHEN stock_location_dest_id = %(location)s THEN -1*quantity
                            ELSE quantity
                            END), aml.date,
                             array_agg(aml.id), COALESCE(aml.ref, aml.name) 
                                 FROM account_move_line AS aml
                                      WHERE
                                            aml.account_id in %(valuations)s and
                                            aml.product_id = %(product)s AND 
                                               aml.company_id=%(company)s AND 
                                               aml.date >= %(date_from)s AND aml.date  <= %(date_to)s AND
                                                ( stock_location_id = %(location)s OR stock_location_dest_id = %(location)s) AND
                                               (aml.debit  -  aml.credit) < 0 
                                      GROUP BY aml.date, aml.product_id, aml.account_id, aml.ref, aml.name"""

        params = {
            'location': self.location_id.id,
            'product': self.product_id.id,
            'company': self.company_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'valuations': tuple(valuations)
        }

        self.env.cr.execute(query, params=params)

        res = self.env.cr.fetchall()
        for row in res:
            values = {
                'report_id': self.id,
                'product_id': row[0],
                'account_id': row[1],
                'amount': row[2],
                'quantity': row[3],
                'date': row[4],
                'type': 'out',
                'aml_ids': [(6, 0, list(row[5]))],
                'ref':row[6]
            }
            self.env['l10n_ro.storage_sheet_report.line'].create(values)
        if not res:
            values = {
                'report_id': self.id,
                'product_id': self.product_id.id,
                'date': self.date_to,
                'type': 'out',
            }
            self.env['l10n_ro.storage_sheet_report.line'].create(values)


    def button_show(self):
        self.do_compute()
        action = self.env.ref('l10n_ro_stock_account.action_storage_sheet_report_line').read()[0]
        action['domain'] = [('report_id', '=', self.id)]
        action['context'] = {'active_id': self.id}
        action['target'] = 'main'
        return action

    def button_print(self):
        self.do_compute()
        records = self
        report_name = 'l10n_ro_stock_account.action_report_storage_sheet_report'
        report = self.env.ref(report_name).report_action(records)
        return report


class DailyStockReportLine(models.TransientModel):
    _name = 'l10n_ro.storage_sheet_report.line'
    _description =  'l10n_ro.storage_sheet_report.line'


    report_id = fields.Many2one('l10n_ro.storage_sheet_report')
    product_id = fields.Many2one('product.product')
    quantity = fields.Float()
    amount = fields.Float()
    ref = fields.Char(string='Reference')
    date = fields.Date()
    type = fields.Selection([('balance', 'Balance'), ('in', 'Input'), ('out', 'Output')])
    account_id = fields.Many2one('account.account')
    aml_ids = fields.Many2many('account.move.line')

    def action_valuation_at_date_details(self):
        """ Returns an action with either a list view of all the valued stock moves of `self` if the
        valuation is set as manual or a list view of all the account move lines if the valuation is
        set as automated.
        """
        self.ensure_one()

        action = {
            'name': _('Valuation'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'context': self.env.context,
            'res_model': 'account.move.line',
            'domain': [('id', 'in', self.aml_ids.ids)]
        }

        tree_view_ref = self.env.ref('stock_account.view_stock_account_aml')
        form_view_ref = self.env.ref('account.view_move_line_form')
        action['views'] = [(tree_view_ref.id, 'tree'), (form_view_ref.id, 'form')]

        return action
