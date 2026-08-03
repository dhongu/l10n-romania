## 19.0.1.0.8 (2026-08-03)

- Fix the line numbering column (`No.`): it now counts only product lines.
  The number came from `line_index`, the index of the report loop over *all*
  order lines, so sections, subsections and notes consumed numbers even though
  they are not numbered themselves — an order with a section, a note and three
  products printed 2, 4, 6 instead of 1, 2, 3. A dedicated counter is now
  incremented only on the rendered product rows, which also keeps collapsed
  composition lines from consuming numbers.

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
