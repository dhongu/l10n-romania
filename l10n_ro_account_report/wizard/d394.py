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

import base64

from openerp.osv import fields, osv
from openerp.tools.translate import _


class d394_report(osv.osv_memory):

    """
    D394 Declaration
    """
    _name = "l10n_ro_account_report.d394.report"
    _description = 'D394 Declaration'

    def _get_xml_data(self, cr, uid, context=None):
        if context.get('file_save', False):
            return base64.encodestring(context['file_save'].encode('utf8'))
        return ''

    _columns = {
        'file_save': fields.binary('Save File'),
        'name': fields.char('File Name'),
        'msg': fields.text('File created', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'period_id': fields.many2one(
            'account.period',
            'Period',
            required=True
        ),
    }

    _defaults = {
        'msg': 'Save the File with '".xml"' extension.',
        'file_save': _get_xml_data,
        'name': 'd394.xml',
    }

    def _get_datas(self, cr, uid, ids, context=None):
        """Collects require data for vat intra xml
        :param ids: id of wizard.
        :return: dict of all data to be used to generate xml for Partner VAT
        Intra.
        :rtype: dict
        """
        if context is None:
            context = {}
        obj_invoice = self.pool.get('account_invoice')
        obj_period = self.pool.get('account_period')
        obj_sequence = self.pool.get('ir.sequence')
        obj_company = self.pool.get('res.company')
        currency_obj = self.pool.get('res.currency')
        obj_invoice = self.pool.get('account.invoice')
        obj_partner = self.pool.get('res.partner')
        tax_obj = self.pool.get('account.tax')
        xmldict = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        function = email = ''
        if user.partner_id.function:
            function = user.partner_id.function
        else:
            raise osv.except_osv(_('Error!'),
                                 _('You need to define your Job Position.'))
        uid_name = user.partner_id.name.split()
        uid_fname = ' '.join(uid_name[:-1])
        uid_name = uid_name[-1]
        wiz_data = self.browse(cr, uid, ids[0], context=context)

        data_company = obj_company.browse(
            cr, uid, wiz_data.company_id.id, context=context)
        company = wiz_data.company_id.id
        comp_currency = data_company.currency_id.id
        period = wiz_data.period_id.id
        xmldict.update({
            'luna': int(wiz_data.period_id.code[:2]),
            'an': int(wiz_data.period_id.code[3:]),
            'tip_D394': "L",
            'nume_declar': uid_name,
            'prenume_declar': uid_fname,
            'functie_declar': function,
            'cui': data_company.partner_id.vat[2:],
            'den': data_company.partner_id.name,
            'adresa': ', '.join([
                data_company.state_id and data_company.state_id.name,
                data_company.city,
                data_company.street,
                data_company.zip]),
            'telefon': data_company.phone,
            'totalPlata_A': 0,
            'nrCui': 0,
            'nrFactL': 0,
            'bazaL': 0,
            'tvaL': 0,
            'nrFactA': 0,
            'bazaA': 0,
            'tvaA': 0,
            'nrFactV': 0,
            'bazaV': 0,
            'tvaV': 0,
            'bazaVc': 0,
            'tvaVc': 0,
            'nrFactC': 0,
            'bazaC': 0,
            'tvaC': 0,
            'bazaCc': 0,
            'tvaCc': 0,
            'oper': [],
        })
        if data_company.email:
            xmldict.update({
                'mail': data_company.email,
                'mailFisc': data_company.email,
            })
        else:
            xmldict.update({
                'mail': user.partner_id.email or '-',
                'mailFisc': user.partner_id.email or '-',
            })

        from_xml = []
        cui = {}
        totalPlata_A = 0
        nrCui = 0
        nrfactL = bazaL = tvaL = 0
        nrfactA = bazaA = tvaA = 0
        nrfactV = bazaV = tvaV = bazaVc = tvaVc = 0
        nrfactC = bazaC = tvaC = bazaCc = tvaCc = 0
        invoices = obj_invoice.browse(
            cr,
            uid,
            obj_invoice.search(
                cr,
                uid,
                [
                    ('state', 'in', ['open', 'paid']),
                    ('period_id', '=', period),
                    ('fiscal_receipt', '=', False),
                    ('company_id', '=', company)
                ])
            )
        for inv in invoices:
            if not inv.fiscal_receipt:
                part = inv.partner_id
                nrCUI = len(cui) + 1
                if part.vat and part.vat_subjected and ('RO' in
                                                        part.vat.upper()):
                    if cui:
                        for key in cui.iterkeys():
                            if part.id == cui[key]:
                                nrCUI = key
                    if nrCUI > len(cui):
                        cui[nrCUI] = part.id
        invoices = []
        invoices = obj_invoice.browse(
            cr,
            uid,
            obj_invoice.search(
                cr,
                uid,
                [
                    ('state', 'in', ['open', 'paid']),
                    ('type', 'in', ['out_invoice', 'out_refund']),
                    ('period_id', '=', period),
                    ('company_id', '=', company)
                ])
        )
        for key in cui.iterkeys():
            in_xml = []
            tip = 'L'
            nrfact = nrfactv = baza = tva = 0
            bazainv = tvainv = 0
            bazacer = tvacer = 0
            for inv in invoices:
                if inv.partner_id.id == cui[key]:
                    if not inv.fiscal_receipt:
                        nrfact += 1
                        cuiP = inv.partner_id.vat[2:]
                        denP = inv.partner_id.name.replace(
                            '&', '-').replace('"', '')
                        if inv.fiscal_position and ('Taxare Inversa' in
                                                    inv.fiscal_position.name):
                            nrfactv += 1
                            for tax_line in inv.tax_line:
                                if 'INVERS' in tax_line.name.upper():
                                    bazainv += currency_obj.compute(
                                                   cr, uid, inv.currency_id.id,
                                                   comp_currency,
                                                   tax_line.base,
                                                   context={'date':
                                                            inv.date_invoice}
                                                   ) or 0.00
                                if any(i in tax_line.name for i in
                                   ('24', ' 9', ' 5', ' 0')):
                                    baza += currency_obj.compute(
                                                cr, uid,
                                                inv.currency_id.id,
                                                comp_currency,
                                                tax_line.base,
                                                context={'date':
                                                         inv.date_invoice}
                                                ) or 0.00
                                    tva += currency_obj.compute(
                                                cr, uid,
                                                inv.currency_id.id,
                                                comp_currency,
                                                tax_line.amount,
                                                context={'date':
                                                         inv.date_invoice}
                                                ) or 0.00

                            for line in inv.invoice_line:
                                taxes = tax_obj.compute_all(
                                            cr, uid,
                                            line.product_id.taxes_id,
                                            line.price_subtotal,
                                            1,
                                            product=line.product_id,
                                            partner=line.invoice_id.partner_id)
                                tvainv += currency_obj.compute(
                                              cr, uid,
                                              inv.currency_id.id,
                                              comp_currency,
                                              taxes['total_included'] -
                                              taxes['total'],
                                              context={'date':
                                                       inv.date_invoice}
                                              ) or 0.00
                        else:
                            for tax_line in inv.tax_line:
                                baza += currency_obj.compute(
                                              cr, uid,
                                              inv.currency_id.id,
                                              comp_currency,
                                              tax_line.base,
                                              context={'date':
                                                       inv.date_invoice}
                                              ) or 0.00
                                tva += currency_obj.compute(
                                              cr, uid,
                                              inv.currency_id.id,
                                              comp_currency,
                                              tax_line.amount,
                                              context={'date':
                                                       inv.date_invoice}
                                              ) or 0.00
            if baza != 0 and bazainv != 0:
                nrfact += 1
            if nrfact - nrfactv != 0:
                from_xml.append({
                    'tip': 'L',
                    'cuiP': cuiP,
                    'denP': denP,
                    'nrFact': nrfact - nrfactv,
                    'baza': int(round(baza)),
                    'tva': int(round(tva)),
                    'cereals': [],
                })
            if bazainv != 0:
                cer = {}
                cereals = []
                codes = self.pool.get('report.394.code').search(cr, uid, [])
                if codes:
                    codes = [code394.id for code394 in self.pool.get(
                        'report.394.code').browse(cr, uid, codes)]
                    for code in codes:
                        cer[code] = {
                            'baza': 0.00,
                            'tva': 0.00,
                        }
                    for inv in invoices:
                        if inv.partner_id.id == cui[key]:
                            if inv.fiscal_position and ('Taxare Inversa' in
                               inv.fiscal_position.name):
                                for line in inv.invoice_line:
                                    if line.product_id.d394_id:
                                        code = line.product_id.d394_id.id
                                        if code in codes:
                                            cer[code]['baza'] += \
                                            currency_obj.compute(
                                                    cr, uid,
                                                    inv.currency_id.id,
                                                    comp_currency,
                                                    line.price_subtotal,
                                                    context={'date':
                                                             inv.date_invoice}
                                                ) or 0.00
                                            if line.invoice_line_tax_id:
                                                taxes = tax_obj.compute_all(
                                                        cr, uid,
                                                        line.product_id.taxes_id,
                                                        line.price_subtotal,
                                                        1,
                                                        product=line.product_id,
                                                        partner=inv.partner_id)
                                                cer[code]['tva'] += \
                                                    currency_obj.compute(
                                                        cr, uid,
                                                        inv.currency_id.id,
                                                        comp_currency,
                                                        taxes['total_included'] -
                                                        taxes['total'],
                                                        context={'date':
                                                                 inv.date_invoice}
                                                        ) or 0.00
                    for key in cer.iterkeys():
                        if cer[key]['baza'] != 0:
                            cereals.append(
                                {'code': self.pool.get(
                                         'report.394.code'
                                         ).browse(cr, uid, key).name,
                                 'baza': int(round(cer[key]['baza'])),
                                 'tva': int(round(cer[key]['tva']))
                                 })
                            bazacer += int(round(cer[key]['baza']))
                            tvacer += int(round(cer[key]['tva']))

                from_xml.append({
                    'tip': 'V',
                    'cuiP': cuiP,
                    'denP': denP,
                    'nrFact': nrfactv,
                    'baza': int(round(bazainv)),
                    'tva': int(round(tvainv)),
                    'cereals': cereals
                })

            nrfactL += nrfact - nrfactv
            nrfactV += nrfactv
            bazaL += int(round(baza))
            tvaL += int(round(tva))
            bazaV += int(round(bazainv))
            tvaV += int(round(tvainv))
            bazaVc += int(round(bazacer))
            tvaVc += int(round(tvacer))
        invoices = []
        invoices = obj_invoice.browse(
            cr,
            uid,
            obj_invoice.search(
                cr,
                uid,
                [
                    ('state', 'in', ['open', 'paid']),
                    ('type', '=', 'in_invoice'),
                    ('period_id', '=', period),
                    ('company_id', '=', company)
                ])
        )
        for key in cui.iterkeys():
            in_xml = []
            nrfact = nrfactc = baza = tva = 0
            bazainv = tvainv = 0
            bazacer = tvacer = 0
            for inv in invoices:
                if inv.partner_id.id == cui[key]:
                    if not inv.fiscal_receipt:
                        nrfact += 1
                        cuiP = inv.partner_id.vat[2:]
                        denP = inv.partner_id.name.replace(
                            '&', '-').replace('"', '')
                        if inv.fiscal_position and ('Taxare Inversa' in
                                                    inv.fiscal_position.name):
                            nrfactc += 1
                            # bazainv += inv.amount_untaxed
                            base_exig = base1 = tva1 = tva_exig = 0.00
                            for tax_line in inv.tax_line:
                                if 'Ti-ach-c' in tax_line.name:
                                    bazainv += currency_obj.compute(
                                                   cr, uid,
                                                   inv.currency_id.id,
                                                   comp_currency,
                                                   tax_line.base,
                                                   context={'date':
                                                            inv.date_invoice}
                                                   ) or 0.00
                                    tvainv += currency_obj.compute(
                                                   cr, uid,
                                                   inv.currency_id.id,
                                                   comp_currency,
                                                   -tax_line.amount,
                                                   context={'date':
                                                            inv.date_invoice}
                                                   ) or 0.00
                                    base_exig += currency_obj.compute(
                                                   cr, uid,
                                                   inv.currency_id.id,
                                                   comp_currency,
                                                   tax_line.base,
                                                   context={'date':
                                                            inv.date_invoice}
                                                   ) or 0.00
                                    tva_exig += currency_obj.compute(
                                                   cr, uid,
                                                   inv.currency_id.id,
                                                   comp_currency,
                                                   tax_line.amount,
                                                   context={'date':
                                                            inv.date_invoice}
                                                   ) or 0.00
                                if 'Ti-ach-d' in tax_line.name:
                                    base1 += currency_obj.compute(
                                                   cr, uid,
                                                   inv.currency_id.id,
                                                   comp_currency,
                                                   tax_line.base,
                                                   context={'date':
                                                            inv.date_invoice}
                                                   ) or 0.00
                                    tva1 += currency_obj.compute(
                                                   cr, uid,
                                                   inv.currency_id.id,
                                                   comp_currency,
                                                   tax_line.amount,
                                                   context={'date':
                                                            inv.date_invoice}
                                                   ) or 0.00
                            if base1 - base_exig > 0:
                                nrfact += 1
                                baza += base1 - base_exig
                                tva += tva1 - tva_exig
                        else:
                            for tax_line in inv.tax_line:
                                baza += currency_obj.compute(
                                            cr, uid,
                                            inv.currency_id.id,
                                            comp_currency,
                                            tax_line.base,
                                            context={'date':
                                                     inv.date_invoice}
                                            ) or 0.00
                                tva += currency_obj.compute(
                                            cr, uid,
                                            inv.currency_id.id,
                                            comp_currency,
                                            tax_line.amount,
                                            context={'date':
                                                     inv.date_invoice}
                                            ) or 0.00
            if bazainv != 0:
                cer = {}
                cereals = []
                codes = self.pool.get('report.394.code').search(cr, uid, [])
                if codes:
                    codes = [code394.id for code394 in self.pool.get(
                        'report.394.code').browse(cr, uid, codes)]
                    for code in codes:
                        cer[code] = {
                            'baza': 0.0,
                            'tva': 0.0,
                        }
                    for inv in invoices:
                        if inv.partner_id.id == cui[key]:
                            if inv.fiscal_position and \
                            ('Taxare Inversa' in inv.fiscal_position.name):
                                for line in inv.invoice_line:
                                    if line.product_id.d394_id:
                                        code = line.product_id.d394_id.id
                                        prod_taxes = \
                                            line.product_id.supplier_taxes_id
                                        if code in codes:
                                            cer[code]['baza'] += \
                                            currency_obj.compute(
                                                        cr, uid,
                                                        inv.currency_id.id,
                                                        comp_currency,
                                                        line.price_subtotal,
                                                        context={'date':
                                                                 inv.date_invoice}
                                                    ) or 0.00
                                            taxes = tax_obj.compute_all(
                                                        cr, uid,
                                                        prod_taxes,
                                                        line.price_subtotal,
                                                        1,
                                                        product=line.product_id,
                                                        partner=inv.partner_id)
                                            cer[code]['tva'] += \
                                            currency_obj.compute(
                                                        cr, uid,
                                                        inv.currency_id.id,
                                                        comp_currency,
                                                        taxes['total_included'] -
                                                        taxes['total'],
                                                        context={'date':
                                                                 inv.date_invoice}
                                                    ) or 0.00
                    for key in cer.iterkeys():
                        if cer[key]['baza'] != 0:
                            cereals.append(
                                {'code': self.pool.get(
                                         'report.394.code'
                                         ).browse(cr, uid, key).name,
                                 'baza': int(round(cer[key]['baza'])),
                                 'tva': int(round(cer[key]['tva']))}
                                )
                            bazacer += int(round(cer[key]['baza']))
                            tvacer += int(round(cer[key]['tva']))

                from_xml.append({
                    'tip': 'C',
                    'cuiP': cuiP,
                    'denP': denP,
                    'nrFact': nrfactc,
                    'baza': int(round(bazainv)),
                    'tva': int(round(tvainv)),
                    'cereals': cereals
                })

            if nrfact - nrfactc != 0:
                from_xml.append({
                    'tip': 'A',
                    'cuiP': cuiP,
                    'denP': denP,
                    'nrFact': nrfact - nrfactc,
                    'baza': int(round(baza)),
                    'tva': int(round(tva)),
                    'cereals': [],
                })

            nrfactA += nrfact - nrfactc
            nrfactC += nrfactc
            bazaA += int(round(baza))
            tvaA += int(round(tva))
            bazaC += int(round(bazainv))
            tvaC += int(round(tvainv))
            bazaCc += int(round(bazacer))
            tvaCc += int(round(tvacer))
        xmldict.update({
            'totalPlata_A': int(len(cui)) + int(bazaL) + int(tvaL) +
            int(bazaA) + int(tvaA) + int(bazaV) + int(tvaV) + int(bazaVc) +
            int(tvaVc) + int(bazaC) + int(tvaC) + int(bazaCc) + int(tvaCc),
            'nrCui': int(len(cui)),
            'nrFactL': nrfactL,
            'bazaL': bazaL,
            'tvaL': tvaL,
            'nrFactA': nrfactA,
            'bazaA': bazaA,
            'tvaA': tvaA,
            'nrFactV': nrfactV,
            'bazaV': bazaV,
            'tvaV': tvaV,
            'bazaVc': bazaVc,
            'tvaVc': tvaVc,
            'nrFactC': nrfactC,
            'bazaC': bazaC,
            'tvaC': tvaC,
            'bazaCc': bazaCc,
            'tvaCc': tvaCc,
            'oper': from_xml,
        })
        return xmldict

    def create_xml(self, cursor, user, ids, context=None):

        mod_obj = self.pool.get('ir.model.data')
        xml_data = self._get_datas(cursor, user, ids, context=context)
        data_file = ''
        if xml_data['an'] > 2013:
            data_file = """<?xml version="1.0"?>
<declaratie394 luna="%(luna)s" an="%(an)s" tip_D394="%(tip_D394)s"
nume_declar="%(nume_declar)s" prenume_declar="%(prenume_declar)s"
functie_declar="%(functie_declar)s"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="mfp:anaf:dgti:d394:declaratie:v2 D394.xsd"
xmlns="mfp:anaf:dgti:d394:declaratie:v2">
<identificare cui="%(cui)s" den="%(den)s"
adresa="%(adresa)s" telefon="%(telefon)s" mail="%(mail)s"
totalPlata_A="%(totalPlata_A)s"/>
<rezumat nrCui="%(nrCui)s" nrFactL="%(nrFactL)s"
bazaL="%(bazaL)s" tvaL="%(tvaL)s"
nrFactA="%(nrFactA)s" bazaA="%(bazaA)s"
tvaA="%(tvaA)s" nrFactV="%(nrFactV)s"
bazaV="%(bazaV)s" tvaV="%(tvaV)s"
bazaVc="%(bazaVc)s" tvaVc="%(tvaVc)s"
nrFactC="%(nrFactC)s"
bazaC="%(bazaC)s" tvaC="%(tvaC)s"
bazaCc="%(bazaCc)s" tvaCc="%(tvaCc)s"/>""" % (xml_data)
            for client in xml_data['oper']:
                data_file += """<op1 tip="%s" cuiP="%s"
                                denP="%s" nrFact="%s"
                                baza="%s" tva="%s" >
                             """ % ((client['tip']), (client['cuiP']),
                                    (client['denP']), (client['nrFact']),
                                    (client['baza']), (client['tva']))
                if client['cereals']:
                    for line in client['cereals']:
                        data_file += """<op11 codPR="%s"
                                        bazaPR="%s" tvaPR="%s"/>
                                     """ % ((line['code']),
                                            (line['baza']),
                                            (line['tva']))
                data_file += """
    </op1> """
            data_file += """
</declaratie394>"""
        else:
            data_file = """<?xml version="1.0"?>
<declaratie394 luna="%(luna)s" an="%(an)s" tip_D394="%(tip_D394)s"
nume_declar="%(nume_declar)s" prenume_declar="%(prenume_declar)s"
functie_declar="%(functie_declar)s"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="mfp:anaf:dgti:d394:declaratie:v1 D394.xsd"
xmlns="mfp:anaf:dgti:d394:declaratie:v1">
<identificare cui="%(cui)s" den="%(den)s"
adresa="%(adresa)s" telefon="%(telefon)s" mail="%(mail)s"
totalPlata_A="%(totalPlata_A)s"/>
<rezumat nrCui="%(nrCui)s"
bazaL="%(bazaL)s" tvaL="%(tvaL)s"
bazaA="%(bazaA)s" tvaA="%(tvaA)s"
bazaV="%(bazaV)s" tvaV="%(tvaV)s"
bazaVc="%(bazaVc)s" tvaVc="%(tvaVc)s"
bazaC="%(bazaC)s" tvaC="%(tvaC)s"
bazaCc="%(bazaCc)s" tvaCc="%(tvaCc)s"/>""" % (xml_data)
            for client in xml_data['oper']:
                data_file += """<op1 tip="%s" cuiP="%s"
                                denP="%s"
                                baza="%s" tva="%s" >
                             """ % ((client['tip']), (client['cuiP']),
                                    (client['denP']),
                                    (client['baza']), (client['tva']))
                if client['cereals']:
                    for line in client['cereals']:
                        data_file += """<op11 codPR="%s"
                                        bazaPR="%s" tvaPR="%s"/>
                                     """ % ((line['code']),
                                            (line['baza']),
                                            (line['tva']))
                data_file += """
    </op1> """
            data_file += """
</declaratie394>"""

        context['file_save'] = data_file

        model_data_ids = mod_obj.search(cursor, user,
                                        [('model', '=', 'ir.ui.view'),
                                         ('name', '=', 'view_d394_save')],
                                        context=context)
        resource_id = mod_obj.read(cursor, user, model_data_ids,
                                   fields=['res_id'],
                                   context=context)[0]['res_id']

        return {
            'name': _('Save'),
            'context': context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'l10n_ro_account_report.d394.report',
            'views': [(resource_id, 'form')],
            'view_id': 'view_394_save',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

d394_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
