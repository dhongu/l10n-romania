# -*- coding: utf-8 -*-
# ©  2016 Forest and Biomass Romania
# See README.rst file on addons root folder for license details

{
    "name": "Romania - D394 Account Report",
    "version": "8.0.1.0.0",
    "author": "Forest and Biomass Romania",
    "website": "http://www.forbiom.eu",
    "category": "Romania Adaptation",
    "depends": [
        'account',
        'report',
        'account_storno',
        'l10n_ro_invoice_report',
        'l10n_ro_config',
        'l10n_ro_hr',
        'l10n_ro_contact_address',
        'l10n_ro_fiscal_validation',
    ],
    'data': ['data/394_codes.xml',
             'data/res_country_state.xml',
             'views/d394_code_view.xml',
             'views/product_view.xml',
             'views/account_invoice_view.xml',
             'views/account_journal_view.xml',
             'views/ir_sequence_view.xml',
             'views/res_company_view.xml',
             'wizard/d394_view.xml',
             'security/ir.model.access.csv', ],
    'installable': True,
    'auto_install': False,
}
