"""
Diff live_rows.jsonl vs res_zip.sql -> res_zip_delta.sql + raport.csv.

Doua regimuri, pe sursa randului live:
  - 'small' (comune <50k): diff curat 1:1
        NEW        -> INSERT
        ZIP_CHG    -> UPDATE name
        OFFICE_ADD -> UPDATE office (existent gol, live are)
  - 'refresh'/'osm-new' (orase >50k): REPLACE per oras
        re-segmentarea face diff-ul pe rand inutilizabil -> DELETE randurile
        orasului + INSERT setul live. Absoarbe si strazile noi din OSM.

GONE e raportat DOAR pentru judetele/orasele atinse de acest crawl (altfel,
la rulare partiala, ar lista tot restul tarii).
Nimic nu se sterge in afara oraselor explicit re-importate.
"""
# pylint: disable=print-used

import argparse
import csv
import json
import os

import existing
import posta

SQL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "res_zip.sql")


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
            k = (posta.norm_key(r["state"]), posta.norm_key(r["city"]), posta.norm_key(r["street_name"]), r["name"])
            if k not in seen:
                seen.add(k)
                rows.append(r)
    return rows


def insert_stmt(next_id, r):
    return (
        "INSERT INTO res_zip (id, state, city, street_type, street_name, name, sector, office, address)\n"
        f"VALUES ({next_id}, '{esc(r['state'])}', '{esc(r['city'])}', '{esc(r['street_type'])}', "
        f"'{esc(r['street_name'])}', '{esc(r['name'])}', '', '{esc(r['office'])}', '');\n"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", default="live_rows.jsonl")
    ap.add_argument("--out-sql", default="res_zip_delta.sql")
    ap.add_argument("--out-report", default="raport.csv")
    args = ap.parse_args()

    ex_rows = existing.load(SQL)
    ex_index = existing.build_index(ex_rows)
    next_id = existing.max_id(ex_rows) + 1

    live = load_live(args.live)
    small = [r for r in live if r["src"] == "small"]
    big = [r for r in live if r["src"] in ("refresh", "osm-new")]

    # orase atinse (state_norm, city_norm)
    big_cities = {}
    for r in big:
        big_cities.setdefault((posta.norm_key(r["state"]), posta.norm_key(r["city"])), []).append(r)
    touched_states = {posta.norm_key(r["state"]) for r in live}

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
        if posta.norm_key(m["city"]) != posta.norm_key(r["city"]):
            rename.append((m, r))  # acelasi cod, nume schimbat
        elif not m["office"] and r["office"]:
            office_add.append((m, r))

    # GONE comune: randuri-localitate din state-urile atinse, al caror cod NU a fost
    # vazut live (si nu sunt orase re-importate).
    gone = []
    for (st, zipc), m in ex_loc_by_zip.items():
        if st not in touched_states:
            continue
        if (st, posta.norm_key(m["city"])) in big_cities:
            continue
        if (st, zipc) not in seen_zip:
            gone.append(m)

    # ---- SQL ----
    with open(args.out_sql, "w", encoding="utf-8") as f:
        f.write("-- Delta posta-romana.ro (live) + OSM.\n")
        f.write("-- Comune: INSERT/UPDATE. Orase: REPLACE per oras (DELETE+INSERT).\n")
        f.write("BEGIN;\n\n")

        if new:
            f.write("-- === comune NEW ===\n")
            for r in new:
                f.write(insert_stmt(next_id, r))
                next_id += 1
            f.write("\n")
        if rename:
            f.write("-- === comune RENAME (acelasi cod, nume actualizat) ===\n")
            for m, r in rename:
                office_set = f", office='{esc(r['office'])}'" if (not m["office"] and r["office"]) else ""
                f.write(
                    f"UPDATE res_zip SET city='{esc(r['city'])}'{office_set} WHERE id={m['id']};"
                    f"  -- {esc(m['city'])} -> {esc(r['city'])} ({r['name']})\n"
                )
            f.write("\n")
        if office_add:
            f.write("-- === comune OFFICE_ADD ===\n")
            for m, r in office_add:
                f.write(f"UPDATE res_zip SET office='{esc(r['office'])}' WHERE id={m['id']};\n")
            f.write("\n")

        if big_cities:
            f.write("-- === orase REPLACE per oras ===\n")
            for (_st, _city), rows in big_cities.items():
                state_v = rows[0]["state"]
                city_v = rows[0]["city"]
                f.write(f"DELETE FROM res_zip WHERE state='{esc(state_v)}' AND city='{esc(city_v)}';\n")
                for r in rows:
                    f.write(insert_stmt(next_id, r))
                    next_id += 1
                f.write("\n")

        f.write("SELECT setval('res_zip_id_seq', (SELECT MAX(id) FROM res_zip));\n")
        f.write("COMMIT;\n")

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
        for (st, city), rows in big_cities.items():
            old_n = len(ex_index_city(ex_index, st, city))
            w.writerow(
                [
                    "CITY_REPLACE",
                    rows[0]["state"],
                    rows[0]["city"],
                    f"{old_n} -> {len(rows)} randuri",
                    "",
                    "",
                    "",
                    "refresh+osm",
                ]
            )
        for m in gone:
            w.writerow(["GONE", m["state"], m["city"], m["street_name"], m["name"], "", "", ""])

    print(f"comune: NEW={len(new)} RENAME={len(rename)} OFFICE_ADD={len(office_add)}")
    print(f"orase REPLACE: {len(big_cities)} orase, {len(big)} randuri live")
    print(f"GONE (in judetele atinse, exclus orase): {len(gone)}")
    print(f"-> {args.out_sql}  +  {args.out_report}")


def ex_index_city(ex_index, st, city):
    out = []
    for k, lst in ex_index.items():
        if k[0] == st and k[1] == city:
            out.extend(lst)
    return out


if __name__ == "__main__":
    main()
