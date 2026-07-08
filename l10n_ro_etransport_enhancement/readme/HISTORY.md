## 18.0.0.2.4 (2026-07-08)

- **Fixed ANAF rejection: "Attribute 'greutateBruta' must appear on element
  'bunuriTransportate'".** Same root cause as the `cantitate` fix above: the
  QWeb template renders `greutateNeta`/`greutateBruta` via `t-att-*`, which
  silently drops a falsy (`0.0`) value from the XML. Unlike `cantitate`, a
  zero weight does not mean the line should be removed — it usually means the
  product's `weight` field (or the shipping weight line) was never filled in,
  while the goods are genuinely being transported. `_l10n_ro_edi_stock_get_template_data`
  now falls back to the other known weight (`greutateNeta` for a zero
  `greutateBruta`, or vice versa) as an approximation, so a missing product
  weight no longer breaks the whole submission.

## 18.0.0.2.3 (2026-07-08)

- **Fixed ANAF rejection: "Attribute 'cantitate' must appear on element
  'bunuriTransportate'".** The zero-quantity cleanup in
  `_l10n_ro_edi_stock_get_template_data` only ran when the *last* stock move
  iterated in the preceding loop belonged to a company with
  `l10n_ro_etransport_get_validated_qty` enabled. When that setting was off, or
  when the order-value loop never ran (`l10n_ro_etransport_get_order_value`
  disabled), a `bunuriTransportate` line with `cantitate == 0` was never
  removed. The QWeb template renders `cantitate` via `t-att-cantitate`, and
  Odoo's QWeb compiler silently drops any `t-att-*` attribute whose value is
  falsy (`0`/`0.0`) and not already a string — so the attribute vanished from
  the generated XML and ANAF's XSD validation rejected the document. The
  cleanup now runs unconditionally in `_l10n_ro_edi_stock_get_template_data`.
