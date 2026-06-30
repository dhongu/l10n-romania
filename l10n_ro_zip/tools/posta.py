"""
Client + parser + normalizare pentru endpoint-urile publice posta-romana.ro.

Regimuri (confirmat live):
  - localitate clasa `sub_50_mii`  -> UN cod pe localitate (adresa goala).
  - localitate clasa `peste_50_mii` -> street-level; k_adresa cere nume EXACT de strada.

Normalizarea aliniaza datele live la "house style"-ul din res_zip.sql:
  - street_type live (forma articulata) -> vocabular scurt existent (Sosea/Alee/...).
  - cheie de diff insensibila la diacritice.
"""

import html
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request

BASE = "https://www.posta-romana.ro/cnpr-app/modules/cauta-cod-postal/ajax"
UA = "Mozilla/5.0 (compatible; l10n-ro-zip-refresh/1.0)"

# Cele 42 de valori k_judet (eticheta -> value trimisa). value != eticheta doar la cateva.
JUDETE = {
    "Alba": "Alba",
    "Arad": "Arad",
    "Argeș": "Argeș",
    "Bacău": "Bacău",
    "Bihor": "Bihor",
    "Bistrița-Năsăud": "Bistrița-Năsăud",
    "Botoșani": "Botoșani",
    "Brăila": "Brăila",
    "Brașov": "Brașov",
    "București": "Bucuresti",
    "Buzău": "Buzău",
    "Călărași": "Călărași",
    "Caraș-Severin": "Caraș-Severin",
    "Cluj": "Cluj",
    "Constanța": "Constanța",
    "Covasna": "Covasna",
    "Dâmbovița": "Dambovița",
    "Dolj": "Dolj",
    "Galați": "Galați",
    "Giurgiu": "Giurgiu",
    "Gorj": "Gorj",
    "Harghita": "Harghita",
    "Hunedoara": "Hunedoara",
    "Ialomița": "Ialomița",
    "Iași": "Iași",
    "Ilfov": "Ilfov",
    "Maramureș": "Maramureș",
    "Mehedinți": "Mehedinți",
    "Mureș": "Mureș",
    "Neamț": "Neamț",
    "Olt": "Olt",
    "Prahova": "Prahova",
    "Sălaj": "Sălaj",
    "Satu Mare": "Satu Mare",
    "Sibiu": "Sibiu",
    "Suceava": "Suceava",
    "Teleorman": "Teleorman",
    "Timiș": "Timiș",
    "Tulcea": "Tulcea",
    "Vâlcea": "Valcea",
    "Vaslui": "Vaslui",
    "Vrancea": "Vrancea",
}

# state-ul scris in res_zip.sql (ASCII, fara diacritice) per judet.
STATE_NAME = {
    "Alba": "Alba",
    "Arad": "Arad",
    "Argeș": "Arges",
    "Bacău": "Bacau",
    "Bihor": "Bihor",
    "Bistrița-Năsăud": "Bistrita-Nasaud",
    "Botoșani": "Botosani",
    "Brăila": "Braila",
    "Brașov": "Brasov",
    "București": "Bucuresti",
    "Buzău": "Buzau",
    "Călărași": "Calarasi",
    "Caraș-Severin": "Caras-Severin",
    "Cluj": "Cluj",
    "Constanța": "Constanta",
    "Covasna": "Covasna",
    "Dâmbovița": "Dambovita",
    "Dolj": "Dolj",
    "Galați": "Galati",
    "Giurgiu": "Giurgiu",
    "Gorj": "Gorj",
    "Harghita": "Harghita",
    "Hunedoara": "Hunedoara",
    "Ialomița": "Ialomita",
    "Iași": "Iasi",
    "Ilfov": "Ilfov",
    "Maramureș": "Maramures",
    "Mehedinți": "Mehedinti",
    "Mureș": "Mures",
    "Neamț": "Neamt",
    "Olt": "Olt",
    "Prahova": "Prahova",
    "Sălaj": "Salaj",
    "Satu Mare": "Satu Mare",
    "Sibiu": "Sibiu",
    "Suceava": "Suceava",
    "Teleorman": "Teleorman",
    "Timiș": "Timis",
    "Tulcea": "Tulcea",
    "Vâlcea": "Valcea",
    "Vaslui": "Vaslui",
    "Vrancea": "Vrancea",
}

# Tip strada live (forma articulata) -> vocabular scurt din res_zip.sql.
STREET_TYPE_MAP = {
    "Strada": "Strada",
    "Stradela": "Stradela",
    "Strădela": "Stradela",
    "Bulevardul": "Bulevard",
    "Bulevard": "Bulevard",
    "Șoseaua": "Sosea",
    "Soseaua": "Sosea",
    "Sosea": "Sosea",
    "Aleea": "Alee",
    "Alee": "Alee",
    "Calea": "Cale",
    "Cale": "Cale",
    "Intrarea": "Intrare",
    "Intrare": "Intrare",
    "Piața": "Piata",
    "Piata": "Piata",
    "Piaţa": "Piata",
    "Drumul": "Drum",
    "Drum": "Drum",
    "Splaiul": "Splai",
    "Splai": "Splai",
    "Fundătura": "Fundatura",
    "Fundatura": "Fundatura",
    "Fundacul": "Fundac",
    "Fundac": "Fundac",
    "Prelungirea": "Prelungire",
    "Prelungire": "Prelungire",
    "Pasajul": "Pasaj",
    "Pasaj": "Pasaj",
    "Cartierul": "Cartier",
    "Cartier": "Cartier",
    "Parcul": "Parc",
    "Parc": "Parc",
    "Curtea": "Curte",
}
STREET_TYPE_PREFIXES = sorted(STREET_TYPE_MAP, key=len, reverse=True)


def strip_diacritics(s):
    if not s:
        return ""
    s = s.replace("ș", "s").replace("ş", "s").replace("ț", "t").replace("ţ", "t")
    s = s.replace("Ș", "S").replace("Ş", "S").replace("Ț", "T").replace("Ţ", "T")
    # mojibake in datele 2013: 'ª' (U+00AA) = Ș/ș corupt -> altfel 'ªcheia' nu matchuieste 'Scheia'
    s = s.replace("ª", "s").replace("º", "t")
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def norm_key(s):
    """Cheie de comparatie: fara diacritice, lower, spatii colapsate.

    Unifica ortografia veche (î) cu cea noua (â) — datele 2013 au 'Avîntului',
    posta returneaza 'Avântului'; ambele -> 'avintului', altfel ar aparea fals nou/disparut.
    """
    s = s or ""
    s = s.replace("â", "î").replace("Â", "Î")  # unifica â->î inainte de strip (ambele -> 'i')
    s = strip_diacritics(s).lower()
    s = re.sub(r"[^\w]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def split_street(combined):
    """'Șoseaua Păcurari nr. 59-T' -> ('Sosea', 'Pacurari nr. 59-T') in stil res_zip."""
    combined = (combined or "").strip()
    if not combined or combined == "-":
        return "", ""
    for pref in STREET_TYPE_PREFIXES:
        if combined == pref or combined.startswith(pref + " "):
            rest = combined[len(pref) :].strip()
            return STREET_TYPE_MAP[pref], strip_diacritics(rest)
    # fara tip recunoscut -> tot in street_name
    return "", strip_diacritics(combined)


def _post(endpoint, data, retries=3):
    body = urllib.parse.urlencode(data).encode()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                f"{BASE}/{endpoint}?q=",
                data=body,
                headers={"User-Agent": UA, "X-Requested-With": "XMLHttpRequest"},
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:  # noqa: BLE001
            if attempt == retries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))


def get_localities(judet_val):
    """Returneaza [(value, label, klass)] pentru un judet.

    value = ce trimitem in k_localitate (ASCII-ish); label = textul optiunii (cu
    diacritice, necesar pentru OSM); klass in {'sub_50_mii','peste_50_mii'}.
    """
    data = _post("cauta_orase.php", {"k_judet": judet_val, "k_lang": "ro"})
    formular = data.get("formular", "")
    out = []
    for m in re.finditer(r"<option[^>]*?class='([^']+)'[^>]*?value='([^']+)'\s*>(.*?)</option>", formular):
        klass, value, label = m.group(1), html.unescape(m.group(2)), html.unescape(m.group(3)).strip()
        out.append((value, label, klass))
    return out


_P = re.compile(r"<p[^>]*>(.*?)</p>", re.S)
_LINE = re.compile(r"cod-postal-line.*?(?=cod-postal-line|$)", re.S)
_A = re.compile(r"<a[^>]*>(.*?)</a>", re.S)


def _clean(x):
    return re.sub(r"<[^>]+>", "", html.unescape(x)).strip()


def search_address(judet_val, localitate, adresa=""):
    """Returneaza randuri brute: dict(zip, state, city, street_combined, office)."""
    data = _post(
        "cautare_pentru_cod.php",
        {
            "k_adresa": adresa,
            "k_judet": judet_val,
            "k_localitate": localitate,
            "k_lang": "ro",
        },
    )
    formular = data.get("formular", "")
    rows = []
    if "nu a furnizat" in formular or "completati toate" in formular:
        return rows
    for block in _LINE.findall(formular):
        ps = [_clean(p) for p in _P.findall(block)]
        ps = [p for p in ps if p]
        office = _clean(_A.search(block).group(1)) if _A.search(block) else ""
        if len(ps) >= 3 and re.match(r"^\d{5,6}$", ps[0]):
            rows.append(
                {
                    "zip": ps[0],
                    "state": ps[1],
                    "city": ps[2],
                    "street": ps[3] if len(ps) > 3 and ps[3] != "-" else "",
                    "office": office,
                }
            )
    return rows
