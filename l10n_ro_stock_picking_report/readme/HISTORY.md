## 19.0.1.3.2 (2026-08-15)

- Imp: `stock.picking.delegate_id` is now indexed. The same field is declared in `deltatech_cmr_document`, so the attribute is set in both modules — the last one loaded decides.
  Context: `res_partner` is referenced by ~158 foreign-key columns; on a production database 77 of them had no index, so a single partner deletion triggered sequential scans over 3.180 MB of tables. Deleting 5.350 merged partner records took over 8 minutes without indexes and 190 seconds with them, foreign keys left ENABLED.

## 19.0.1.3.1

- **Fix:** internal transfer report no longer crashes with
  `ZeroDivisionError` when a move has only the done quantity filled in
  (`quantity`) and no demand (`product_uom_qty`), which leaves
  `product_qty` at 0. The unit price now falls back to `quantity` and the
  division is skipped entirely when both quantities are 0. The previous
  `or 1` fallback applied to the division result, not the denominator, so
  it never protected against this case.

## 19.0.1.2.10

- **Fix:** reception report no longer crashes on Odoo 19. `stock.picking` lost
  the `group_id` field (the procurement group mechanism was replaced by
  `stock.reference` / `reference_ids`), which raised
  `AttributeError: 'stock.picking' object has no attribute 'group_id'` when
  printing reception NIRs. The shared `report_reception_text` template now
  branches on field existence so it renders correctly for both `stock.picking`
  (`reference_ids`) and the `stock.picking.cumulative` report model (`group_id`).
