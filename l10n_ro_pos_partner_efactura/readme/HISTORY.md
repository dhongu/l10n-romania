## 19.0.1.1.1 (2026-10-22)

- Depends on `l10n_ro_anaf_partner_lookup`, the new name of `l10n_ro_anaf_lookup`.

## 19.0.1.1.0 (2026-10-22)

- Search by CUI in the customer list of the Point of Sale: a customer on file is offered, otherwise
  the company is fetched from ANAF (`l10n_ro_anaf_lookup`, no OCA module) and the cashier confirms
  its data in the partner form before it goes on the order.
- Choosing a company as the customer no longer ticks the invoice.
- Takes over the confirmation of `l10n_ro_pos_partner_efactura_anaf`, which is removed, and
  excludes `l10n_ro_pos_partner` (OCA).

## 19.0.1.0.0 (2026-10-21)

- Initial version: the partner form opened from POS requires street, city,
  state, country, the Tax ID for companies and the sector for Bucharest, so the
  invoice can be sent to e-Factura (SPV).
- Romanian translation of the messages; consultant sheet with screenshots
  generated from `tests/test_screenshots.py`.
