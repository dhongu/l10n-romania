# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: account_storno
#    Author: Goran Kliska
#    mail:   gkliskaATgmail.com
#    Copyright (C) 2011- Slobodni programi d.o.o., Zagreb
#                  http://www.slobodni-programi.hr
#    Contributions:
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
##############################################################################

{
    "name": "Account storno",
    "description": """

Author: Goran Kliska @ Slobodni programi d.o.o.
        http://www.slobodni-programi.hr
Contributions:
  Ivan Vađić @ Slobodni programi d.o.o.
  Tomislav Bošnjaković @ Storm Computers d.o.o.: Bugs report

Description:
 Enables Storno Accounting, a business practice commonly used in
 Eastern European countries.
 Adds new field "Posting policy" with values Storno/Contra on the
 Journal.
 For Storno Journals refund invoices are (usually) done in the
 same journal with negative *(-1) quantities.

 Countries where Storno accounting is mandatory or considered as best practice:
     Czech Republic, Poland, Romania, Russia, China, Slovakia, Slovenia,
     Ukraine, Croatia, Bosnia and Herzegovina, Serbia, Romania, ...

WARNING:
 This module is managing accounting, invoices, and refund wizard.
 Other modules are required for stock, voucher, etc. storno posting.

""",
    "version": "13.1",
    "author": "Slobodni programi d.o.o.",
    "category": "Localisation/Croatia",
    "website": "http://www.slobodni-programi.hr",
    'depends': ['account', 'account_voucher'],
    'data': ['account_view.xml', ],
    'test': [],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
