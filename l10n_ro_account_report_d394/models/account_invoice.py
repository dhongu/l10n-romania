# -*- coding: utf-8 -*-
# ©  2016 Forest and Biomass Romania
# See README.rst file on addons root folder for license details

import re
from openerp import models, fields, api

ORIGIN_TYPE = [
    ('1', 'Invoice'),
    ('2', 'Slip'),
    ('3', 'Trading Book'),
    ('4', 'Contract')
]

OPERATION_TYPE = [
    ('L', 'Customer Invoice'),
    ('A', 'Supplier Invoice'),
    ('LS', 'Special Customer Invoice'),
    ('AS', 'Special Supplier Invoice'),
    ('AI', 'VAT on Payment Supplier Invoice'),
    ('V', 'Inverse Taxation Customer Invoice'),
    ('C', 'Inverse Taxation Supplier Invoice'),
    ('N', 'Fizical Persons Supplier Invoice')
]

SEQUENCE_TYPE = [
    ('normal', 'Invoice'),
    ('autoinv1', 'Customer Auto Invoicing'),
    ('autoinv2', 'Supplier  Auto Invoicing')
]


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    fiscal_receipt = fields.Boolean('Fiscal Receipts Journal')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _get_inv_number(self):
        regex = re.compile('[^a-zA-Z]')
        regex1 = re.compile('[^0-9]')
        for inv in self:
            if inv.type in ('out_invoice', 'out_refund') or \
                    inv.journal_id.sequence_type in ('autoinv1', 'autoinv2'):
                inv_seq = inv.journal_id.sequence_id
                ctx = self._context.copy()
                ctx['fiscalyear_id'] = inv.period_id.fiscalyear_id.id
                inv_serie = inv_seq._interpolate(
                    inv_seq.prefix,
                    inv_seq.with_context(ctx)._interpolation_dict_context())
                inv.inv_serie = regex.sub('', inv_serie)
                if inv.internal_number:
                    inv.inv_number = int(regex1.sub(
                        '',
                        inv.internal_number.replace(inv_serie, '')))
            else:
                if inv.supplier_invoice_number and \
                        regex1.sub('', inv.supplier_invoice_number):
                    val = inv.supplier_invoice_number
                else:
                    val = inv.internal_number
                if val:
                    inv_serie = regex.sub('', val)
                    inv.inv_serie = inv_serie
                    if inv_serie:
                        inv.inv_number = int(regex1.sub(
                            '',
                            val.replace(inv_serie, '')))
                    else:
                        inv.inv_number = int(regex1.sub(
                            '', val))
        return True

    @api.multi
    def _get_partner_type(self):
        for inv in self:
            partner = inv.partner_id
            eur_countries = []
            eur_grp = self.env.ref('base.europe')
            if eur_grp:
                eur_countries = [country.id for country in eur_grp.country_ids]
            if partner.country_id and \
                    partner.country_id.id == self.env.ref('base.ro').id:
                if partner.vat_subjected:
                    new_type = '1'
                else:
                    new_type = '2'
            elif partner.country_id.id in eur_countries:
                new_type = '3'
            else:
                new_type = '4'
            inv.partner_type = new_type
        return True

    @api.multi
    def _get_operation_type(self):
        for inv in self:
            partner = inv.partner_id
            country_ro = self.env.ref('base.ro')
            if inv.type in ('out_invoice', 'out_refund'):
                if inv.fiscal_position and \
                        ('Taxare Inversa' in inv.fiscal_position.name):
                    oper_type = 'V'
                elif not inv.fiscal_position or \
                        (inv.fiscal_position and \
                         ('National' in inv.fiscal_position.name)):
                    if inv.special_taxes:
                        oper_type = 'LS'
                    elif partner.country_id and \
                            partner.country_id.id != country_ro.id:
                        oper_type = 'V'
                    else:
                        oper_type = 'L'
                else:
                    oper_type = 'L'
            else:
                if not partner.is_company and inv.origin_type:
                    oper_type = 'N'
                elif inv.fiscal_position and \
                        (('Taxare Inversa' in inv.fiscal_position.name) or \
                         ('Comunitar' in inv.fiscal_position.name)):
                    oper_type = 'C'
                elif inv.fiscal_position and  \
                        ('Scutite' in inv.fiscal_position.name):
                    if partner.country_id and \
                            partner.country_id.id == country_ro.id:
                        if inv.special_taxes:
                            oper_type = 'AS'
                        else:
                            oper_type = 'A'
                    else:
                        oper_type = 'C'
                elif not inv.fiscal_position or \
                        (inv.fiscal_position and
                         ('National' in inv.fiscal_position.name)):
                    if inv.special_taxes:
                        oper_type = 'AS'
                    elif inv.vat_on_payment:
                        oper_type = 'AI'
                    else:
                        oper_type = 'A'
                elif inv.vat_on_payment:
                    oper_type = 'AI'
                else:
                    oper_type = 'A'
            inv.operation_type = oper_type
        return True

    @api.multi
    def _get_tax_ids(self):
        for inv in self:
            check = False
            taxes = []
            if not inv.fiscal_position or (('National' in \
                    inv.fiscal_position.name) or ('Invers' in \
                    inv.fiscal_position.name)  or (('Scutit' in \
                    inv.fiscal_position.name) and inv.partner_type in ('1','2'))):
                for line in inv.invoice_line:
                    taxes += [tax.id for tax in line.invoice_line_tax_id]
            else:
                for line in inv.invoice_line:
                    if inv.type in ('out_invoice', 'out_refund'):
                        taxes += [tax.id for tax in line.product_id.taxes_id]
                    else:
                        taxes += [tax.id for tax in \
                            line.product_id.supplier_taxes_id]
            inv.tax_ids = taxes
        return True

    @api.multi
    def _check_special_taxes(self):
        self.ensure_one()
        check = False
        for tax_line in self.tax_line:
            if any(i in tax_line.name for i in (' 9', ' 5')):
                check = True
        return check

    origin_type = fields.Selection(ORIGIN_TYPE, default='1',
                                   string='Origin Type')
    sequence_type = fields.Selection(SEQUENCE_TYPE,
                                     related='journal_id.sequence_type',
                                     string='Sequence Type')
    operation_type = fields.Selection(OPERATION_TYPE,
                                      compute='_get_operation_type',
                                      string='Operation Type')
    inv_serie = fields.Char('Invoice Serie',
                            compute="_get_inv_number")
    inv_number = fields.Char('Invoice Number',
                             compute="_get_inv_number")
    partner_type = fields.Char('D394 Partner Type',
                               compute="_get_partner_type")
    special_taxes = fields.Boolean('Special Taxation')
    tax_ids = fields.Many2many('account.tax',
                               compute="_get_tax_ids",
                               string='Normal Taxes')

    @api.multi
    def onchange_journal_id(self, journal_id=False):
        res = super(AccountInvoice, self).onchange_journal_id(journal_id)
        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
            res['value']['fiscal_receipt'] = journal.fiscal_receipt
        return res
