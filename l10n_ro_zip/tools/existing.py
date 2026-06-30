"""Incarca res_zip.sql existent in memorie + index pe cheie normalizata."""

import re

from posta import norm_key

ROW = re.compile(r"^\((\d+), '(.*?)', '(.*?)', '(.*?)', '(.*?)', '(.*?)', '(.*?)', '(.*?)', '(.*?)'\),?$")
COLS = ["id", "state", "city", "street_type", "street_name", "name", "sector", "office", "address"]


def load(sql_path):
    rows = []
    with open(sql_path, encoding="utf-8") as f:
        for line in f:
            m = ROW.match(line.strip())
            if m:
                rows.append(dict(zip(COLS, m.groups())))
    return rows


def key(state, city, street_name):
    """Cheie de identitate a unei strazi/localitati (insensibila la diacritice/ortografie)."""
    return (norm_key(state), norm_key(city), norm_key(street_name))


def build_index(rows):
    """key -> dict(id, zip, office, ...). Daca exista duplicate de cheie, pastram lista."""
    idx = {}
    for r in rows:
        k = key(r["state"], r["city"], r["street_name"])
        idx.setdefault(k, []).append(r)
    return idx


def max_id(rows):
    return max((int(r["id"]) for r in rows), default=0)
