.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=============================
Romania - D394 Account Report
=============================

Version 3 - starting from 01.07.2016

Input operations
================

All the datas available in the report are taken from invoices, that's why we need to separate the invoice in 3 major categories, depending on Journal used and Fiscal Receipt field checked or not.

* Invoices - they are invoices inputted in a normal journal (Fiscal Receipt not checked on the journal).
* Simplified Invoices - they are invoices posted in a normal journal (Fiscal Receipt not checked on the journal) but the Fiscal Receipt field on the invoice in not checked.
  
  Fiscal Receipts that contains all the data to be Simplified Invoice are inputted as above.
* Fiscal Receipts - they are invoices that are posted in a journal with Fiscal Receipt checked and Fiscal Receipt field on the invoice checked.

At change of the journal on invoice, the Fiscal Receipt firld is completed with the value from the journal.
