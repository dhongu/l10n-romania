## 19.0.1.0.0

Migrated to Odoo 19.0.

`stock.valuation.layer` no longer exists in 19.0: the valuation is carried by
the stock move itself and the journal entry is generated from it. The check was
rebuilt on `stock.move` accordingly.

### Rebuilding the valuation side

* `stock.valuation.layer.value` was signed; `stock.move.value` is always
  positive and the direction lives in `l10n_ro_move_type`. The report rebuilds
  the sign from a table derived from
  `stock.move._get_l10n_ro_move_type_account_list()` in `l10n_ro_stock_account`.
  The signs were verified against the entries posted in two production
  databases: the ratio between the balance an entry puts on the valuation
  account and the value of its move comes out at exactly ±1 for every move type
  present, and the totals agree to 0,06%.
* Internal moves (`internal_transfer`, `internal_transit_out`,
  `internal_transit_in`) are left out of **both** sides of the comparison.
  Their sign on `l10n_ro_account_id` is not a constant - it flips with
  `product.category.l10n_ro_stock_account_change`, which decides whether that
  field follows the credited source account or the debited destination account.
  Leaving them out costs no coverage: an internal move takes its value and its
  entry from the same place in the same step, so the two sides cannot drift
  apart for it.
* `remaining_qty` / `remaining_value` are unstored computed fields on
  `stock.move` in 19.0, derived from the moves themselves. They are aggregated
  in Python instead of being read in SQL, and the two checks that looked for a
  drift between the layers and their remainder were dropped: that drift can no
  longer happen.
* The valuation figures now use `product_qty`, the quantity the journal items
  carry, instead of the layer quantity.

### Corrections

* `correction_valuation()` moved from the layer to `stock.move`, and uses
  `_set_value()` and `_create_account_move()` instead of the removed
  `_prepare_out_svl_vals()` and `_account_entry_move()`. It now revalues every
  outgoing move, not only the deliveries the 18.0 version handled.
  In 19.0 one journal entry covers a whole set of moves, so correcting a single
  move pulls in the moves sharing its entry - otherwise the others would be
  left with no entry at all.
* `stock.picking.correction_valuation()` used to call `move_line_ids`, which is
  `stock.move.line` and never had the method; the action was dead. It now calls
  `move_ids`.
* **Fix AML** used to put the counterpart on the stock account itself - the
  entry balanced 371 against 371 and corrected nothing. The counterpart is now
  the expense account of the product, which is what OMFP 1802/2014 prescribes
  for a stock difference (account 371 is debited from 607 for a plus at
  inventory and credited to 607 for a shortage). The accounts are read with a
  representative move in the context, so the per-location accounts configured
  in `l10n_ro_stock_account` are honoured.
* **Fix Valuation** no longer patches the FIFO remainder - there is none to
  patch. It books a real inventory adjustment: the move goes through
  `_action_done()` so the quants move too, taking the goods out of a location
  that actually holds them, and the value is forced through `value_manual`, the
  19.0 mechanism for that. Lines an inventory adjustment cannot express are
  refused up front instead of being booked with the wrong sign: a difference in
  value with no difference in quantity is a revaluation of the cost, and a
  quantity and a value pointing in opposite directions cannot be one movement.
* **Move Valuation on Product Account** recomputes `l10n_ro_account_id` on the
  moves and re-posts their entries, rather than writing two compensating
  layers. It keeps the values the moves already carry, so history is not
  repriced at today's cost.
* **Fix Cost Price** refuses FIFO products, whose cost comes from the incoming
  moves and which `_change_standard_price()` skips - writing the cost there
  would silently change nothing. `disable_auto_svl` was replaced by its 19.0
  counterpart `disable_auto_revaluation`, and the revaluation is dated at the
  end of the reported period rather than today.

### API renames

* `stock.picking.notice` became `l10n_ro_notice` in `l10n_ro_stock_account`.
* `stock.picking.date` was dropped; the date the valuation and the entry follow
  is `date_done`.
* `stock.move.name` was dropped.
* `account.account.company_id` is no longer searchable; the accounts are shared
  through `company_ids`.
* `ir.actions.server.groups_id` became `group_ids`.
* The `<group expand=... string=...>` of the search view is rejected by the RNG
  on both attributes.
* `product.last_purchase_price` comes from `deltatech_purchase_price`, which is
  not a dependency of this module; it is now read only when the field exists.

### Removed

* `views/stock_valuation_layer_view.xml` held a server action bound to the
  valuation layer; the equivalent action on `stock.move` remains.
* `views/stock_move_view.xml` was empty and was not referenced in the manifest.

### Known limitations

* The report compares only what is attributable to a product. Where the stock
  is discharged through global journal entries with no `product_id` on the
  line, the accounting side is not comparable - as was already the case in
  18.0.
* `i18n/ro.po` holds no translation, so the Romanian user sees the English
  strings. It was empty in 18.0 as well.
* With the default `date_to` - the end of the current month - the entries the
  corrections generate are dated in the future and stay in draft.
