## 19.0.1.0.11 (2026-08-25)

- Keep combo-row colspan calculation compatible with older Odoo 19 builds
  where the core sale report still uses the inline colspan formula and does
  not define `colspan_count`. Prefer the dynamic counter when available and
  fall back to the legacy formula otherwise.

## 19.0.1.0.10 (2026-08-24)

- Combo rows: initialize `combo_name_colspan` from the core `colspan_count`
  instead of the hardcoded `3 + discount + taxes` formula that Odoo 19 no
  longer uses. The old formula would silently drift out of sync with the
  header if core adds or removes optional columns. The module-specific
  increments (numbering, image, lead time columns) are kept, since the
  headers injected by this module do not bump the core counter.
  Added a regression test asserting that a rendered combo row spans exactly
  the header column count. (#518)

## 19.0.1.0.9 (2026-08-24)

- Fix module installation on current Odoo 19: the section colspan XPath was
  anchored on the exact core formula `3 + (1 if display_discount else 0) +
  (1 if display_taxes else 0)`, which core replaced with the dynamic
  `colspan_count` variable. The anchor now targets
  `//tr[@name='tr_section']/t[@t-set='section_name_colspan']`, independent of
  the internal formula. Added a regression assertion on rendered section
  colspans. (#517)

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
