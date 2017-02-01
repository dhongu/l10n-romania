.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=============================
Romania - D394 Account Report
=============================

This module allows you to print the D394 report, on a monthly basis.
Module in designed from ANAF specifications available at

https://chat.anaf.ro/d394.nsf

Module depends on many modules which are adding needed fields and methods to print the report.

Installation
============

To install this module, you need to:

* clone the branch 8.0 of the repository https://github.com/odoo-romania/l10n-romania
* add the path to this repository in your configuration (addons-path)
* update the module list
* search for "Romania - D394 Account Report" in your addons
* install the module

Usage
=====

In the Accounting -> Reporting -> Legal Reports -> Accounting Reports
you have a new menu called D394. At launch of the wizard, Odoo will
print the D394 based on the operations inputed.

More configuration and doc about it in `D394.rst <https://github.com/odoo-romania/l10n-romania/tree/8.0/l10n_ro_account_report_d394/config/D394.rst>`_.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/odoo-romania/l10n-romania/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/odoo-romania/l10n-romania/issues/new?body=module:%20l10n_ro_account_report_d394%0Aversion:%208.0.1.0.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Fekete Mihai <feketemihai@gmail.com>
