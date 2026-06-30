## 19.0.1.2.10

- **Fix:** reception report no longer crashes on Odoo 19. `stock.picking` lost
  the `group_id` field (the procurement group mechanism was replaced by
  `stock.reference` / `reference_ids`), which raised
  `AttributeError: 'stock.picking' object has no attribute 'group_id'` when
  printing reception NIRs. The shared `report_reception_text` template now
  branches on field existence so it renders correctly for both `stock.picking`
  (`reference_ids`) and the `stock.picking.cumulative` report model (`group_id`).
