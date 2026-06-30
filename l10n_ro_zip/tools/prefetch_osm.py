"""
Pre-fetch lista de strazi OSM pentru cele ~50 orase >50k -> osm_cache.json.

Decupleaza Overpass (rate-limited, fragil) de crawl-ul posta. Ruleaza-l INAINTE de
crawl.py; pacing generos (6s intre orase) ca sa nu fim throttled. Resumabil: orasele
deja in cache sunt sarite.

Uz: python prefetch_osm.py
"""
# pylint: disable=print-used

import json
import os
import sys
import time

import osm

CACHE = "osm_cache.json"
PAUSE = 6.0


def main():
    cache = {}
    if os.path.exists(CACHE):
        cache = json.load(open(CACHE, encoding="utf-8"))
    targets = sorted(set(osm.BIG_CITY_OSM.values()))
    print(f"{len(targets)} orase de pre-fetch; {len(cache)} deja in cache")
    for name in targets:
        if name in cache:
            continue
        try:
            streets = osm.fetch_streets(name)
            cache[name] = streets
            print(f"  {name}: {len(streets)} strazi")
        except Exception as e:  # noqa: BLE001
            print(f"  ! {name}: ESUAT ({e})", file=sys.stderr)
        json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        time.sleep(PAUSE)
    print(f"gata -> {CACHE} ({len(cache)} orase)")


if __name__ == "__main__":
    main()
