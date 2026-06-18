## 18.0.1.2.9

- Fix: reading stock valuation layers in the reception report (`_get_line`)
  now uses `sudo()`. Standard Inventory users can print reception reports
  without requiring direct read access to `stock.valuation.layer`.
