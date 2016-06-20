# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Business Applications
#    Copyright (C) 2014-2015 Odoo S.A. <http://www.odoo.com>
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import base64
import xml.etree.ElementTree as ET
from collections import namedtuple
from datetime import datetime

from openerp import exceptions, SUPERUSER_ID, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

INTRASTAT_XMLNS = 'http://www.intrastat.ro/xml/InsSchema'

class xml_decl(osv.TransientModel):
    """
    Intrastat XML Declaration
    """
    _name = "l10n_ro_intrastat_xml.xml_decl"
    _description = 'Intrastat XML Declaration'

    def _get_tax_code(self, cr, uid, context=None):
        obj_tax_code = self.pool.get('account.tax.code')
        obj_user = self.pool.get('res.users')
        company_id = obj_user.browse(cr, uid, uid, context=context).company_id.id
        tax_code_ids = obj_tax_code.search(cr, uid, [('company_id', '=', company_id),
                                                     ('parent_id', '=', False)],
                                           context=context)
        return tax_code_ids and tax_code_ids[0] or False

    def _get_def_monthyear(self, cr, uid, context=None):
        td = datetime.strptime(fields.date.context_today(self, cr, uid, context=context),
                               tools.DEFAULT_SERVER_DATE_FORMAT).date()
        return td.strftime('%Y'), td.strftime('%m')

    def _get_def_month(self, cr, uid, context=None):
        return self._get_def_monthyear(cr, uid, context=context)[1]

    def _get_def_year(self, cr, uid, context=None):
        return self._get_def_monthyear(cr, uid, context=context)[0]

    _columns = {
        'name': fields.char('File Name'),
        'month': fields.selection([('01','January'), ('02','February'), ('03','March'),
                                   ('04','April'), ('05','May'), ('06','June'), ('07','July'),
                                   ('08','August'), ('09','September'), ('10','October'),
                                   ('11','November'), ('12','December')], 'Month', required=True),
        'year': fields.char('Year', size=4, required=True),
        'tax_code_id': fields.many2one('account.tax.code', 'Company Tax Chart',
                                       domain=[('parent_id', '=', False)], required=True),
        'type': fields.selection([('arrivals', 'Arrivals'),
                                      ('dispatches', 'Dispatches') ],
                                     'Type', required=True),

        'contact_id':fields.many2one('res.partner', 'Contact', domain=[('is_company', '=', False)], required=True),
        'file_save': fields.binary('Intrastat Report File', readonly=True),
        'state': fields.selection([('draft', 'Draft'), ('download', 'Download')], string="State"),
    }

    _defaults = {
        'type':'arrivals',

        'name': 'intrastat.xml',
        'tax_code_id': _get_tax_code,
        'month': _get_def_month,
        'year': _get_def_year,
        'state': 'draft',
    }
    
    def _company_warning(self, cr, uid, translated_msg, context=None):
        """ Raise a error with custom message, asking user to configure company settings """
        xmlid_mod = self.pool['ir.model.data']
        action_id = xmlid_mod.xmlid_to_res_id(cr, uid, 'base.action_res_company_form')
        raise exceptions.RedirectWarning(
            translated_msg, action_id, _('Go to company configuration screen'))
            
    def create_xml(self, cr, uid, ids, context=None):
        """Creates xml that is to be exported and sent to estate for partner vat intra.
        :return: Value for next action.
        :rtype: dict
        """
        decl_datas = self.browse(cr, uid, ids[0])
        company = decl_datas.tax_code_id.company_id
        if not (company.partner_id and company.partner_id.country_id and
                company.partner_id.country_id.id):
            self._company_warning(
                cr, uid,
                _('The country of your company is not set, '
                  'please make sure to configure it first.'),
                context=context)
         
        if not company.vat:
            self._company_warning(
                cr, uid,
                _('The VAT of your company is not set, '
                  'please make sure to configure it first.'),
                context=context)
        if len(decl_datas.year) != 4:
            raise exceptions.Warning(_('Year must be 4 digits number (YYYY)'))

        #Create root declaration
        if decl_datas.type == 'arrivals':
            decl = ET.Element('InsNewArrival')
        else:
            decl = ET.Element('InsNewDispatch') 
        
        decl.set('SchemaVersion','1.0')    
        decl.set('xmlns', INTRASTAT_XMLNS)



        CodeVersion = ET.SubElement(decl, 'InsCodeVersions')
        tag = ET.SubElement(CodeVersion, 'CountryVer')
        tag.text = '2007'
        tag = ET.SubElement(CodeVersion, 'EuCountryVer')
        tag.text = '2007'
        tag = ET.SubElement(CodeVersion, 'CnVer')
        tag.text = '2016'
        tag = ET.SubElement(CodeVersion, 'ModeOfTransportVer')
        tag.text = '2005'
        tag = ET.SubElement(CodeVersion, 'DeliveryTermsVer')
        tag.text = '2011'
        tag = ET.SubElement(CodeVersion, 'NatureOfTransactionAVer')
        tag.text = '2010'
        tag = ET.SubElement(CodeVersion, 'NatureOfTransactionBVer')
        tag.text = '2010'
        tag = ET.SubElement(CodeVersion, 'CountyVer')
        tag.text = '1'
        tag = ET.SubElement(CodeVersion, 'LocalityVer')
        tag.text = '06/2006'
        tag = ET.SubElement(CodeVersion, 'UnitVer')
        tag.text = '1'        

                
        #Add Administration elements
        header = ET.SubElement(decl, 'InsDeclarationHeader')
        tag = ET.SubElement(header, 'VatNr')
        vat = company.vat
        if vat[:2] == 'RO':
            vat = '00'+vat[2:]
        if vat[:2] != '00':
            vat = '00'+vat

        tag.text = vat
        
        tag = ET.SubElement(header, 'FirmName')
        tag.text = company.partner_id.name
        
        tag = ET.SubElement(header, 'RefPeriod')
        tag.text = decl_datas.year +'-'+decl_datas.month
        
        
        last_name =  decl_datas.contact_id.name.split(' ')[-1]
        first_name = ' '.join(decl_datas.contact_id.name.split(' ')[:-1])
        
        ContactPerson = ET.SubElement(header, 'ContactPerson')
        tag = ET.SubElement(ContactPerson, 'LastName')
        tag.text = last_name
        tag = ET.SubElement(ContactPerson, 'FirstName')
        tag.text = first_name        
        tag = ET.SubElement(ContactPerson, 'Phone')
        tag.text = decl_datas.contact_id.phone        
        tag = ET.SubElement(ContactPerson, 'Position')
        tag.text = decl_datas.contact_id.function
        
         
        if decl_datas.type == 'arrivals':
            self._get_lines(cr, SUPERUSER_ID, ids, decl_datas, company,  dispatchmode=False, decl=decl,  context=context)
           
        else:
            self._get_lines(cr, SUPERUSER_ID, ids, decl_datas, company,  dispatchmode=True, decl=decl,  context=context)
           

        #Get xml string with declaration
        data_file = ET.tostring(decl, encoding='UTF-8', method='xml')

        #change state of the wizard
        self.write(cr, uid, ids,
                   {'name': 'intrastat_%s%s.xml' % (decl_datas.year, decl_datas.month),
                    'file_save': base64.encodestring(data_file),
                    'state': 'download'},
                   context=context)
        return {
            'name': _('Save'),
            'context': context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'l10n_ro_intrastat_xml.xml_decl',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': ids[0],
        }

    def _get_lines(self, cr, uid, ids, decl_datas, company, dispatchmode, decl, context=None):
        intrastatcode_mod = self.pool['report.intrastat.code']
        invoiceline_mod = self.pool['account.invoice.line']
        product_mod = self.pool['product.product']
        currency_mod  = self.pool['res.currency']
         

        if dispatchmode:
            mode1 = 'out_invoice'
            mode2 = 'in_refund'
            
        else:
            mode1 = 'in_invoice'
            mode2 = 'out_refund'
            

        
        
        intrastatkey = namedtuple("intrastatkey",
                                  [ 'Cn8Code','SupplUnitCode','Country','TrCodeA','TrCodeB','DeliveryTerms','ModeOfTransport'])



        
        entries = {}

        sqlreq = """
            select
                inv_line.id
            from
                account_invoice_line inv_line
                join account_invoice inv on inv_line.invoice_id=inv.id
                left join res_country on res_country.id = inv.intrastat_country_id
                left join res_partner on res_partner.id = inv.partner_id
                left join res_country countrypartner on countrypartner.id = res_partner.country_id
                join product_product on inv_line.product_id=product_product.id
                join product_template on product_product.product_tmpl_id=product_template.id
                left join account_period on account_period.id=inv.period_id
            where
                inv.state in ('open','paid')
                and inv.company_id=%s
                and not product_template.type='service'
                and (res_country.intrastat=true or (inv.intrastat_country_id is null
                                                    and countrypartner.intrastat=true))
                and ((res_country.code is not null and not res_country.code=%s)
                     or (res_country.code is null and countrypartner.code is not null
                     and not countrypartner.code=%s))
                and inv.type in (%s, %s)
                and to_char(account_period.date_start, 'YYYY')=%s
                and to_char(account_period.date_start, 'MM')=%s
            """

        cr.execute(sqlreq, (company.id, company.partner_id.country_id.code,
                            company.partner_id.country_id.code, mode1, mode2,
                            decl_datas.year, decl_datas.month))
        lines = cr.fetchall()
        invoicelines_ids = [rec[0] for rec in lines]
        invoicelines = invoiceline_mod.browse(cr, uid, invoicelines_ids, context=context)
        for inv_line in invoicelines:

            #Check type of transaction
            if inv_line.invoice_id.intrastat_transaction_id:
                intrastat_transaction = inv_line.invoice_id.intrastat_transaction_id
            else:
                intrastat_transaction = company.intrastat_transaction_id
           
            if intrastat_transaction.parent_id:
                TrCodeA = intrastat_transaction.parent_id.code
                TrCodeB = intrastat_transaction.code
            else:
                TrCodeA = intrastat_transaction.code
                TrCodeB = '' 
            
            
            if inv_line.invoice_id.transport_mode_id:
                ModeOfTransport = inv_line.invoice_id.transport_mode_id.code
            else:
                ModeOfTransport = company.transport_mode_id.code


            if inv_line.invoice_id.incoterm_id:
                DeliveryTerms = inv_line.invoice_id.incoterm_id.code
            else:
                DeliveryTerms = company.incoterm_id.code

            
            #Check country
            if inv_line.invoice_id.intrastat_country_id:
                Country = inv_line.invoice_id.intrastat_country_id.code
            else:
                Country = inv_line.invoice_id.partner_id.country_id.code


            #Check commodity codes
            intrastat_id = product_mod.get_intrastat_recursively(  cr, uid, inv_line.product_id.id, context=context)
            if intrastat_id:
                intrastatcode = intrastatcode_mod.browse(cr, uid, intrastat_id, context=context)
                Cn8Code = intrastatcode.name
                suppl_unit_code = intrastatcode.suppl_unit_code
            else:
                raise exceptions.Warning(
                    _('Product "%s" has no intrastat code, please configure it') %
                        inv_line.product_id.display_name)

            linekey = intrastatkey(Cn8Code=Cn8Code,
                                   SupplUnitCode = suppl_unit_code,
                                   Country=Country,
                                   TrCodeA=TrCodeA,
                                   TrCodeB=TrCodeB,
                                   DeliveryTerms=DeliveryTerms,
                                   ModeOfTransport=ModeOfTransport)
            
            #We have the key
            #calculate amounts
            # si daca pretul contine tva-ul inclus ???
            if inv_line.price_unit and inv_line.quantity:
                amount = inv_line.price_unit * inv_line.quantity
                if inv_line.invoice_id.currency_id.id != company.currency_id.id:
                   new_context =  dict(context)
                   new_context['date'] = inv_line.invoice_id.date_invoice
                   amount = currency_mod.compute(cr, uid, inv_line.invoice_id.currency_id.id, company.currency_id.id, amount,new_context)
            else:
                amount = 0
            weight = (inv_line.product_id.weight_net or 0.0) * \
                self.pool.get('product.uom')._compute_qty(cr, uid, inv_line.uos_id.id, inv_line.quantity, inv_line.product_id.uom_id.id)
            if (not inv_line.uos_id.category_id or not inv_line.product_id.uom_id.category_id
                    or inv_line.uos_id.category_id.id != inv_line.product_id.uom_id.category_id.id):
                supply_units = inv_line.quantity
            else:
                supply_units = inv_line.quantity * inv_line.uos_id.factor
            amounts = entries.setdefault(linekey, (0, 0, 0))
            amounts = (amounts[0] + amount, amounts[1] + weight, amounts[2] + supply_units)
            entries[linekey] = amounts


        """
     <InsArrivalItem OrderNr="1">
        <Cn8Code>83011000</Cn8Code>
        <InvoiceValue>100</InvoiceValue>
        <StatisticalValue>111</StatisticalValue>
        <NetMass>10</NetMass>
        <NatureOfTransactionACode>6</NatureOfTransactionACode>
        <DeliveryTermsCode>DAP</DeliveryTermsCode>
        <ModeOfTransportCode>5</ModeOfTransportCode>
        <CountryOfOrigin>PL</CountryOfOrigin>
        <CountryOfConsignment>PL</CountryOfConsignment>
    </InsArrivalItem>
        """

        numlgn = 0
        for linekey in entries:
            numlgn += 1
            amounts = entries[linekey]
            
            if dispatchmode:
                item = ET.SubElement(decl, 'InsDispatchItem')
            else:
                item = ET.SubElement(decl, 'InsArrivalItem')     
            item.set('OrderNr', unicode(numlgn))

            tag = ET.SubElement(item, 'Cn8Code')
            tag.text = unicode(linekey.Cn8Code)
            
            tag = ET.SubElement(item, 'InvoiceValue')
            tag.text = unicode(int(round(amounts[0], 0)))
            
            tag = ET.SubElement(item, 'StatisticalValue')
            tag.text = unicode(int(round(amounts[0], 0))) 

            tag = ET.SubElement(item, 'NetMass')
            tag.text = unicode(int(round(amounts[1], 0))) 

            if linekey.SupplUnitCode:
                SupplUnitsInfo = ET.SubElement(item, 'InsSupplUnitsInfo')
                tag = ET.SubElement(SupplUnitsInfo, 'SupplUnitCode')
                tag.text = unicode(linekey.SupplUnitCode)
                tag = ET.SubElement(SupplUnitsInfo, 'QtyInSupplUnits')
                tag.text = unicode(int(round(amounts[2], 0))) 


            tag = ET.SubElement(item, 'NatureOfTransactionACode')
            tag.text = unicode(linekey.TrCodeA) 
            if linekey.TrCodeB:
                tag = ET.SubElement(item, 'NatureOfTransactionBCode')
                tag.text = unicode(linekey.TrCodeB)            

            tag = ET.SubElement(item, 'DeliveryTermsCode')
            tag.text = unicode(linekey.DeliveryTerms) 

            tag = ET.SubElement(item, 'ModeOfTransportCode')
            tag.text = unicode(linekey.ModeOfTransport) 
                       
            tag = ET.SubElement(item, 'CountryOfOrigin')
            tag.text = unicode(linekey.Country)  
            
            tag = ET.SubElement(item, 'CountryOfConsignment')
            tag.text = unicode(linekey.Country)              
        return decl

 