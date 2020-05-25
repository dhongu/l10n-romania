# -*- coding: utf-8 -*-
# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
{
    "name": "Romania - Stock Report",
    "version": "1.0",
    "author": "Terrabit",
    "website": "http://www.terrabit.ro",
    "category": "Warehouse",
    "depends": ['stock_account', 'account', 'l10n_ro_config', 'l10n_ro_stock', 'purchase_stock','date_range'],

    'data': [
        'report/daily_stock_report_view.xml',
        'report/daily_stock_report_template.xml',
        'report/storage_sheet_report_view.xml',
        'report/storage_sheet_report_template.xml'
    ],
    'installable': True,
    'active': False,
}
