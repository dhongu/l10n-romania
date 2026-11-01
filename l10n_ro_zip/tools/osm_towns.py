"""
Strazi pentru orasele mici (sub_50_mii) din OpenStreetMap, cu codul de la posta.

La posta, un oras sub 50k are UN cod pe localitate si nu-si listeaza strazile. Luam
numele strazilor din OSM (date ODbL) si le dam codul localitatii de la posta:
  - o interogare Overpass pe judet: localitatile (place=city/town/village/hamlet) si
    strazile cu nume (cu centrul geometric);
  - fiecare strada merge la localitatea cea mai apropiata; pastram doar strazile
    al caror cel mai apropiat punct e un oras (city/town) — satele componente ale
    orasului au cod propriu la posta;
  - codul vine din randurile 'small' din live_rows.jsonl (crawl.py) sau, daca
    lipsesc, din posta (cautare cu adresa goala).

Iesire: randuri src='osm-town' adaugate in live_rows.jsonl; build_delta.py le scrie
intr-un SQL separat (res_zip_osm_delta.sql), fiindca datele OSM sunt sub ODbL.

Uz (din acelasi workdir ca crawl.py):
  python osm_towns.py --judete Vaslui Galați
  python osm_towns.py                   # toate judetele (~42 interogari Overpass)
"""
# pylint: disable=print-used

import argparse
import json
import math
import os
import sys
import time
import urllib.parse
import urllib.request

import osm
import posta

CACHE = "osm_counties.json"  # {judet: {"places": [...], "ways": [...]}}
OUT = "live_rows.jsonl"
DONE = "done_osm_towns.txt"
PAUSE = 6.0  # intre interogarile Overpass
DELAY = 0.45  # intre cererile catre posta, ca in crawl.py
MAX_KM = 5.0  # o strada mai departe de orice localitate e ignorata

JUDET_ISO = {
    "Alba": "RO-AB",
    "Arad": "RO-AR",
    "Argeș": "RO-AG",
    "Bacău": "RO-BC",
    "Bihor": "RO-BH",
    "Bistrița-Năsăud": "RO-BN",
    "Botoșani": "RO-BT",
    "Brăila": "RO-BR",
    "Brașov": "RO-BV",
    "București": "RO-B",
    "Buzău": "RO-BZ",
    "Călărași": "RO-CL",
    "Caraș-Severin": "RO-CS",
    "Cluj": "RO-CJ",
    "Constanța": "RO-CT",
    "Covasna": "RO-CV",
    "Dâmbovița": "RO-DB",
    "Dolj": "RO-DJ",
    "Galați": "RO-GL",
    "Giurgiu": "RO-GR",
    "Gorj": "RO-GJ",
    "Harghita": "RO-HR",
    "Hunedoara": "RO-HD",
    "Ialomița": "RO-IL",
    "Iași": "RO-IS",
    "Ilfov": "RO-IF",
    "Maramureș": "RO-MM",
    "Mehedinți": "RO-MH",
    "Mureș": "RO-MS",
    "Neamț": "RO-NT",
    "Olt": "RO-OT",
    "Prahova": "RO-PH",
    "Sălaj": "RO-SJ",
    "Satu Mare": "RO-SM",
    "Sibiu": "RO-SB",
    "Suceava": "RO-SV",
    "Teleorman": "RO-TR",
    "Timiș": "RO-TM",
    "Tulcea": "RO-TL",
    "Vâlcea": "RO-VL",
    "Vaslui": "RO-VS",
    "Vrancea": "RO-VN",
}

# drumuri care nu sunt strazi de adresa
SKIP_HIGHWAY = {
    "motorway",
    "motorway_link",
    "trunk_link",
    "service",
    "track",
    "path",
    "footway",
    "cycleway",
    "steps",
    "bridleway",
    "construction",
    "proposed",
    "platform",
    "corridor",
}
TOWN_PLACES = {"city", "town"}


def fetch_county(iso):
    """Localitatile si strazile cu nume dintr-un judet (Overpass)."""
    q = f"""
    [out:json][timeout:300];
    area["ISO3166-2"="{iso}"]->.c;
    node(area.c)["place"~"^(city|town|village|hamlet)$"]["name"];
    out;
    way(area.c)["highway"]["name"];
    out tags center;
    """
    data = urllib.parse.urlencode({"data": q}).encode()
    last = {}
    for attempt in range(5):
        try:
            req = urllib.request.Request(
                osm.OVERPASS, data=data, headers={"User-Agent": osm.UA, "Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=360) as r:
                j = json.loads(r.read().decode("utf-8"))
            els = j.get("elements", [])
            places = [
                {"name": e["tags"]["name"], "place": e["tags"]["place"], "lat": e["lat"], "lon": e["lon"]}
                for e in els
                if e["type"] == "node"
            ]
            ways = [
                {"name": e["tags"]["name"], "highway": e["tags"]["highway"], **e["center"]}
                for e in els
                if e["type"] == "way" and "center" in e
            ]
            if places and ways:
                return {"places": places, "ways": ways}
            last = {"remark": j.get("remark", ""), "n_elements": len(els)}
        except Exception as e:  # noqa: BLE001
            last = {"error": str(e)}
        time.sleep(15 * (attempt + 1))
    raise RuntimeError(f"Overpass fara rezultat pentru {iso}: {last}")


def km(a, b):
    """Distanta aproximativa (echirectangulara) — suficienta la scara unui judet."""
    x = math.radians(b["lon"] - a["lon"]) * math.cos(math.radians((a["lat"] + b["lat"]) / 2))
    y = math.radians(b["lat"] - a["lat"])
    return 6371 * math.hypot(x, y)


def is_street_name(name):
    """Doar nume care incep cu un tip de strada (Strada, Aleea...): scoate 'Parcare', 'DN24'."""
    st, rest = posta.split_street(name)
    return bool(st) and bool(rest)


def town_streets(county, big_cities):
    """{oras_osm: set(nume strada OSM)} pentru orasele mici din judet."""
    places = county["places"]
    out = {}
    for w in county["ways"]:
        if w["highway"] in SKIP_HIGHWAY or not is_street_name(w["name"]):
            continue
        best, dist = None, None
        for p in places:
            d = km(w, p)
            if dist is None or d < dist:
                best, dist = p, d
        if best is None or dist > MAX_KM or best["place"] not in TOWN_PLACES:
            continue
        if posta.city_key(best["name"]) in big_cities:
            continue  # orasele mari au strazile lor, de la posta
        out.setdefault(best["name"], set()).add(w["name"])
    return out


def load_codes(path):
    """(judet_key, oras_key) -> rand 'small' (cod + oficiu) din live_rows.jsonl."""
    codes = {}
    if not os.path.exists(path):
        return codes
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["src"] == "small" and not r["street_name"]:
                codes.setdefault((posta.norm_key(r["state"]), posta.city_key(r["city"])), r)
    return codes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judete", nargs="*", help="limiteaza la anumite judete (eticheta)")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
    done = set(open(DONE, encoding="utf-8").read().split("\n")) if os.path.exists(DONE) else set()
    codes = load_codes(args.out)
    items = [(k, v) for k, v in posta.JUDETE.items() if k != "București"]
    if args.judete:
        items = [(k, v) for k, v in items if k in args.judete]

    with open(args.out, "a", encoding="utf-8") as fout:
        for eticheta, jud_val in items:
            if eticheta in done:
                print(f"== {eticheta}: deja facut, skip")
                continue
            print(f"== {eticheta}")
            if eticheta not in cache:
                cache[eticheta] = fetch_county(JUDET_ISO[eticheta])
                json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
                time.sleep(PAUSE)
            locs = posta.get_localities(jud_val)
            time.sleep(DELAY)
            big = {posta.city_key(v) for v, _l, k in locs if k != "sub_50_mii"}
            small = {posta.city_key(v): v for v, _l, k in locs if k == "sub_50_mii"}
            state_key = posta.norm_key(posta.STATE_NAME[eticheta])
            n = 0
            for town, streets in sorted(town_streets(cache[eticheta], big).items()):
                tk = posta.city_key(town)
                if tk not in small:
                    print(f"    ! {town}: nu e in lista postei pentru {eticheta}", file=sys.stderr)
                    continue
                base = codes.get((state_key, tk))
                if base is None:
                    found = posta.search_address(jud_val, small[tk], "")
                    time.sleep(DELAY)
                    if not found:
                        print(f"    ! {town}: fara cod la posta", file=sys.stderr)
                        continue
                    f0 = found[0]
                    base = {
                        "state": posta.strip_diacritics(f0["state"]),
                        "city": posta.strip_diacritics(f0["city"]),
                        "name": f0["zip"],
                        "office": posta.strip_diacritics(f0["office"]),
                    }
                for name in sorted(streets):
                    st, sn = posta.split_street(name)
                    row = {
                        "state": base["state"],
                        "city": base["city"],
                        "street_type": st,
                        "street_name": sn,
                        "name": base["name"],
                        "office": base["office"],
                        "src": "osm-town",
                    }
                    fout.write(json.dumps(row, ensure_ascii=False) + "\n")
                    n += 1
                print(f"    {town} ({base['name']}): {len(streets)} strazi")
            fout.flush()
            print(f"   {n} randuri osm-town")
            with open(DONE, "a", encoding="utf-8") as fd:
                fd.write(eticheta + "\n")
    print("gata.")


if __name__ == "__main__":
    main()
