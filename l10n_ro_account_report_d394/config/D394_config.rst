.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=============================
Romania - D394 Account Report
=============================

Version 3 - starting from 01.07.2016

Configuration
=============

`Company`
=========

* If you have different CAEN code for subsidiaries, create one child company with the right CAEN code (No Separate Chart of Accounts), and linked invoices with the subsidiaries. D394 is taking in consideration subsidiaries invoices when selecting the Parent Company.
* For Fiscal Representative, if it's the case, complete the partner Function by deselecting the 'Is Company' checkbox and after tick it again.


`Users`
=======

* When you print the report, the "Intocmit" fields are linked either with your user, if you don't have a Parent Partner, or with your Parent Partner.

  * If you have an employee responsible for fiscal declarations, make sure that you complete the partner associated with the user the Function field, and update the VAT (TIN) field with "RO" + CNP of the employee.
  * If your Accounting is externalized to a company, and they are responsible for fiscal declarations, make sure that you linked the external users with the partner created for that company.

`Sequences`
===========

* For easier acces and historical overview, configure Sales Journals and Purchases Journals sequences by Fiscalyears. At each begining of the year, create a new sequence (easier by duplicating the one associated with previous year) and complete de Serie First Number and Last Number.


`Account Journals`
==================

* Create one Journal with Fiscal Receipts checked for each POS (Cash Register/Fiscal Printer).


`D394 codes`
============
  
* Before printing the report, update products with the D394 codes, either from the product view in Accounting page, (the field is linked with Product Variants) or bulk method from Accounting -> Configuration -> Misceleaneous -> D394 Codes and update products linked with that code.
