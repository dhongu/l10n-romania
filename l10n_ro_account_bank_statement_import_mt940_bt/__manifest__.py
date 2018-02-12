# Copyright (C) 2016 Forest and Biomass Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'MT940 BT Format Bank Statements Import',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Forest and Biomass Romania, '
              'Odoo Community Association (OCA)',
    'website': 'https://www.forbiom.eu',
    'category': 'Banking addons',
    'depends': ['account_bank_statement_import_mt940_base'],
    'data':['views/account_bank_statement_import_sta_view.xml'],
    'demo': ['demo/demo_data.xml'],
    'installable': True,
}
