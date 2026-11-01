"""
Orchestrator crawl live -> live_rows.jsonl (resumable).

Per judet:
  - localitate sub_50_mii  : un search_address(adresa="") -> rand(uri) la nivel localitate.
  - localitate peste_50_mii: refresh strazi EXISTENTE (din res_zip, hit ~100%)
                             + descoperire strazi noi din OSM ce NU-s deja in set.
  - cu --by-code, pentru orasele peste_50_mii: cautare inversa pe TOATE codurile din
    blocurile folosite de oras (prefix de 4 cifre din res_zip -> 100 de coduri/bloc);
    fiecare cod intoarce toate strazile lui. Strazile existente nevazute in blocuri se
    cauta apoi exact, ca plasa de siguranta.

Fiecare rand live e scris ca JSON pe o linie, in schema res_zip:
  {state, city, street_type, street_name, name(zip), office, src}
Checkpoint: judetele terminate sunt notate in done.txt -> re-rularea le sare.

Uz:
  python crawl.py                      # tot (lung, ~ore)
  python crawl.py --judete Covasna     # un judet (validare)
  python crawl.py --no-osm             # fara descoperire OSM (doar refresh + comune)
  python crawl.py --by-code            # nomenclator complet pe orase, prin blocuri de coduri
  python crawl.py --by-code --prefix-len 3   # blocuri de 1000 de coduri (mai lent, mai larg)
  python crawl.py --by-code --no-osm --orase Iasi   # doar orasul (fara comunele judetului)
"""
# pylint: disable=print-used

import argparse
import json
import os
import sys
import time

import existing
import osm
import posta

OSM_CACHE = "osm_cache.json"  # {nume_osm: [strazi]} produs de prefetch_osm.py


def load_osm_cache():
    if os.path.exists(OSM_CACHE):
        return json.load(open(OSM_CACHE, encoding="utf-8"))
    return {}


SQL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "res_zip.sql")
DELAY = 0.45
OUT = "live_rows.jsonl"
DONE = "done.txt"
DONE_BLOCKS = "done_blocks.txt"  # --by-code: "<judet>:<prefix>" pentru blocurile terminate


def to_schema(r, src):
    st, sn = posta.split_street(r["street"])
    return {
        "state": posta.strip_diacritics(r["state"]),
        "city": posta.strip_diacritics(r["city"]),
        "street_type": st,
        "street_name": sn,
        "name": r["zip"],
        "office": posta.strip_diacritics(r["office"]),
        "src": src,
    }


def code_blocks(ex_rows, state_ascii, cities, prefix_len):
    """Prefixele de cod folosite de strazile oraselor mari din judet (fara unitati postale)."""
    blocks = set()
    for r in ex_rows:
        if (
            r["street_name"]
            and r["name"].isdigit()
            and r["street_type"] not in posta.POSTAL_UNIT_TYPES
            and posta.norm_key(r["state"]) == posta.norm_key(state_ascii)
            and posta.city_key(r["city"]) in cities
        ):
            blocks.add(r["name"][:prefix_len])
    return sorted(blocks)


def crawl_codes(jud_eticheta, ex_rows, cities, prefix_len, fout):
    """Cautare inversa pe toate codurile din blocurile oraselor mari ale judetului.

    Returneaza (n_randuri, {city_key: set(norm_key strada de baza)} vazute).
    """
    state_ascii = posta.STATE_NAME[jud_eticheta]
    done_blocks = set()
    if os.path.exists(DONE_BLOCKS):
        done_blocks = set(open(DONE_BLOCKS, encoding="utf-8").read().split("\n"))
    n, other = 0, 0
    seen_rows = set()
    seen_bases = {c: set() for c in cities}
    blocks = code_blocks(ex_rows, state_ascii, cities, prefix_len)
    print(f"  {len(blocks)} blocuri de coduri ({10 ** (6 - prefix_len)} coduri/bloc)")
    for prefix in blocks:
        tag = f"{jud_eticheta}:{prefix}"
        if tag in done_blocks:
            continue
        for i in range(10 ** (6 - prefix_len)):
            code = f"{prefix}{i:0{6 - prefix_len}d}"
            # codul unui oficiu intoarce toate strazile oficiului -> acelasi rand poate reveni
            for r in posta.search_code(code):
                if not r["street"]:
                    continue  # rand-localitate: il ia cautarea pe localitati
                ck = posta.city_key(r["city"])
                if ck not in cities:
                    other += 1  # strada din alt oras/judet (ex. oras mic cu coduri pe strazi)
                    continue
                row = to_schema(r, "code")
                rk = (ck, posta.norm_key(row["street_name"]), row["name"])
                if rk in seen_rows:
                    continue
                seen_rows.add(rk)
                seen_bases[ck].add(posta.norm_key(posta.base_street(row["street_name"])))
                fout.write(json.dumps(row, ensure_ascii=False) + "\n")
                n += 1
            time.sleep(DELAY)
        fout.flush()
        with open(DONE_BLOCKS, "a", encoding="utf-8") as fd:
            fd.write(tag + "\n")
    if other:
        print(f"    {other} randuri de strada din alte localitati, ignorate", file=sys.stderr)
    return n, seen_bases


def crawl_judet(
    jud_eticheta, jud_val, ex_index, use_osm, fout, osm_cache, ex_rows=None, prefix_len=0, only_cities=None
):
    n = 0
    locs = posta.get_localities(jud_val)
    time.sleep(DELAY)
    if only_cities:
        # --orase: doar orasele cerute; comunele judetului nu se citesc
        locs = [x for x in locs if x[2] != "sub_50_mii" and posta.city_key(x[0]) in only_cities]
    print(f"  {len(locs)} localitati")
    code_seen = None
    if prefix_len:
        cities = {posta.city_key(loc) for loc, _label, klass in locs if klass != "sub_50_mii"}
        n_code, code_seen = crawl_codes(jud_eticheta, ex_rows, cities, prefix_len, fout)
        n += n_code
    for loc, _label, klass in locs:
        if klass == "sub_50_mii":
            for r in posta.search_address(jud_val, loc, ""):
                fout.write(json.dumps(to_schema(r, "small"), ensure_ascii=False) + "\n")
                n += 1
            time.sleep(DELAY)
        else:  # peste_50_mii — oras street-level
            state_ascii = posta.STATE_NAME[jud_eticheta]
            city_ascii = posta.strip_diacritics(loc)
            # 1) refresh strazi existente (din res_zip pentru acest oras)
            existing_bases = set()
            for k, lst in ex_index.items():
                if k[0] == posta.norm_key(state_ascii) and k[1] == posta.city_key(city_ascii):
                    if lst[0]["street_type"] in posta.POSTAL_UNIT_TYPES:
                        continue
                    existing_bases.add(posta.base_street(lst[0]["street_name"]))
            existing_bases.discard("")
            seen_bases = set()
            if code_seen is not None:
                # --by-code: cautam exact doar strazile existente pe care blocurile nu le-au adus
                got = code_seen.get(posta.city_key(loc), set())
                existing_bases = {b for b in existing_bases if posta.norm_key(b) not in got}
                seen_bases |= got
            for b in sorted(existing_bases):
                for r in posta.search_address(jud_val, loc, b):
                    fout.write(json.dumps(to_schema(r, "refresh"), ensure_ascii=False) + "\n")
                    n += 1
                seen_bases.add(posta.norm_key(b))
                time.sleep(DELAY)
            # 2) descoperire OSM: strazi care nu-s deja in set
            osm_name = osm.BIG_CITY_OSM.get(posta.norm_key(loc))
            osm_streets = []
            if use_osm and osm_name:
                if osm_name in osm_cache:  # preferam cache-ul (prefetch_osm.py)
                    osm_streets = osm_cache[osm_name]
                else:
                    try:
                        osm_streets = osm.fetch_streets(osm_name)
                    except Exception as e:  # noqa: BLE001
                        print(f"    ! OSM esuat pentru {osm_name}: {e}", file=sys.stderr)
            elif use_osm and not osm_name:
                print(f"    ! fara mapare OSM pentru orasul {loc!r} — sar descoperirea", file=sys.stderr)
            print(
                f"    oras {loc}: {len(existing_bases)} baze existente, {len(osm_streets)} strazi OSM", file=sys.stderr
            )
            for nm in osm_streets:
                only = osm.street_name_only(nm)
                if posta.norm_key(only) in seen_bases or not only:
                    continue
                for r in posta.search_address(jud_val, loc, only):
                    fout.write(json.dumps(to_schema(r, "osm-new"), ensure_ascii=False) + "\n")
                    n += 1
                time.sleep(DELAY)
    fout.flush()
    return n


def _osm_name(jud_eticheta, loc):
    """Nume oras pentru OSM (cu diacritice, asa cum e in OSM)."""
    # eticheta posta e deja aproape OK; folosim direct loc (are diacritice in dropdown)
    return loc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judete", nargs="*", help="limiteaza la anumite judete (eticheta)")
    ap.add_argument("--no-osm", action="store_true")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--by-code", action="store_true", help="orase: cautare inversa pe blocurile de coduri")
    ap.add_argument("--prefix-len", type=int, default=4, choices=(3, 4), help="lungimea prefixului de bloc")
    ap.add_argument("--orase", nargs="*", help="doar aceste orase mari (judetul se deduce din res_zip.sql)")
    args = ap.parse_args()

    ex_rows = existing.load(SQL)
    ex_index = existing.build_index(ex_rows)
    print(f"existent: {len(ex_rows)} randuri, {len(ex_index)} chei")

    done = set()
    if os.path.exists(DONE):
        done = set(open(DONE, encoding="utf-8").read().split("\n"))

    items = list(posta.JUDETE.items())
    if args.judete:
        items = [(k, v) for k, v in items if k in args.judete]
    only_cities = None
    if args.orase:
        only_cities = {posta.city_key(c) for c in args.orase}
        states = {posta.norm_key(r["state"]) for r in ex_rows if posta.city_key(r["city"]) in only_cities}
        items = [(k, v) for k, v in items if posta.norm_key(posta.STATE_NAME[k]) in states]
        if not items:
            sys.exit(f"niciun judet gasit pentru {args.orase}")

    osm_cache = load_osm_cache()
    print(f"osm cache: {len(osm_cache)} orase")

    mode = "a" if os.path.exists(args.out) else "w"
    with open(args.out, mode, encoding="utf-8") as fout:
        for eticheta, val in items:
            if eticheta in done and not only_cities:
                print(f"== {eticheta}: deja facut, skip")
                continue
            print(f"== {eticheta}")
            n = crawl_judet(
                eticheta,
                val,
                ex_index,
                not args.no_osm,
                fout,
                osm_cache,
                ex_rows,
                args.prefix_len if args.by_code else 0,
                only_cities,
            )
            print(f"   {n} randuri live")
            if not only_cities:  # judetul e complet doar fara --orase
                with open(DONE, "a", encoding="utf-8") as fd:
                    fd.write(eticheta + "\n")
    print("gata.")


if __name__ == "__main__":
    main()
