"""
Lista de strazi per oras din OpenStreetMap (Overpass API).

Pentru orasele >50k (street-level), site-ul Posta Romana NU permite enumerarea
strazilor. Luam numele de strazi din OSM (actuale), apoi le rezolvam exact pe
endpoint-ul oficial ca sa obtinem codul postal oficial.
"""

import json
import time
import urllib.parse
import urllib.request

OVERPASS = "https://overpass-api.de/api/interpreter"

# posta returneaza numele oraselor inconsistent (ASCII / diacritice gresite); OSM
# cere numele canonic cu diacritice. Cheie = norm_key(valoarea posta) -> nume OSM.
BIG_CITY_OSM = {
    "alba iulia": "Alba Iulia",
    "arad": "Arad",
    "pitesti": "Pitești",
    "bacau": "Bacău",
    "onesti": "Onești",
    "oradea": "Oradea",
    "bistrita": "Bistrița",
    "botosani": "Botoșani",
    "braila": "Brăila",
    "brasov": "Brașov",
    "bucuresti": "București",
    "buzau": "Buzău",
    "calarasi": "Călărași",
    "resita": "Reșița",
    "cluj napoca": "Cluj-Napoca",
    "turda": "Turda",
    "constanta": "Constanța",
    "sfantu gheorghe": "Sfântu Gheorghe",
    "targoviste": "Târgoviște",
    "craiova": "Craiova",
    "galati": "Galați",
    "giurgiu": "Giurgiu",
    "targu jiu": "Târgu Jiu",
    "miercurea ciuc": "Miercurea Ciuc",
    "deva": "Deva",
    "hunedoara": "Hunedoara",
    "petrosani": "Petroșani",
    "slobozia": "Slobozia",
    "iasi": "Iași",
    "baia mare": "Baia Mare",
    "drobeta turnu severin": "Drobeta-Turnu Severin",
    "targu mures": "Târgu Mureș",
    "piatra neamt": "Piatra Neamț",
    "roman": "Roman",
    "slatina": "Slatina",
    "ploiesti": "Ploiești",
    "zalau": "Zalău",
    "satu mare": "Satu Mare",
    "medias": "Mediaș",
    "sibiu": "Sibiu",
    "suceava": "Suceava",
    "alexandria": "Alexandria",
    "timisoara": "Timișoara",
    "tulcea": "Tulcea",
    "ramnicu valcea": "Râmnicu Vâlcea",
    "barlad": "Bârlad",
    "vaslui": "Vaslui",
    "focsani": "Focșani",
}
# UA descriptiv obligatoriu — Overpass (mod_security) blocheaza UA-urile tip "Mozilla" cu 406.
UA = "l10n-ro-zip-refresh/1.0 (dorin@terrabit.ro)"

# tip OSM ("Strada Pacurari") -> doar numele canonic asteptat de k_adresa ("Pacurari").
# Posta cere numele FARA tip si fara diacritice obligatorii; stripam tipul + diacriticele in resolver.
OSM_TYPE_PREFIXES = [
    "Strada",
    "Bulevardul",
    "Bulevard",
    "Soseaua",
    "Șoseaua",
    "Aleea",
    "Calea",
    "Intrarea",
    "Piata",
    "Piața",
    "Drumul",
    "Splaiul",
    "Fundatura",
    "Fundătura",
    "Prelungirea",
    "Stradela",
    "Strada ",
    "Str.",
    "B-dul",
    "Bd.",
    "Cal.",
    "Al.",
]


def fetch_streets(city_name):
    """Returneaza set de nume de strazi (cu tip, asa cum sunt in OSM) pentru un oras."""
    # cautam relatia/aria orasului dupa nume, apoi highway-urile cu name din interiorul ei
    q = f"""
    [out:json][timeout:120];
    area["name"="{city_name}"]["boundary"="administrative"]->.a;
    way(area.a)["highway"]["name"];
    out tags;
    """
    data = urllib.parse.urlencode({"data": q}).encode()
    # retry inclusiv pe rezultat GOL — Overpass throttled raspunde 200 cu 0 elemente
    # sau cu un "remark: runtime error: ... rate_limited". Tratam ambele ca esec temporar.
    last = {}
    for attempt in range(5):
        try:
            req = urllib.request.Request(
                OVERPASS,
                data=data,
                headers={"User-Agent": UA, "Accept": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=180) as r:
                j = json.loads(r.read().decode("utf-8"))
            els = j.get("elements", [])
            remark = j.get("remark", "")
            if els:
                names = {e["tags"]["name"] for e in els if e.get("tags", {}).get("name")}
                if names:
                    return sorted(names)
            last = {"remark": remark, "n_elements": len(els)}
        except Exception as e:  # noqa: BLE001
            last = {"error": str(e)}
        time.sleep(8 * (attempt + 1))  # backoff generos pentru rate-limit Overpass
    # dupa toate incercarile, ridica pentru a fi vizibil (nu inghiti tacit)
    raise RuntimeError(f"Overpass fara rezultat dupa 5 incercari: {last}")


def street_name_only(osm_name):
    """Scoate prefixul de tip ('Strada Pacurari' -> 'Pacurari') pentru query exact."""
    s = osm_name.strip()
    for pref in sorted(OSM_TYPE_PREFIXES, key=len, reverse=True):
        if s.startswith(pref + " "):
            return s[len(pref) :].strip()
        if s.startswith(pref + "."):
            return s[len(pref) + 1 :].strip()
    return s
