.. image:: https://img.shields.io/badge/licence=AGPL==3=blue.svg
    :alt: License: AGPL=3

=================================
Odoo/OpenERP Romania Localization
=================================

It extends Odoo/OpenERP to add needed functionnalites to use Odoo/OpenERP in Romania.

l10n_ro_config
==============
Module to provide easy configuration for Romanian adaptation, It provides easy install of the modules from this repo, plus accounting configuration or data upload for some modules. Will be install by default when you install the l10n_ro, and in Settings => Configuration a menu will be created named Romania.

partner_create_by_vat
=====================
Adds an easy method to create partners based on their VAT, if from Romania the partner will be created from Ministry of Finance/ANAF website, and if from EU will be created based on VIES site.

l10n_ro_partner_unique
======================
This allows you to set unique partners by company, VAT and NRC.

l10n_ro_contact_address
=======================
This allows you to set street name and number, block, staircase and apartment number for contacts.
Module depends on web_readonly_bypass from OCA/web repo: https://github.com/OCA/web/tree/8.0/web_readonly_bypass

l10n_ro_siruta
==============
This allows you to manage the Romanian Zones, States, Communes, Cities. The address fields will contain city, commune, state, zone, country, zip.

l10n_ro_fiscal_validation
=========================
Adds partner checking for VAT Subjected on ANAF Asynch Service , VAT on Payment partners checking based on ANAF datas. Validation for VAT on Payment works at date, so you can record older invoices and partner will be threated at invoice date.

account_storno
==============
Provides posting account move lines with negative debit or credit, plus recomputation of refunds changed to have negative quantities. (Functionality proposed to be on Odoo V9)

account_vat_on_payment
======================
Provides VAT on Payment concept, at one invoice with Vat on Payment, taxes are substite by one Uneligible tax, which will become eligible only at payment. (Probably to change the eligibility to reconcile from voucher). (Functionality proposed to be on Odoo V9)

account_compensation
====================
This allows you to manage partners compensation on accounts marked to be reconciled.

account_compensation_vat_on_payment
===================================
This allows you to manage the vat on payment behaviour in compensations.

l10n_ro_account_constrains
==========================
Removes the constrains regarding secondary currency on accounts, journal, move lines.

l10n_ro_invoice_line_not_deductible
===================================
Add the concept of invoice line not deductible, every tax will have a new field, not deductible tax, which will be used on every supplier invoice line marked as not deductible to collect the corresponding tax amount.

l10n_ro_account_bank_statement
==============================
Import of invoices to bank statement will take in consideration residual amounts instead of total amount.
In multicompany database use https://github.com/odoo-romania/extra/tree/8.0/account_statement_operation_multicompany module.

l10n_ro_account_bank_statement_import_mt940_brd
===============================================
Import of bank statements from BRD statements.
Depends on https://github.com/OCA/bank-statement-import/tree/8.0/account_bank_statement_import_mt940_base.

l10n_ro_account_voucher_cash
============================
Adds a voucher sequence on cash journals, restrict the journals available in Pay Invoice wizard, and at every pay it will add a line in the corresponfind Cash Register.

l10n_ro_asset
=============
Module is splitting the asset category in 2 types, view and normal one, to facilitate the import of Chart of Asset Category. The chart can be install from Romania Configuration. Asset are split in fixed and financial assets. Alow reevaluation of assets. Multiple methods changed to respect Romanian Legislation.

l10n_ro_account_voucher_currency_update
=======================================
Adds the method for currency update at partial payments. Modified the dates of reevaluation according to legislation, at the rate from last day of previous month if invoice month is not equal to payment month.

l10n_ro_account_compensation_currency_update
============================================
Adds currency update methods for compensation, if debits or credits are in a different currency than the company one. 

l10n_ro_currency_reevaluation
=============================
Add a method to calculate currency reevaluation based on accounts (adds a boolean field to mark the account for reevaluation). It will calculate the amounts even if you will have other operation after the end of the month, taking in consideration the balance amount at the end of the month.For accounts, partners will use the journal available in wizard, for bank accounts, cash registers will be posted in the corresponding journals to have the balance equal.

l10n_ro_account_period_close
============================
Provides multicompany templates for closing the Incomes, Expenses, VAT at the end of every month.

l10n_ro_invoice_report
======================
This allows you to print invoice report based on romanian layout. Invoice includes voucher if payment is on the same day. Voucher report with amount in word.

l10n_ro_account_report
======================
Provides Romanian reports according to legislation: Trial Balance, Sale/Purchase Journals.

l10n_ro_account_report_d394
===========================
Provides Romanian D394 report print. Two methods for now, use D3394 New Report from July 2016.

l10n_ro_stock
=============
Adds some configuration to warehouse to ease the concepts of Consume/Usage of giving.

l10n_ro_stock_account
=====================
Adds new accounts on location to overwrite the accounts from product/product category to allow moving the same product from one location to another, and to change the financial account (product <=> raw material, product <=> custody). Account moves will be generated for every stock move (based of stock quant) instead of stock quant, will add in context different types of operation and the account moves will defer based on type.

l10n_ro_stock_picking_report
============================
This allows you to print Reports for Reception, Delivery, Internal Transfers.

currency_rate_update
====================
Provides currency rate updated from many web services (National Bank of Romania available).Module copied from OCA/account=financial=tools. (Functionality proposed to be on Odoo V9)

l10n_ro_zipcode - Not finished
==============================
Provides a new location field in partners to allow easy completion of the city, state_id, country, zipcode.

