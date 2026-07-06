This module allows you to import the MT940 files exported from Revolut
Business in Odoo as bank statements.

A single Revolut export contains one block per currency wallet, all
reported under the same IBAN. Each currency block is imported against its
own bank journal; wallets for which no matching journal exists (for
example a foreign-currency wallet with no transactions) are silently
skipped instead of blocking the import.
