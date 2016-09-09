.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=============================
Romania - D394 Account Report
=============================

Version 3 - starting from 01.07.2016

Fields added
============


`Companies <https://github.com/odoo-romania/l10n-romania/tree/8.0/l10n_ro_account_report_d394/models/res_company.py>`_.
===========================================================================================================================

* ANAF Crosschecking - option to allow ANAF crosschecking.
* Is Fiscal representative - boolean field to know if the company is fiscal represented by another partner.
* Fiscal representative - Partner representing the company.


`Country states <https://github.com/odoo-romania/l10n-romania/tree/8.0/l10n_ro_account_report_d394/models/res_country_state.py>`_.
======================================================================================================================================

* Order Code - Country state order.

The field in completed/updated at module install/update from data file.


`Sequences <https://github.com/odoo-romania/l10n-romania/tree/8.0/l10n_ro_account_report_d394/models/ir_sequence.py>`_.
===========================================================================================================================

* Sequence Type - Selection field to choose the type of invoicing:

  * Normal invoicing
  * Autoinvoicing emmited by supplier (Customer Invoice)
  * Autoinvoicing emitted by company (Supplier Invoice)
* Serie First Number - First number of sequence at the beggining of fiscalyear - available in internal decision about ordering.
* Serie Last Number - Last number of sequence at the beggining of fiscalyear - available in internal decision about ordering.
* Partner - In autoinvoicing, the field in storing the partner associated with this sequence.


`Account Journals <https://github.com/odoo-romania/l10n-romania/tree/8.0/l10n_ro_account_report_d394/models/account_journal.py>`_.
======================================================================================================================================

* Fiscal Receipt - Field to mark the journal as fiscal receipts journal.
* Sequence Type - Selection field to choose the type of invoicing:

  * Normal invoicing
  * Autoinvoicing emmited by supplier (Customer Invoice)
  * Autoinvoicing emitted by company (Supplier Invoice)
  
  Field is related to Sequence Type field from Journal Sequence.
* Partner - In autoinvoicing, the field in storing the partner associated with this sequence.
  
  Field is related to Partner field from Journal Sequence.


`Account Invoice <https://github.com/odoo-romania/l10n-romania/tree/8.0/l10n_ro_account_report_d394/models/account_invoice.py>`_.
=====================================================================================================================================

* Operation Type - Computed field to get operation type specified in ANAF specification.
  Options availables are:

  * L - Customer Invoice
  * A - Supplier Invoice
  * LS - Special Customer Invoice
  * AS - Special Supplier Invoice
  * AI - VAT on Payment Supplier Invoice
  * V - Inverse Taxation Customer Invoice
  * C - Inverse Taxation Supplier Invoice
  * N - Individuals Supplier Invoice
* Sequence Type - Selection field to choose the type of invoicing:

  * Normal invoicing
  * Autoinvoicing emmited by supplier (Customer Invoice)
  * Autoinvoicing emitted by company (Supplier Invoice)

  Field is related to Sequence Type field from Journal and Journal Sequence.
* Partner Type - Computed field to get partner type specified in ANAF specification.
  Options availables are:

  * 1 - Romanian Companies with Vat Subjected
  * 2 - Romanian Companies without Vat Subjected or individuals
  * 3 - EU Partnes
  * 4 - Extra EU Partnes
* Origin Type - Selection field for type of aquisition from individuals
  Options availables are:

  * 1 - Invoice
  * 2 - Slip
  * 3 - Trading Book
  * 4 - Contract
* Special Taxation - Boolean field to mark the invoices with Special Taxation, e.g. Tourism, Second hand goods reseller...
* Invoice Serie - Computed field to get the serie of the invoice splitted the invoice number/supplier invoice number.
* Invoice Number - Computed field to get the number of the invoice splitted the invoice number/supplier invoice number.
* Normal Taxes - On invoices with fiscal position different than National, the field computes the normal taxes associated with invoice line products, to easily fetch the vat quotas in D394.


`D394 codes <https://github.com/odoo-romania/l10n-romania/tree/8.0/l10n_ro_account_report_d394/models/d394_code.py>`_.
==========================================================================================================================
  
* Parent Code - Added for hierarchical use of codes, useful in "Rezumat" tags in report.
