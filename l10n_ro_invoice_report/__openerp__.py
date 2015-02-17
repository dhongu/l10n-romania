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
    "version": "1.0",
    "author": "Dorin Hongu",
    "website": "",

    "description": """

Romania - Invoice Report layout
------------------------------------------


 - factura contine: pretul fara tva, valoare si valoare tva

La companie a fost adaugat un camp nou pentru capitalul social
La factura au fost adugate campurile delegat si mijloc de transport

    """,

    "category": "Generic Modules",
    "depends": ["base", "account", "account_voucher", "l10n_ro"],


    "data": [
        'views/invoice_report.xml',
        'views/voucher_report.xml',
        'company_view.xml',
        'account_invoice_view.xml',
        'account_voucher_report.xml'
    ],
    "active": False,
    "installable": True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
