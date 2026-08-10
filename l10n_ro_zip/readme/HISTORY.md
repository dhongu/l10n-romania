## 19.0.0.0.2

- **The postal code search now matches word by word, so the word order no longer
  matters.** The nomenclature spells streets named after people surname first
  (`Strada Balcescu Nicolae`), while users type them the natural way round
  ("Nicolae Balcescu") — and a plain substring match never bridged the two. The
  data is not even consistent with itself: 131 rows spell "Balcescu Nicolae" and
  none the reverse, while "Alexandru Ioan Cuza" appears both ways. Since these
  are largely the main streets of every city, a good part of the street data was
  unreachable in practice even with the search fixed in 19.0.0.0.1.
  A multi-word term is now split, and every word must match either `street_name`
  or `street_type`. Typing the street type along with the name ("Strada Mircea")
  keeps working, and a single-word term behaves exactly as before.

## 19.0.0.0.1

- **Fix: searching a street name in the postal code field returned nothing.**
  `res.zip._search_display_name()` only extended the search to `street_name` and
  `street_type` when the operator was *different* from `ilike` — but `ilike` is
  exactly the operator the autocomplete widget uses, so typing a street name in
  the "Postal Code" field on a partner produced zero results. Only a search by
  the postal code itself worked, since that is the model's `_rec_name`. The
  street data was present all along (~52.000 rows, ~38.000 of them at street
  level), which made the symptom look like missing data: users on large cities
  (Bucharest, Constanța, Iași) reported "the streets are gone" and filled in the
  postal code by hand.
  The condition is now `operator in ("ilike", "like", "=")`, and the operator
  received is reused in the extra leaves instead of a hardcoded `ilike`. This
  ports the fix already present on the 18.0 branch, which never reached 19.0.
  Note that on 19.0 only `ilike`/`like` actually reach this method: the ORM
  optimizes `display_name = value` into `name in [value]` on its own.
- Add regression tests for the postal code search (street name, street type,
  `name_search`, and the postal code itself), previously only available on 18.0.
