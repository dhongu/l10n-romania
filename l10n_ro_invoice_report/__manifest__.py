# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Deltatech All Rights Reserved
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
#
##############################################################################

{
    "name": "Romania - Invoice Report",
    "version": "2.1",
    "author": "Dorin Hongu",
    "website": "",

    "description": """

Romania - Invoice Report layout
------------------------------------------

Funftionalitati
 - factura contine: pretul fara tva, valoare si valoare tva
 - La factura au fost adugate campurile delegat si mijloc de transport
 - la partener se poate adauga un text aditinonal care apara pe facura
 - tiparire plata / incasare / dispozitie de plata
 
 
 pip3 install --force-reinstall num2words==0.5.9
 
 
 https://static.anaf.ro/static/10/Anaf/legislatie/Cod_fiscal_norme_31072017.htm#A330
 

    """,

    "category": "Generic Modules",
    "depends": ["base", "account", "account_voucher", "l10n_ro_config",'deltatech_watermark'],


    "data": [
        'views/invoice_report.xml',
        'views/voucher_report.xml',
        'views/payment_report.xml',

        'views/account_invoice_view.xml',
        'views/account_voucher_report.xml',
        'views/account_bank_statement_view.xml',
        'views/statement_report.xml',
        # 'views/res_partner_view.xml',
    ],
    "active": False,
    "installable": True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
