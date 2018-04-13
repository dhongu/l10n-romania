# -*- coding: utf-8 -*-
# ©  2018 Terrabit
# See README.rst file on addons root folder for license details

{
    "name": "Deltatech Declaratii ANAF",
    'version': '11.0.1.0.0',
    "author": "Terrabit, Dorin Hongu",
    "website": "www.terrabit.ro",
    "description": """
    
   
    """,

    "category": "Generic Modules",
    "depends": [
        'account','l10n_ro'
    ],

    "data": [
        'views/declarations_view.xml',
        'views/d394_view.xml',
        'wizard/run_declaration_view.xml'
    ],

    "active": False,
    "installable": True,
    'application': True,
}
