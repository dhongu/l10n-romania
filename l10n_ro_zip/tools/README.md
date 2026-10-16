# Refresh coduri poștale `l10n_ro_zip` (live posta-romana.ro + OSM)

Completează `data/res_zip.sql` (vintage ~2013) cu datele curente, generând un **delta SQL idempotent** (INSERT/UPDATE),
fără a rescrie baza.

## Cum funcționează

| Regim                          | Sursă                                 | Acoperire                                          |
| ------------------------------ | ------------------------------------- | -------------------------------------------------- |
| Localități <50k (`sub_50_mii`) | endpoint oficial, adresă goală        | **completă** — un cod/localitate                   |
| Orașe >50k — străzi existente  | re-query exact pe `res_zip`           | **~100%** — refresh cod + oficiu                   |
| Orașe >50k — străzi noi        | OSM (Overpass) → query exact pe posta | **parțială** — doar cele pe care posta le codifică |

> Limitarea orașelor: site-ul posta-romana.ro **nu permite enumerarea** străzilor (`k_adresa` cere nume exact). Fișierul
> oficial descărcabil e blocat la Sept-2016. OSM dă numele curente, posta dă codul oficial — restul rămâne golul real al
> sursei.

## Rulare

```bash
# validare pe un județ
python3 crawl.py --judete Covasna
python3 build_delta.py

# fără descoperire OSM (mai rapid: doar comune + refresh străzi existente)
python3 crawl.py --no-osm

# TOT (lung, ~ore; resumabil — județele terminate sunt în done.txt)
python3 crawl.py
python3 build_delta.py
```

Resume: re-rularea `crawl.py` sare județele din `done.txt` și adaugă în `live_rows.jsonl`.

## Ieșiri

- `live_rows.jsonl` — toate rândurile live (schema res_zip), o linie/rând.
- `res_zip_delta.sql` — INSERT/UPDATE/DELETE, înfășurat în BEGIN…COMMIT.
- `raport.csv` — NEW / RENAME / OFFICE_ADD / CITY_REPLACE / GONE pentru review uman.

Categorii:

- **comune** (`sub_50_mii`, un cod/localitate): identitate pe `(județ, cod)`, nu pe nume → `NEW` (cod nou), `RENAME`
  (același cod, nume schimbat), `OFFICE_ADD`.
- **orașe** (`peste_50_mii`, street-level): `CITY_REPLACE` (DELETE + INSERT setul live), fiindcă re-segmentarea
  `bl./nr.` face diff-ul pe rând inutilizabil.

## STARE și PLAN DE RELUAT (la 2026-06-19)

Validat complet pe **Covasna** și **Iași**. Iași: 2 NEW, 3 RENAME, 411 OFFICE_ADD, oraș 1221→1335 rânduri (322 străzi
noi, ~10 din OSM), 0 GONE fals.

Capcane de date rezolvate în normalizator (`posta.py`): mojibake `ª`=Ș corupt în baza 2013; unificare ortografie veche
`â`↔`î`; dedup fără `src` (altfel refresh+osm-new dublau rândul).

**Rămas de făcut (neînceput):**

1. Full country: `python3 prefetch_osm.py` (~10 min) → `python3 crawl.py` (~2-3h, resumabil prin `done.txt`) →
   `python3 build_delta.py`. Rulează dintr-un workdir extern (ex. scratchpad), nu din `tools/`, ca să nu lași artefacte
   în modul.
2. Review `raport.csv` național (mai ales `GONE` — nimic nu se șterge automat în afara orașelor).
3. Integrare — decizie deschisă:
   - **recomandat**: fuzionează delta în `data/res_zip.sql` (instalări noi primesc date curente fără migrare) + script
     în `migrations/` pentru instalări existente; SAU
   - delta separat în `data/`, apelat din `post_init_hook` după `res_zip.sql`. Pe branch dedicat + PR; nu s-a atins încă
     `res_zip.sql`.

## Note legale / politețe

- `DELAY=0.45s` între request-uri; verifică robots.txt + ToS înainte de crawl complet.
- OSM Overpass cere UA descriptiv (nu „Mozilla"), altfel 406.
- București: tratat ca oraș >50k, dar coloana `sector` cere mapare separată (vezi post_init_hook).
