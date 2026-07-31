## 19.0.1.0.7 (2026-07-31)

- Fix `TypeError: replace() argument 1 must be str, not bool` when rendering the
  sale order report on a line without a product. `line.product_id.display_name`
  evaluates to `False` on an empty recordset, so `line_name.replace(product_name,
  '', 1)` was called with a boolean. The product name is now stripped from the
  line description only when a product is actually set.
  - `make_description_smaller` had no guard at all and raised on every such line.
  - `exclude_product_name_from_description_offer` guarded the replacement but
    still evaluated `product_name in line_name`, which raises
    `TypeError: 'in <string>' requires string as left operand` in the same case.
