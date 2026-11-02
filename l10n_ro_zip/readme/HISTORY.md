## 19.0.0.0.19 (2026-11-02)

- The streets of the small towns from OpenStreetMap (ODbL) move to the new module `l10n_ro_zip_osm`, installed
  automatically with this one. The streets already in a database stay; a new database gets them with the new
  module.

## 19.0.0.0.18 (2026-11-02)

- The module no longer depends on `l10n_ro_city`: the county of each postal code comes from its first two
  digits, from a list in the module (Bucharest 01–06, Giurgiu 08), and the Bucharest codes are linked to their
  sector by its name. The codes are linked to the localities of `l10n_ro_city` when it is installed, as
  before, also when `l10n_ro_city` is installed in the same run or later: creating Romanian localities links
  the codes that have none. Without it they have the county only. The 19.0.0.0.17 migration becomes 19.0.0.0.18 and fills the
  county of the codes that had none, such as the Bucharest codes outside the sectors.
- The postal code is indexed: applying the update on install or upgrade takes about 5 seconds instead of 19.

## 19.0.0.0.17 (2026-11-02)

- More postal codes linked to their locality: the post office writes some names with a hyphen (Miercurea-Ciuc,
  Popești-Leordeni, Târgu-Jiu), others as "Village (Commune)" for the villages with the same name in a county, and the
  old list has "ª" for "Ș". A row is linked only to a single locality, or to the single one with its postal code. On a
  new database, the rows without a locality go from 1,656 to 193.
- Needs l10n_ro_city 19.0.1.10.2, which adds Breaza (Prahova), Băile Govora, Băile Olănești, Ocnele Mari and Eforie and
  fixes Sfântu Gheorghe and Popești-Leordeni. On update, the existing rows are linked again where they have no locality,
  and the Giurgiu rows get their county (prefix fixed in l10n_ro_city 19.0.1.10.1).

## 19.0.0.0.16 (2026-11-02)

- Street names from OpenStreetMap (ODbL, see Credits) for the small towns where the post office has a single postal
  code: 269 towns (Pantelimon, Voluntari, Lugoj, Râmnicu Sărat, Tecuci, Câmpina, Bușteni and others) get 15,968
  streets with the town's postal code, instead of the 521 streets of six towns. The nomenclature now has about 73,000
  postal codes. The 19.0.0.0.15 migration becomes 19.0.0.0.16.

## 19.0.0.0.15 (2026-11-02)

- Postal codes refreshed from posta-romana.ro for the last eight counties: Sibiu, Suceava, Teleorman, Timiș, Tulcea,
  Vaslui, Vâlcea and Vrancea. The update now covers the whole country: 26,937 city streets updated in place, 6,821 new
  (plus the 521 OSM streets of six small towns), 1,276 no longer listed and removed unless a partner uses them, 13,297
  localities get their post office, 25 new localities, 37 renamed. The 19.0.0.0.14 migration becomes 19.0.0.0.15 and
  applies the larger update.
- Postal code refresh tools (`tools/`): the new streets of Timișoara, which the post office lists under the locality
  "Timiș", are put back under Timișoara.
- Description, consultant sheet and Apps banner give the new size of the nomenclature: about 58,000 postal codes.

## 19.0.0.0.14 (2026-11-02)

- Postal codes refreshed from posta-romana.ro for 18 more counties: Dâmbovița, Dolj, Galați, Giurgiu, Gorj, Harghita,
  Hunedoara, Ialomița, Iași (the whole county), Ilfov, Maramureș, Mehedinți, Mureș, Neamț, Olt, Prahova, Sălaj and Satu
  Mare. With the counties of 19.0.0.0.13, the update now covers 34 counties: 22,088 city streets updated in place, 5,504
  new (plus the 521 OSM streets of six small towns), 1,022 no longer listed and removed unless a partner uses them,
  10,693 localities get their post office, 25 new localities, 29 renamed. The 19.0.0.0.13 migration becomes
  19.0.0.0.14 and applies the larger update.

## 19.0.0.0.13 (2026-11-02)

- Postal codes refreshed from posta-romana.ro for seven more counties: București, Buzău, Călărași, Caraș-Severin, Cluj,
  Constanța and Covasna (the whole county, not only Sfântu Gheorghe). With the counties of 19.0.0.0.12, the update now
  covers 16 counties and Iași: 13,231 city streets updated in place, 3,423 new (plus the 521 OSM streets of six small
  towns), 718 no longer listed and removed unless a partner uses them, 5,148 localities get their post office, 11 new
  localities, 10 renamed (Basarabi is now Murfatlar). The 19.0.0.0.12 migration becomes 19.0.0.0.13 and applies the
  larger update.

## 19.0.0.0.12 (2026-11-02)

- Postal codes refreshed from posta-romana.ro for the counties Alba, Arad, Argeș, Bacău, Bihor, Bistrița-Năsăud,
  Botoșani, Brăila and Brașov, on top of Sfântu Gheorghe and Iași: the streets of Alba Iulia, Arad, Pitești, Bacău,
  Onești, Oradea, Bistrița, Botoșani, Brăila and Brașov are read by postal code (7,384 streets updated in place, 1,972
  new, 281 no longer listed and removed unless a partner uses them), 3,565 localities get their post office, 9 new
  localities, 7 renamed. The 19.0.0.0.11 migration becomes 19.0.0.0.12 and applies the larger update. On a database
  already at 19.0.0.0.11, two Iași street segments matched to the wrong street are put back, and the copies left twice
  are removed unless a partner uses them.
- Postal code refresh tools (`tools/`): a street segment whose name is unchanged but whose code changed (Brăila renumbered
  its streets) is matched to its existing row when the pair is unique; a row whose code belongs to another county is
  ignored. Every matched city row gets all its columns from the post office, not only those that differ from
  `res_zip.sql`, so the result is the same whichever earlier update the database had.

## 19.0.0.0.11 (2026-11-01)

- Postal codes refreshed from posta-romana.ro for Sfântu Gheorghe, Bacău and Iași: 1,968 streets updated in place, 454
  new streets, and 61 streets the post office no longer lists are removed unless a partner uses them. The localities of
  Covasna get their post office. The towns of Huși, Negrești, Murgeni (Vaslui), Tecuci, Târgu Bujor and Berești
  (Galați) get 521 streets from OpenStreetMap (ODbL, see Credits), with the town's postal code. The update is applied on
  install and, for existing databases, by a migration; partners keep their postal code.
- Postal code refresh tools (`tools/`): the delta updates and deletes a row only if it still has the county and city it
  has in `res_zip.sql`.
- The postal code SQL files are read as UTF-8, whatever the server locale.
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
