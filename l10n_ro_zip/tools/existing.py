"""Incarca res_zip.sql existent in memorie + index pe cheie normalizata."""

import re

from posta import city_key, norm_key

# res_zip.sql e impartit in mai multe INSERT-uri: ultimul rand din fiecare se termina cu ");",
# restul cu "),". Valorile pot contine apostrof dublat ('').
_VAL = r"'((?:[^']|'')*)'"
ROW = re.compile(r"^\((\d+), " + ", ".join([_VAL] * 8) + r"\)[,;]?$")
COLS = ["id", "state", "city", "street_type", "street_name", "name", "sector", "office", "address"]


def load(sql_path):
    rows = []
    skipped = []
    with open(sql_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            m = ROW.match(line)
            if m:
                vals = [v.replace("''", "'") for v in m.groups()]
                rows.append(dict(zip(COLS, vals)))
            elif re.match(r"^\(\d+,", line):
                skipped.append(line)
    # un rand sarit = id maxim gresit sau strada lipsa la REPLACE -> oprim, nu ghicim
    if skipped:
        raise ValueError(f"{len(skipped)} randuri din {sql_path} nu au putut fi citite, ex.: {skipped[0][:120]}")
    return rows


def key(state, city, street_name):
    """Cheie de identitate a unei strazi/localitati (insensibila la diacritice/ortografie)."""
    return (norm_key(state), city_key(city), norm_key(street_name))


def build_index(rows):
    """key -> dict(id, zip, office, ...). Daca exista duplicate de cheie, pastram lista."""
    idx = {}
    for r in rows:
        k = key(r["state"], r["city"], r["street_name"])
        idx.setdefault(k, []).append(r)
    return idx


def max_id(rows):
    return max((int(r["id"]) for r in rows), default=0)
