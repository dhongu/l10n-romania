## 19.0.0.0.11 (2026-11-01)

- Postal codes refreshed from posta-romana.ro for Sfântu Gheorghe, Bacău and Iași: 1,968 streets updated in place, 454
  new streets, and 61 streets the post office no longer lists are removed unless a partner uses them. The localities of
  Covasna get their post office. The towns of Huși, Negrești, Murgeni (Vaslui), Tecuci, Târgu Bujor and Berești
  (Galați) get 521 streets from OpenStreetMap (ODbL, see Credits), with the town's postal code. The update is applied on
  install and, for existing databases, by a migration; partners keep their postal code.
- Postal code refresh tools (`tools/`): the delta updates and deletes a row only if it still has the county and city it
  has in `res_zip.sql`.
- Consultant sheet (`readme/FISA_CONSULTANT.md`) and usage guide (`readme/USAGE.md`), with screenshots.

## 19.0.0.0.10 (2026-11-01)

- Postal code refresh tools (`tools/`): the street type is now part of a street's identity, so *Alee X* and *Strada X*
  under the same code are no longer merged into one row (Iași had 61 such rows reported as gone). `crawl.py --orase`
  takes the county where the city has streets, not a village with the same name. No change to the installed module.

## 19.0.0.0.9 (2026-11-01)

- Postal code refresh tools (`tools/`): `osm_towns.py` gives the towns under 50,000 inhabitants a street list. The
  post office has a single code for these towns and does not list their streets, so the street names come from
  OpenStreetMap (ODbL) and each street gets the town's code from posta-romana.ro. `build_delta.py` writes these rows
  to a separate `res_zip_osm_delta.sql`. `crawl.py --orase` reads a single big city, without the localities of its
  county. No change to the installed module.

## 19.0.0.0.8 (2026-11-01)

- Postal code refresh tools (`tools/`): `crawl.py --by-code` reads every street of the big cities from posta-romana.ro
  by looking up all the codes in the blocks each city uses, instead of only the streets we already know. Streets whose
  name is spelled differently by the post office (`Horia`/`Horea`, word order, an added first name) are now matched to
  the existing row under the same code. Drobeta-Turnu Severin, cut to `Drobeta-Turnu S` in `res_zip.sql`, is now
  recognised and gets its full name back instead of a duplicate set of streets. No change to the installed module.

## 19.0.0.0.7 (2026-11-01)

- Postal code refresh tools (`tools/`): the generated delta now updates city streets in place instead of deleting and
  re-inserting them, so partners keep their postal code; a renamed street or a street with a new code is updated on
  the same row, and rows still used by a partner are never deleted. Post office rows (`O.P.`, `Uz intern`...) are left
  as they are. The Bucharest sector and the post office address are kept (or derived for new rows), the delta can be
  run more than once, and reading `res_zip.sql` no longer skips the last row of each `INSERT` block. No change to the
  installed module.

## 19.0.0.0.6 (2026-10-22)

- Listed on Odoo Apps as *Romania - Postal Codes* (was *Romania - Coduri Postale*), with the same title on the Apps banner.
  The technical name `l10n_ro_zip` does not change.

## 19.0.0.0.5 (2026-10-09)

- Odoo Apps banner (`static/description/main_screenshot.png`), generated from `banner.json`.

## 19.0.0.0.4 (2026-10-06)

- The postal code dropdown shows a second, greyed-out column: for a street,
  `Strada Mircea Vulcan` followed by `010101 · Bucuresti, Sector 1, B` (postal
  code, city, sector when filled in, county code); for a code without a street,
  the city followed by the postal code and the county code. Empty parts are
  left out, and the county is skipped when it repeats the city. The plain name
  used on documents and reports is unchanged.

## 19.0.0.0.3

- Own module icon in the flat style of the Terrabit modules, instead of the missing or generic one.

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
