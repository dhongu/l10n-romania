"""
Orchestrator crawl live -> live_rows.jsonl (resumable).

Per judet:
  - localitate sub_50_mii  : un search_address(adresa="") -> rand(uri) la nivel localitate.
  - localitate peste_50_mii: refresh strazi EXISTENTE (din res_zip, hit ~100%)
                             + descoperire strazi noi din OSM ce NU-s deja in set.

Fiecare rand live e scris ca JSON pe o linie, in schema res_zip:
  {state, city, street_type, street_name, name(zip), office, src}
Checkpoint: judetele terminate sunt notate in done.txt -> re-rularea le sare.

Uz:
  python crawl.py                      # tot (lung, ~ore)
  python crawl.py --judete Covasna     # un judet (validare)
  python crawl.py --no-osm             # fara descoperire OSM (doar refresh + comune)
"""
# pylint: disable=print-used

import argparse
import json
import os
import re
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


def base_street(street_name):
    """Numele de baza pt query exact (fara sufix 'bl.'/'nr.')."""
    return re.split(r"\s+(?:bl\.|nr\.)", street_name)[0].strip()


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


def crawl_judet(jud_eticheta, jud_val, ex_index, use_osm, fout, osm_cache):
    n = 0
    locs = posta.get_localities(jud_val)
    time.sleep(DELAY)
    print(f"  {len(locs)} localitati")
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
                if k[0] == posta.norm_key(state_ascii) and k[1] == posta.norm_key(city_ascii):
                    existing_bases.add(base_street(lst[0]["street_name"]))
            existing_bases.discard("")
            seen_bases = set()
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

    osm_cache = load_osm_cache()
    print(f"osm cache: {len(osm_cache)} orase")

    mode = "a" if os.path.exists(args.out) else "w"
    with open(args.out, mode, encoding="utf-8") as fout:
        for eticheta, val in items:
            if eticheta in done:
                print(f"== {eticheta}: deja facut, skip")
                continue
            print(f"== {eticheta}")
            n = crawl_judet(eticheta, val, ex_index, not args.no_osm, fout, osm_cache)
            print(f"   {n} randuri live")
            with open(DONE, "a", encoding="utf-8") as fd:
                fd.write(eticheta + "\n")
    print("gata.")


if __name__ == "__main__":
    main()
