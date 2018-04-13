# -*- coding: utf-8 -*-
# ©  2018 Terrabit
# See README.rst file on addons root folder for license details

from odoo import api, fields, models
from odoo.tools import safe_eval
from dateutil.relativedelta import relativedelta


class RunDeclaration(models.TransientModel):
    _name = "l10n_ro.run.declaration"

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)

    declaration_id = fields.Many2one('l10n_ro.declaration', string='Declaration', required=True)
    date_range_id = fields.Many2one('date.range', string='Date range')
    date_from = fields.Date('Start Date', required=True)
    date_to = fields.Date('End Date', required=True)

    @api.model
    def default_get(self, fields_list):
        res = super(RunDeclaration, self).default_get(fields_list)
        today = fields.Date.context_today(self)
        today = fields.Date.from_string(today)

        from_date = (today + relativedelta(day=1, months=-1, days=0))
        to_date = (today + relativedelta(day=1, months=0, days=-1))

        res['date_from'] = fields.Date.to_string(from_date)
        res['date_to'] = fields.Date.to_string(to_date)
        if 'declaration_code' in self.env.context:
            declaration = self.env['l10n_ro.declaration'].search([('code', '=', self.env.context['declaration_code']),
                                                                  ('company_id', '=', self.env.user.company_id.id)])
            if declaration:
                res['declaration_id'] = declaration.id
        return res


    def get_report(self):
        model = self.env['l10n_ro.%s_report' % self.declaration_id.code.lower()]

        report = model.create({
            'company_id': self.company_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to
        })
        report.compute_data_for_report()
        return report

    @api.onchange('date_range_id')
    def onchange_date_range_id(self):
        """Handle date range change."""
        self.date_from = self.date_range_id.date_start
        self.date_to = self.date_range_id.date_end

    @api.multi
    def button_show(self):
        report = self.get_report()
        return report.show_report()


    @api.multi
    def button_execute(self):

        report = self.get_report()
        url = '/declarations/%s/%s/%s_data.xdp' % (self.id,report.id,self.declaration_id.code)
        action = {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }
        # todo: este o alta metoda de a obtine fisierul ?
        return action
