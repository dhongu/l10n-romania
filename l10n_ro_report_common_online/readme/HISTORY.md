## 20.0.1.0.0

- First version: the data-only variant of `l10n_ro_report_common`, importable on Odoo Online.
  The bank accounts and the company identification block are the same QWeb templates on
  manual `x_` fields; the RON amount in words is a QWeb template (`amount_in_words`) instead
  of the `res.currency.amount_to_text` override, and spells the thousands and millions
  correctly (*douăsprezece mii*, *două milioane*).
