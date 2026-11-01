# Refresh coduri poștale `l10n_ro_zip` (live posta-romana.ro + OSM)

Completează `data/res_zip.sql` (vintage ~2013) cu datele curente, generând un **delta SQL idempotent** (INSERT/UPDATE),
fără a rescrie baza.

## Cum funcționează

| Regim                          | Sursă                                                      | Acoperire                                          |
| ------------------------------ | ---------------------------------------------------------- | -------------------------------------------------- |
| Localități <50k (`sub_50_mii`) | endpoint oficial, adresă goală                             | **completă** — un cod/localitate                   |
| Orașe >50k — străzi existente  | re-query exact pe `res_zip`                                | **~100%** — refresh cod + oficiu                   |
| Orașe >50k — străzi noi        | OSM (Overpass) → query exact pe posta                      | **parțială** — doar cele pe care posta le codifică |
| Orașe >50k — `--by-code`       | căutare inversă pe blocurile de coduri                     | **completă** pe blocurile folosite de oraș         |
| Orașe <50k — străzi            | nume din OSM + codul orașului de la posta (`osm_towns.py`) | cât are OSM; un singur cod pe oraș                 |

> Căutarea pe stradă (`k_adresa`) cere numele exact, deci nu permite enumerarea străzilor. Căutarea inversă
> (`cautare_cod.php`) întoarce însă **toate** străzile unui cod; pentru codul unui oficiu întoarce toate străzile
> oficiului. Cu `--by-code`, `crawl.py` parcurge toate codurile din blocurile folosite de fiecare oraș mare (prefixul de
> 4 cifre din `res_zip.sql`, 100 de coduri/bloc; `--prefix-len 3` = 1000/bloc) și găsește și străzile pe care nu le
> avem. Străzile existente nevăzute în blocuri se caută apoi exact, ca plasă de siguranță. Fișierul oficial descărcabil
> e blocat la Sept-2016.

> Orașele <50k au la posta **un singur cod** pe localitate și nu își listează străzile (căutarea inversă întoarce doar
> localitatea). `osm_towns.py` ia numele străzilor din OpenStreetMap — o interogare Overpass pe județ, cu localitățile
> și străzile cu nume — dă fiecare stradă localității celei mai apropiate (sub 5 km) și le păstrează doar pe cele ale
> orașelor (`place=city/town`), fiindcă satele componente au cod propriu. Rămân doar nume care încep cu un tip de stradă
> (scoate „Parcare”, „DN24”) și drumuri de adresă (fără `service`, `track`, `footway`...). Codul și oficiul vin din
> rândurile `small` ale crawl-ului sau, dacă lipsesc, direct de la posta.

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

# nomenclatorul complet pe orașe, prin blocurile de coduri (~6 h pe toată țara; OSM nu mai e necesar)
python3 crawl.py --by-code --no-osm
python3 build_delta.py

# un singur oraș mare, fără comunele județului (pentru verificare oraș cu oraș)
python3 crawl.py --by-code --no-osm --orase Iasi
python3 build_delta.py

# străzile orașelor mici din OSM (după crawl.py, în același workdir; ~42 de interogări Overpass)
python3 osm_towns.py --judete Vaslui
python3 build_delta.py   # -> și res_zip_osm_delta.sql
```

Resume: re-rularea `crawl.py` sare județele din `done.txt` și, cu `--by-code`, blocurile din `done_blocks.txt`;
rândurile se adaugă în `live_rows.jsonl`.

## Ieșiri

- `live_rows.jsonl` — toate rândurile live (schema res_zip), o linie/rând.
- `res_zip_delta.sql` — INSERT/UPDATE/DELETE, înfășurat în BEGIN…COMMIT.
- `res_zip_osm_delta.sql` — străzile orașelor mici (`src=osm-town`), separat: datele OSM sunt sub licența ODbL.
- `raport.csv` — NEW / RENAME / OFFICE_ADD / CITY (sumar per oraș) / CITY_NEW / CITY_GONE / GONE pentru review uman.

Categorii:

- **comune** (`sub_50_mii`, un cod/localitate): identitate pe `(județ, cod)`, nu pe nume → `NEW` (cod nou), `RENAME`
  (același cod, nume schimbat), `OFFICE_ADD`. Un cod schimbat apare ca `NEW` + `GONE`; `GONE` doar se raportează.
- **orașe** (`peste_50_mii`, street-level): rândurile live se potrivesc pe rândurile existente ale orașului, după id —
  întâi aceeași stradă și același cod, apoi aceeași stradă de bază (fără `bl.`/`nr.`) și același cod, apoi — doar când
  perechea e unică pe ambele părți — aceeași stradă de bază cu cod schimbat și același cod cu stradă redenumită:
  - `CITY_UPDATE` — `UPDATE` pe loc; id-ul rămâne, deci și `res_partner.zip_id`;
  - `CITY_NEW` — `INSERT`;
  - `CITY_GONE` — `DELETE` doar dacă niciun partener nu folosește rândul; cele folosite rămân (FK-ul
    `res_partner.zip_id` e `ON DELETE SET NULL`, deci o ștergere directă ar goli codul la parteneri). Partenerii nu se
    mută pe alt rând cu același cod, fiindcă ar ajunge pe altă stradă.
- Rândurile-oraș cu cod `*` și unitățile poștale (`O.P.`, `Gh.P.`, `O.P.R.M.`, `O.P.D.C.`, `Uz intern`) nu vin de la
  poștă la căutarea pe stradă, deci nu se reîmprospătează și rămân neatinse.

Ce se păstrează sau se deduce, fiindcă posta nu le întoarce:

- `sector` (București): rămâne de pe rândul existent; la rândurile noi e a doua cifră a codului (`01xxxx` = sector 1).
- `address` (adresa oficiului): rămâne de pe rândul existent; la oficiu nou se ia de pe alt rând cu același oficiu.

Delta e **idempotent**: `INSERT`-urile nu au id (vin din secvență) și sunt păzite de `NOT EXISTS`, iar `UPDATE`/`DELETE`
nu mai au efect la a doua rulare. La final, rândurile noi și cele redenumite primesc `country_id`/`state_id`/`city_id`
cu aceleași reguli ca `post_init_hook`.

`existing.py` oprește rularea dacă un rând din `res_zip.sql` nu poate fi citit (altfel id-ul maxim și lista de străzi de
reîmprospătat ar fi greșite).

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
   - **recomandat**: fuzionează datele în `data/res_zip.sql` (instalări noi primesc date curente fără migrare) + delta
     rulat dintr-un script în `migrations/` pentru instalări existente (delta e idempotent și nu pierde `zip_id`); SAU
   - delta separat în `data/`, apelat din `post_init_hook` după `res_zip.sql`. Pe branch dedicat + PR; nu s-a atins încă
     `res_zip.sql`.

## Note legale / politețe

- `DELAY=0.45s` între request-uri; verifică robots.txt + ToS înainte de crawl complet.
- OSM Overpass cere UA descriptiv (nu „Mozilla"), altfel 406.
- Datele OSM sunt © OpenStreetMap contributors, sub licența ODbL (https://www.openstreetmap.org/copyright). Când
  străzile orașelor mici intră în modul, se pun într-un fișier de date separat, cu atribuirea și licența ODbL menționate
  în fișier, în README-ul modulului și pe pagina din Apps Store; codul modulului își păstrează licența.
- București: tratat ca oraș >50k, dar coloana `sector` cere mapare separată (vezi post_init_hook).
