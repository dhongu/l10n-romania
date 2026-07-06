============================================
MT940 Revolut Format Bank Statements Import
============================================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fl10n--romania-lightgray.png?logo=github
    :target: https://github.com/OCA/l10n-romania/tree/18.0/l10n_ro_account_bank_statement_import_mt940_revolut
    :alt: OCA/l10n-romania

|badge1| |badge2| |badge3|

This module allows you to import the MT940 files exported from Revolut
Business in Odoo as bank statements.

A single Revolut export contains one block per currency wallet, all
reported under the same IBAN. Each currency block is imported against its
own bank journal; wallets for which no matching journal exists (for
example a foreign-currency wallet with no transactions) are silently
skipped instead of blocking the import.

**Table of contents**

.. contents::
   :local:

Bug Tracker
===========

Bugs are tracked on `Terrabit Issues <https://www.terrabit.ro/helpdesk>`_.
In case of trouble, please check there if your issue has already been reported.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
-------

* Terrabit

Contributors
------------

- `Terrabit <https://www.terrabit.ro>`__:

  - Danila <danila@terrabit.ro>

Do not contact contributors directly about support or help with
technical issues.

Maintainers
-----------

.. |maintainer-danila12| image:: https://github.com/danila12.png?size=40px
    :target: https://github.com/danila12
    :alt: danila12

Current maintainers:

|maintainer-danila12|

This module is part of the `OCA/l10n-romania <https://github.com/OCA/l10n-romania/tree/18.0/l10n_ro_account_bank_statement_import_mt940_revolut>`_ project on GitHub.

You are welcome to contribute.
