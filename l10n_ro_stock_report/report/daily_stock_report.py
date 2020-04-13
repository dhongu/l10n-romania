# -*- coding: utf-8 -*-
# ©  2008-2018 Fekete Mihai <mihai.fekete@forbiom.eu>
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _


class DailyStockReport(models.TransientModel):
    _name = 'l10n_ro.daily_stock_report'
    _description = 'DailyStockReport'

    # Filters fields, used for data computation

    location_id = fields.Many2one('stock.location', domain="[('usage','=','internal'),('company_id','=',company_id)]", required=True)

    date_range_id = fields.Many2one('date.range', string='Date range')
    date_from = fields.Date('Start Date', required=True, default=fields.Date.today)
    date_to = fields.Date('End Date', required=True, default=fields.Date.today)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id)
    mode = fields.Selection([('product', 'Product'), ('ref', 'Reference')], default='ref', string='Detail mode')

    line_product_ids = fields.One2many('l10n_ro.daily_stock_report.line','report_id')
    line_ref_ids = fields.One2many('l10n_ro.daily_stock_report.ref', 'report_id')


    @api.model
    def default_get(self, fields_list):
        res = super(DailyStockReport, self).default_get(fields_list)
        mode = res.get('mode','ref')
        if mode == 'product':
            today = fields.Date.context_today(self)
            today = fields.Date.from_string(today)

            from_date = (today + relativedelta(day=1, months=0, days=0))
            to_date = (today + relativedelta(day=1, months=1, days=-1))

            res['date_from'] = fields.Date.to_string(from_date)
            res['date_to'] = fields.Date.to_string(to_date)
        return res

    @api.onchange('date_range_id')
    def onchange_date_range_id(self):
        """Handle date range change."""
        if self.date_range_id:
            self.date_from = self.date_range_id.date_start
            self.date_to = self.date_range_id.date_end

    @api.multi
    def do_compute(self):
        self.env['account.move.line'].check_access_rights('read')

        lines = self.env['l10n_ro.daily_stock_report.line'].search([('report_id', '=', self.id)])
        lines.unlink()

        stock_init = {}

        stock_in = {}


        stock_out = {}

        to_date = self.date_from
        query = """SELECT aml.product_id, aml.account_id, sum(aml.debit) - sum(aml.credit), 
                    sum(CASE WHEN stock_location_dest_id = %(location)s THEN -1*quantity
                        ELSE quantity
                        END), 
                    array_agg(aml.id)
                        FROM account_move_line AS aml 
                            WHERE aml.product_id IS NOT NULL AND 
                                    aml.company_id=%(company)s AND 
                                    aml.date < %(date)s AND 
                                   ( stock_location_id = %(location)s OR stock_location_dest_id = %(location)s) 
                            GROUP BY aml.product_id, aml.account_id """


        params = {
            'location': self.location_id.id,
            'company': self.company_id.id,
            'date': self.date_from,
        }


        self.env.cr.execute(query, params=params)

        product_ids = []
        res = self.env.cr.fetchall()
        for row in res:
            product_ids += [row[0]]
            stock_init[(row[0], row[1])] = (row[2], row[3], list(row[4]))
        products = self.env['product.product'].browse(product_ids)

        query = """SELECT aml.product_id, aml.account_id, sum(aml.debit) - sum(aml.credit), 
                        sum(CASE WHEN stock_location_dest_id = %(location)s THEN -1*quantity
                            ELSE quantity
                            END), 
                        array_agg(aml.id) 
                         FROM account_move_line AS aml
                              WHERE aml.product_id IS NOT NULL AND 
                                       aml.company_id=%(company)s AND 
                                       aml.date >= %(date_from)s AND aml.date  <= %(date_to)s AND
                                        ( stock_location_id = %(location)s OR stock_location_dest_id = %(location)s ) AND
                                       (aml.debit  -  aml.credit) >= 0 
                              GROUP BY aml.product_id, aml.account_id"""

        params = {
            'location': self.location_id.id,
            'company': self.company_id.id,
            'date_from': self.date_from  ,
            'date_to': self.date_to  ,
        }

        self.env.cr.execute(query, params=params)
        product_ids = []
        res = self.env.cr.fetchall()
        for row in res:
            product_ids += [row[0]]
            stock_in[(row[0], row[1])] = (row[2], row[3], list(row[4]))
        products |= self.env['product.product'].browse(product_ids)

        query = """SELECT aml.product_id, aml.account_id, sum(aml.debit) - sum(aml.credit), 
                        sum(CASE WHEN stock_location_dest_id = %(location)s THEN -1*quantity
                            ELSE quantity
                            END),
                             array_agg(aml.id) 
                                 FROM account_move_line AS aml
                                      WHERE aml.product_id IS NOT NULL AND 
                                               aml.company_id=%(company)s AND 
                                               aml.date >= %(date_from)s AND aml.date  <= %(date_to)s AND
                                                ( stock_location_id = %(location)s OR stock_location_dest_id = %(location)s) AND
                                               (aml.debit  -  aml.credit) < 0 
                                      GROUP BY aml.product_id, aml.account_id"""
        params = (self.location_id.id, self.env.user.company_id.id, self.date_from, self.date_to, self.location_id.id, self.location_id.id)

        params = {
            'location': self.location_id.id,
            'company': self.company_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        }

        self.env.cr.execute(query, params=params)
        product_ids = []
        res = self.env.cr.fetchall()
        for row in res:
            product_ids += [row[0]]
            stock_out[(row[0], row[1])] = (row[2], row[3], list(row[4]))
        products |= self.env['product.product'].browse(product_ids)

        aml_in = []
        aml_out = []
        aml_init = []

        balance_init = 0.0
        for product in products:
            valuations = [ product.categ_id.property_stock_valuation_account_id.id ]
            if self.location_id.valuation_in_account_id.id and \
                    self.location_id.valuation_in_account_id.id not in valuations:
                valuations.append(self.location_id.valuation_in_account_id.id)
            if self.location_id.valuation_out_account_id.id and \
                    self.location_id.valuation_out_account_id.id not in valuations:
                valuations.append(self.location_id.valuation_out_account_id.id)

            for valuation_account_id in valuations:
                value, quantity, aml_ids = stock_init.get((product.id, valuation_account_id)) or (0, 0, [])

                if value or quantity:
                    self.env['l10n_ro.daily_stock_report.line'].create({
                        'report_id': self.id,
                        'product_id': product.id,
                        'quantity': quantity,
                        'amount': value,
                        'type': 'balance',
                        'aml_ids': [(6, 0, aml_ids)]
                    })
                balance_init += value
                aml_init += aml_ids

                value, quantity, aml_ids = stock_in.get((product.id, valuation_account_id)) or (0, 0, [])
                if value or quantity:
                    self.env['l10n_ro.daily_stock_report.line'].create({
                        'report_id': self.id,
                        'product_id': product.id,
                        'quantity': quantity,
                        'amount': value,
                        'type': 'in',
                        'aml_ids': [(6, 0, aml_ids)]
                    })
                aml_in += aml_ids
                value, quantity, aml_ids = stock_out.get((product.id, valuation_account_id)) or (0, 0, [])
                if value or quantity:
                    self.env['l10n_ro.daily_stock_report.line'].create({
                        'report_id': self.id,
                        'product_id': product.id,
                        'quantity': quantity,
                        'amount': value,
                        'type': 'out',
                        'aml_ids': [(6, 0, aml_ids)]
                    })
                aml_out += aml_ids


        self.env['l10n_ro.daily_stock_report.ref'].create({
            'report_id': self.id,
            'ref': 'initial',
            'amount': balance_init,
            'type': 'balance',
            'aml_ids': [(6, 0, aml_init)]
        })

        if self.mode == 'ref':
            ref_in = {}
            amls = self.env['account.move.line'].browse(aml_in)
            for aml in amls:
                if aml.ref in ref_in:
                    ref_in[aml.ref]['amount'] += aml.debit - aml.credit
                    ref_in[aml.ref]['aml_ids'] += [aml.id]
                else:
                    ref_in[aml.ref] = {
                        'amount': aml.debit - aml.credit,
                        'aml_ids': [aml.id]
                    }

            ref_out = {}
            amls = self.env['account.move.line'].browse(aml_out)
            for aml in amls:
                if aml.ref in ref_out:
                    ref_out[aml.ref]['amount'] += aml.debit - aml.credit
                    ref_out[aml.ref]['aml_ids'] += [aml.id]
                else:
                    ref_out[aml.ref] = {
                        'amount': aml.debit - aml.credit,
                        'aml_ids': [aml.id]
                    }

            for ref in ref_in:
                self.env['l10n_ro.daily_stock_report.ref'].create({
                    'report_id': self.id,
                    'ref': ref,
                    'amount': ref_in[ref]['amount'],
                    'type': 'in',
                    'aml_ids': [(6, 0, ref_in[ref]['aml_ids'])]
                })

            for ref in ref_out:
                self.env['l10n_ro.daily_stock_report.ref'].create({
                    'report_id': self.id,
                    'ref': ref,
                    'amount': ref_out[ref]['amount'],
                    'type': 'out',
                    'aml_ids': [(6, 0, ref_out[ref]['aml_ids'])]
                })

    def button_show(self):
        self.do_compute()
        if self.mode == 'ref':
            action = self.env.ref('l10n_ro_stock_report.action_daily_stock_report_ref').read()[0]
        else:
            action = self.env.ref('l10n_ro_stock_report.action_daily_stock_report_line').read()[0]
        action['domain'] = [('report_id', '=', self.id)]
        action['context'] = {'active_id': self.id}
        action['target'] = 'main'
        return action

    def button_print(self):
        self.do_compute()
        records = self
        report_name = 'l10n_ro_stock_report.action_report_daily_stock_report'
        report = self.env.ref(report_name).report_action(records)
        return report

class DailyStockReportRef(models.TransientModel):
    _name = 'l10n_ro.daily_stock_report.ref'
    _description = 'DailyStockReportRef'

    report_id = fields.Many2one('l10n_ro.daily_stock_report')
    ref = fields.Char(string='Reference')
    amount = fields.Float()
    type = fields.Selection([('balance', 'Balance'), ('in', 'Input'), ('out', 'Output')])
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


class DailyStockReportLine(models.TransientModel):
    _name = 'l10n_ro.daily_stock_report.line'
    _description =  'DailyStockReportLine'



    report_id = fields.Many2one('l10n_ro.daily_stock_report')
    product_id = fields.Many2one('product.product')
    quantity = fields.Float()
    amount = fields.Float()
    type = fields.Selection([('balance', 'Balance'), ('in', 'Input'), ('out', 'Output')])
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
