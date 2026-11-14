## 20.0.1.0.0

- Port to 20.0: the RO header replaces the `information_block` and `address` blocks of
  the invoice (no longer a `<div>`), the line description prints `label`, `t-esc` becomes
  `t-out`, `amount_in_words` gets its values as `t-call` attributes, `report_file` is dropped
  and the delegate also accepts the contacts of a company.

## 19.0.1.0.0

- First version: the data-only variant of `l10n_ro_invoice_report`, importable on Odoo Online.
  The report templates are the same QWeb, on manual `x_` fields; the helpers of the report
  (deliveries, receipt detection, journal type and direction of the payments, amount in words)
  are computed in QWeb; the onchange of the delegate, the payment bank account of the partner
  and *Set origin from pickings* are automation rules and server actions; the settings are on
  the company form. The manifest excludes `l10n_ro_invoice_report`.
