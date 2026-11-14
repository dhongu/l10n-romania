## 19.0.1.0.2 (2026-11-14)

- The zip import (Apps > Import Module) ignores `excludes`: an `eval` guard on the first field
  stops the import while `l10n_ro_report_common` is installed.

## 19.0.1.0.1 (2026-11-14)

- Cannot be installed together with `l10n_ro_report_common`, the module with Python code that does the same
  thing: the manifest lists it under `excludes`.

## 19.0.1.0.0

- First version: the data-only variant of `l10n_ro_report_common`, importable on Odoo Online.
  The bank accounts and the company identification block are the same QWeb templates on
  manual `x_` fields; the RON amount in words is a QWeb template (`amount_in_words`) instead
  of the `res.currency.amount_to_text` override, and spells the thousands and millions
  correctly (*douăsprezece mii*, *două milioane*).
