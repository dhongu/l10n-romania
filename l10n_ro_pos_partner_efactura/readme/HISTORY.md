## 20.0.1.0.0 (2026-10-21)

- Port to 20.0: the rules apply to the POS partner form
  (`point_of_sale.view_partner_form_pos_ui`); the Tax ID is no longer required
  for companies, because `is_company` is now computed from the Tax ID.

## 19.0.1.0.0 (2026-10-21)

- Initial version: the partner form opened from POS requires street, city,
  state, country, the Tax ID for companies and the sector for Bucharest, so the
  invoice can be sent to e-Factura (SPV).
- Romanian translation of the messages; consultant sheet with screenshots
  generated from `tests/test_screenshots.py`.
