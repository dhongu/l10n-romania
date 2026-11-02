"""
Diff live_rows.jsonl vs res_zip.sql -> res_zip_delta.sql + raport.csv.

Doua regimuri, pe sursa randului live:
  - 'small' (comune <50k): identitate pe (judet, cod)
        NEW        -> INSERT
        RENAME     -> UPDATE city (acelasi cod, nume schimbat)
        OFFICE_ADD -> UPDATE office (existent gol, live are)
    Un cod schimbat apare ca NEW + GONE (GONE doar raportat, nu sters).
  - 'code'/'refresh'/'osm-new' (orase >50k): potrivire pe randurile EXISTENTE ale orasului
        CITY_UPDATE -> UPDATE pe loc (id pastrat, deci si res_partner.zip_id)
                       pasii 1-2 intai cu tipul strazii (Alee X si Strada X sunt doua strazi),
                       apoi fara (tip schimbat).
                       pas 1: aceeasi strada + acelasi cod; pas 2: aceeasi strada de baza
                       + acelasi cod (re-segmentare bl./nr.); pas 3: aceeasi strada de baza,
                       cod schimbat; pas 4: acelasi cod, strada redenumita. Pasii 3-4 doar
                       cand perechea e unica pe ambele parti. Pas 5: acelasi cod, nume
                       asemanator (Horia/Horea, ordinea cuvintelor) sau prenume adaugat, doar
                       cand perechea e unica in acel cod.
        CITY_NEW    -> INSERT
        CITY_GONE   -> DELETE doar daca randul nu e folosit de niciun partener
                       (FK res_partner.zip_id e ON DELETE SET NULL); altfel ramane.

Delta e idempotent: INSERT-urile nu au id (vin din secventa) si sunt pazite de
NOT EXISTS, UPDATE/DELETE se refac fara efect. Sectorul (Bucuresti) si adresa
oficiului se pastreaza de pe randul existent sau se deduc (cod / nume oficiu).
La final, randurile noi si cele redenumite primesc country_id/state_id/city_id
cu aceleasi reguli ca post_init_hook.

GONE e raportat DOAR pentru judetele/orasele atinse de acest crawl (altfel,
la rulare partiala, ar lista tot restul tarii).
"""
# pylint: disable=print-used

import argparse
import csv
import difflib
import json
import os

import existing
import posta

SQL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "res_zip.sql")

# post_init_hook: sector Bucuresti -> res.city (l10n_ro_city)
SECTOR_CITY = {
    "1": "RO_179141",
    "2": "RO_179150",
    "3": "RO_179169",
    "4": "RO_179178",
    "5": "RO_179187",
    "6": "RO_179196",
}


def esc(s):
    return (s or "").replace("'", "''")


def load_live(path):
    rows = []
    seen = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            # dedup pe identitatea reala a randului — FARA src (altfel acelasi rand
            # venit si din 'refresh' si din 'osm-new' supravietuieste de 2 ori).
            # 'refresh' e scris inaintea 'osm-new' -> prima aparitie (refresh) castiga.
            # tipul face parte din identitate: 'Alee X' si 'Strada X' cu acelasi cod sunt doua strazi
            k = (
                posta.norm_key(r["state"]),
                posta.norm_key(r["city"]),
                posta.norm_key(r["street_type"]),
                posta.norm_key(r["street_name"]),
                r["name"],
            )
            if k not in seen:
                seen.add(k)
                rows.append(r)
    return rows


def insert_stmt(r, sector, address):
    """INSERT fara id, pazit de NOT EXISTS -> se poate rula de mai multe ori."""
    return (
        "INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)\n"
        f"SELECT '{esc(r['state'])}', '{esc(r['city'])}', '{esc(r['street_type'])}', "
        f"'{esc(r['street_name'])}', '{esc(r['name'])}', '{esc(sector)}', '{esc(r['office'])}', '{esc(address)}'\n"
        f"WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='{esc(r['name'])}' AND state='{esc(r['state'])}' "
        f"AND city='{esc(r['city'])}' AND COALESCE(street_type, '')='{esc(r['street_type'])}' "
        f"AND COALESCE(street_name, '')='{esc(r['street_name'])}');\n"
    )


def match_city(ex_city, live_rows):
    """Potriveste randurile live ale unui oras pe cele existente.

    Returneaza (matched [(ex, live)], new [live], gone [ex]).
    """
    pending = list(ex_city)
    matched, unmatched = [], []

    def typ(x):
        return posta.norm_key(x["street_type"])

    def name(x):
        return posta.norm_key(x["street_name"])

    def base(x):
        return posta.norm_key(posta.base_street(x["street_name"]))

    # intai cu tipul strazii ('Alee X' si 'Strada X' cu acelasi cod sunt doua strazi), apoi fara
    # (tip schimbat: Stradela -> Strada)
    for keyf, unique in (
        (lambda x: (typ(x), name(x), x["name"]), False),
        (lambda x: (name(x), x["name"]), False),
        (lambda x: (typ(x), base(x), x["name"]), False),
        (lambda x: (base(x), x["name"]), False),
        (lambda x: base(x), True),
        (lambda x: x["name"], True),
    ):
        by_key = {}
        for m in pending:
            by_key.setdefault(keyf(m), []).append(m)
        live_count = {}
        for r in live_rows:
            k = keyf(r)
            live_count[k] = live_count.get(k, 0) + 1
        unmatched = []
        for r in live_rows:
            k = keyf(r)
            lst = by_key.get(k)
            if lst and (not unique or (len(lst) == 1 and live_count[k] == 1)):
                matched.append((lst.pop(0), r))
            else:
                unmatched.append(r)
        used = {id(m) for m, _r in matched}
        pending = [m for m in pending if id(m) not in used]
        live_rows = unmatched
    fuzzy = match_similar(pending, live_rows)
    matched.extend(fuzzy)
    used_ex = {id(m) for m, _r in fuzzy}
    used_live = {id(r) for _m, r in fuzzy}
    return matched, [r for r in live_rows if id(r) not in used_live], [m for m in pending if id(m) not in used_ex]


SIMILAR_MIN = 0.8


def _tokens(street_name):
    return posta.norm_key(street_name).split()


def similarity(a, b):
    """Asemanarea a doua nume de strada, insensibila la ordinea cuvintelor.

    1.0 la acelasi set de cuvinte (Romulus Cioflec / Cioflec Romulus). Incluziunea
    (Martinovics / Martinovics Ignac) e tratata separat, in is_subset_pair.
    """
    ta, tb = set(_tokens(a)), set(_tokens(b))
    if not ta or not tb:
        return 0.0
    if ta == tb:
        return 1.0
    return difflib.SequenceMatcher(None, " ".join(sorted(ta)), " ".join(sorted(tb))).ratio()


def is_subset_pair(a, b):
    """Un nume e celalalt plus cel mult un cuvant (prenume adaugat), iar partea comuna
    are un cuvant de cel putin 3 litere — nu '1' / '1 Mai'."""
    ta, tb = set(_tokens(a)), set(_tokens(b))
    small, big = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    if not small or small == big or not small <= big or len(big - small) > 1:
        return False
    return any(len(t) >= 3 and t.isalpha() for t in small)


def match_similar(pending, live_rows):
    """Pas 5: acelasi cod, nume asemanator; fiecare rand o data.

    Asemanarea de text (Horia/Horea) se ia de la scorul cel mai mare in jos. Incluziunea
    de cuvinte se accepta doar cand perechea e unica pe ambele parti in acel cod, ca la
    pasii 3-4 — altfel 'Mihai' s-ar putea lega de 'Mihai Viteazul' in loc de 'Mihai Eminescu'.
    """
    by_zip = {}
    for m in pending:
        by_zip.setdefault(m["name"], []).append(m)
    pairs, subset = [], []
    for r in live_rows:
        for m in by_zip.get(r["name"], []):
            score = similarity(m["street_name"], r["street_name"])
            if score >= SIMILAR_MIN:
                pairs.append((score, m, r))
            elif is_subset_pair(m["street_name"], r["street_name"]):
                subset.append((m, r))
    n_ex, n_live = {}, {}
    for m, r in subset:
        n_ex[id(m)] = n_ex.get(id(m), 0) + 1
        n_live[id(r)] = n_live.get(id(r), 0) + 1
    pairs.sort(key=lambda p: -p[0])
    pairs += [(0.0, m, r) for m, r in subset if n_ex[id(m)] == 1 and n_live[id(r)] == 1]
    out, used = [], set()
    for _score, m, r in pairs:
        if id(m) in used or id(r) in used:
            continue
        used.update((id(m), id(r)))
        out.append((m, r))
    return out


def city_update(m, r, office_addr):
    """SET-urile pentru un rand de oras potrivit; gol daca nu s-a schimbat nimic."""
    sets = {}
    if r["city"] != m["city"]:  # ex. nume trunchiat in res_zip.sql ('Drobeta-Turnu S')
        sets["city"] = r["city"]
        sets["country_id"] = None
    if r["name"] != m["name"]:
        sets["name"] = r["name"]
        # codul poate muta randul in alt sector -> sector si relatii recalculate
        sector = posta.sector_for(m["state"], r["name"])
        if sector != m["sector"]:
            sets["sector"] = sector
        sets["country_id"] = None
    if r["street_name"] != m["street_name"]:
        sets["street_name"] = r["street_name"]
    if r["street_type"] and r["street_type"] != m["street_type"]:
        sets["street_type"] = r["street_type"]
    if r["office"] and posta.norm_key(r["office"]) != posta.norm_key(m["office"]):
        sets["office"] = r["office"]
        # adresa tine de oficiu: o luam pe cea a noului oficiu, daca o stim
        new_addr = office_addr.get(posta.norm_key(r["office"]), "")
        if new_addr != m["address"]:
            sets["address"] = new_addr
    sector = posta.sector_for(m["state"], r["name"])
    if sector and not m["sector"] and "sector" not in sets:
        sets["sector"] = sector
    return sets


def mapping_sql():
    """country_id/state_id/city_id pentru randurile fara country_id (noi sau redenumite),
    cu aceleasi reguli ca post_init_hook."""
    sector_cases = " ".join(f"WHEN '{s}' THEN '{x}'" for s, x in SECTOR_CITY.items())
    return f"""-- === relatii pentru randurile noi/redenumite (ca post_init_hook) ===
CREATE TEMP TABLE _zip_remap ON COMMIT DROP AS SELECT id FROM res_zip WHERE country_id IS NULL;
UPDATE res_zip z SET country_id = c.id FROM res_country c, _zip_remap t WHERE z.id = t.id AND c.code = 'RO';
UPDATE res_zip z SET state_id = s.id
  FROM res_country_state s, _zip_remap t
 WHERE z.id = t.id AND s.l10n_ro_prefix_zip = SUBSTRING(z.name, 1, 2);
CREATE EXTENSION IF NOT EXISTS unaccent;
UPDATE res_zip z SET city_id = rc.id
  FROM res_city rc, _zip_remap t
 WHERE z.id = t.id AND unaccent(z.city) = unaccent(rc.name->>'en_US')
   AND z.state_id = rc.state_id AND z.name = rc.zipcode;
UPDATE res_zip z SET city_id = rc.id
  FROM res_city rc, _zip_remap t
 WHERE z.id = t.id AND unaccent(z.city) = unaccent(rc.name->>'en_US')
   AND z.state_id = rc.state_id AND z.city_id IS NULL;
UPDATE res_zip z SET city_id = rc.id, state_id = rc.state_id
  FROM ir_model_data d, res_city rc, _zip_remap t
 WHERE z.id = t.id AND d.module = 'l10n_ro_city' AND d.model = 'res.city' AND d.res_id = rc.id
   AND d.name = CASE z.sector {sector_cases} END;
"""


def gone_sql(gone_ids):
    """Randurile de oras disparute: stergem doar ce nu e folosit de niciun partener.

    FK res_partner.zip_id e ON DELETE SET NULL, deci o stergere directa ar goli codul.
    Nu mutam partenerii pe alt rand cu acelasi cod: ar ajunge pe alta strada.
    """
    ids = ", ".join(str(i) for i in sorted(gone_ids))
    arr = f"ARRAY[{ids}]"
    return f"""-- === orase GONE ({len(gone_ids)} randuri; cele folosite de parteneri raman) ===
DELETE FROM res_zip z
 WHERE z.id = ANY({arr})
   AND NOT EXISTS (SELECT 1 FROM res_partner p WHERE p.zip_id = z.id);
"""


def write_cities(f, cities, big_cities, office_addr, gone_ids):
    """UPDATE/INSERT per oras + DELETE pentru randurile disparute nefolosite; intoarce nr. de UPDATE."""
    n_upd = 0
    start = len(gone_ids)
    for key, (matched, city_new, city_gone) in cities.items():
        rows = big_cities[key]
        f.write(f"-- === oras {rows[0]['city']} ({rows[0]['state']}) ===\n")
        for m, r in matched:
            sets = city_update(m, r, office_addr)
            if sets:
                n_upd += 1
                sql_sets = ", ".join(f"{k}=NULL" if v is None else f"{k}='{esc(v)}'" for k, v in sets.items())
                f.write(f"UPDATE res_zip SET {sql_sets} WHERE id={m['id']};\n")
        for r in city_new:
            sector = posta.sector_for(r["state"], r["name"])
            f.write(insert_stmt(r, sector, office_addr.get(posta.norm_key(r["office"]), "")))
        gone_ids.extend(int(m["id"]) for m in city_gone)
        f.write("\n")
    if len(gone_ids) > start:
        f.write(gone_sql(gone_ids[start:]))
        f.write("\n")
    return n_upd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", default="live_rows.jsonl")
    ap.add_argument("--out-sql", default="res_zip_delta.sql")
    ap.add_argument(
        "--out-osm-sql",
        default="res_zip_osm_delta.sql",
        help="strazile oraselor mici din OSM (osm_towns.py), separat fiindca sunt sub ODbL",
    )
    ap.add_argument("--out-report", default="raport.csv")
    args = ap.parse_args()

    ex_rows = existing.load(SQL)
    ex_index = existing.build_index(ex_rows)
    office_addr = {}
    for r in ex_rows:
        if r["office"] and r["address"]:
            office_addr.setdefault(posta.norm_key(r["office"]), r["address"])

    live = load_live(args.live)
    small = [r for r in live if r["src"] == "small"]
    big = [r for r in live if r["src"] in ("code", "refresh", "osm-new", "osm-town")]

    # orase atinse (state_norm, city_norm)
    big_cities = {}
    for r in big:
        big_cities.setdefault((posta.norm_key(r["state"]), posta.city_key(r["city"])), []).append(r)
    # GONE la comune doar in judetele din care s-au citit comunele (nu si cele atinse doar de orase/OSM)
    touched_states = {posta.norm_key(r["state"]) for r in small}

    # Comuna sub_50_mii = UN cod/localitate -> identitatea e (judet, cod), NU numele.
    # Asa prindem redenumirile (calificativ schimbat) ca update, nu ca new+gone.
    ex_loc_by_zip = {}
    for r in ex_rows:
        if not r["street_name"]:  # rand la nivel de localitate
            ex_loc_by_zip.setdefault((posta.norm_key(r["state"]), r["name"]), r)

    new, office_add, rename = [], [], []
    seen_zip = set()
    for r in small:
        zk = (posta.norm_key(r["state"]), r["name"])
        seen_zip.add(zk)
        m = ex_loc_by_zip.get(zk)
        if not m:
            new.append(r)
            continue
        if posta.city_key(m["city"]) != posta.city_key(r["city"]):
            rename.append((m, r))  # acelasi cod, nume schimbat
        elif not m["office"] and r["office"]:
            office_add.append((m, r))

    # GONE comune: randuri-localitate din state-urile atinse, al caror cod NU a fost
    # vazut live (si nu sunt orase re-importate).
    gone = []
    for (st, zipc), m in ex_loc_by_zip.items():
        if st not in touched_states:
            continue
        if (st, posta.city_key(m["city"])) in big_cities:
            continue
        if (st, zipc) not in seen_zip:
            gone.append(m)

    # orase: potrivire pe randurile existente (dupa id, nu dupa textul orasului)
    city_results = {}
    for (st, city), rows in big_cities.items():
        # randurile-oras cu cod '*', unitatile postale si randul-localitate (fara strada,
        # la orasele mici) nu sunt strazi de la posta/OSM -> raman neatinse
        ex_city = [
            m
            for m in ex_index_city(ex_index, st, city)
            if m["name"].isdigit() and m["street_name"] and m["street_type"] not in posta.POSTAL_UNIT_TYPES
        ]
        city_results[(st, city)] = match_city(ex_city, rows)

    # ---- SQL ----
    n_city_upd = 0
    gone_ids = []
    osm_cities = {k for k, rows in big_cities.items() if all(r["src"] == "osm-town" for r in rows)}
    with open(args.out_sql, "w", encoding="utf-8") as f:
        f.write("-- Delta posta-romana.ro (live) + OSM. Idempotent.\n")
        f.write("-- Comune: INSERT/UPDATE. Orase: UPDATE pe loc + INSERT + DELETE doar pt randuri nefolosite.\n")
        f.write("BEGIN;\n")
        f.write("SELECT setval('res_zip_id_seq', (SELECT MAX(id) FROM res_zip));\n\n")

        if new:
            f.write("-- === comune NEW ===\n")
            for r in new:
                f.write(insert_stmt(r, "", office_addr.get(posta.norm_key(r["office"]), "")))
            f.write("\n")
        if rename:
            f.write("-- === comune RENAME (acelasi cod, nume actualizat) ===\n")
            for m, r in rename:
                office_set = f", office='{esc(r['office'])}'" if (not m["office"] and r["office"]) else ""
                # city_id/country_id resetate -> recalculate in sectiunea de relatii
                f.write(
                    f"UPDATE res_zip SET city='{esc(r['city'])}'{office_set}, city_id=NULL, country_id=NULL "
                    f"WHERE id={m['id']};  -- {m['city']} -> {r['city']} ({r['name']})\n"
                )
            f.write("\n")
        if office_add:
            f.write("-- === comune OFFICE_ADD ===\n")
            for m, r in office_add:
                addr = office_addr.get(posta.norm_key(r["office"]), "")
                addr_set = f", address='{esc(addr)}'" if addr and not m["address"] else ""
                f.write(f"UPDATE res_zip SET office='{esc(r['office'])}'{addr_set} WHERE id={m['id']};\n")
            f.write("\n")

        cities = {k: v for k, v in city_results.items() if k not in osm_cities}
        n_city_upd += write_cities(f, cities, big_cities, office_addr, gone_ids)
        f.write(mapping_sql())
        f.write("COMMIT;\n")

    osm_gone_ids = []
    if osm_cities:
        with open(args.out_osm_sql, "w", encoding="utf-8") as f:
            f.write("-- Strazile oraselor mici: nume din OpenStreetMap, cod de la posta-romana.ro. Idempotent.\n")
            f.write(
                "-- Date OSM: (c) OpenStreetMap contributors, licenta ODbL (https://www.openstreetmap.org/copyright).\n"
            )
            f.write("BEGIN;\n")
            f.write("SELECT setval('res_zip_id_seq', (SELECT MAX(id) FROM res_zip));\n\n")
            cities = {k: v for k, v in city_results.items() if k in osm_cities}
            n_city_upd += write_cities(f, cities, big_cities, office_addr, osm_gone_ids)
            f.write(mapping_sql())
            f.write("COMMIT;\n")
    gone_ids += osm_gone_ids

    # ---- raport ----
    with open(args.out_report, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["categorie", "state", "city", "street", "zip_vechi", "zip_nou", "office", "src"])
        for r in new:
            w.writerow(["NEW", r["state"], r["city"], r["street_name"], "", r["name"], r["office"], r["src"]])
        for m, r in rename:
            w.writerow(
                [
                    "RENAME",
                    m["state"],
                    f"{m['city']} -> {r['city']}",
                    r["street_name"],
                    m["name"],
                    r["name"],
                    r["office"],
                    r["src"],
                ]
            )
        for m, r in office_add:
            w.writerow(
                ["OFFICE_ADD", m["state"], m["city"], m["street_name"], m["name"], m["name"], r["office"], r["src"]]
            )
        for (st, city), (matched, city_new, city_gone) in city_results.items():
            rows = big_cities[(st, city)]
            old_n = len(matched) + len(city_gone)
            w.writerow(
                [
                    "CITY",
                    rows[0]["state"],
                    rows[0]["city"],
                    f"{old_n} -> {len(rows)} randuri ({len(matched)} potrivite, "
                    f"{len(city_new)} noi, {len(city_gone)} disparute)",
                    "",
                    "",
                    "",
                    "+".join(sorted({r["src"] for r in rows})),
                ]
            )
            for r in city_new:
                w.writerow(["CITY_NEW", r["state"], r["city"], r["street_name"], "", r["name"], r["office"], r["src"]])
            for m in city_gone:
                w.writerow(["CITY_GONE", m["state"], m["city"], m["street_name"], m["name"], "", m["office"], ""])
        for m in gone:
            w.writerow(["GONE", m["state"], m["city"], m["street_name"], m["name"], "", "", ""])

    print(f"comune: NEW={len(new)} RENAME={len(rename)} OFFICE_ADD={len(office_add)}")
    print(
        f"orase: {len(big_cities)} orase, {len(big)} randuri live, {n_city_upd} UPDATE, "
        f"{sum(len(v[1]) for v in city_results.values())} NEW, {len(gone_ids)} GONE"
    )
    print(f"GONE comune (in judetele atinse, exclus orase): {len(gone)}")
    print(f"-> {args.out_sql}  +  {args.out_report}" + (f"  +  {args.out_osm_sql}" if osm_cities else ""))


def ex_index_city(ex_index, st, city):
    out = []
    for k, lst in ex_index.items():
        if k[0] == st and k[1] == city:
            out.extend(lst)
    return out


if __name__ == "__main__":
    main()
