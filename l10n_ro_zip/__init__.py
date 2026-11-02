# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from . import models


import logging
from odoo.tools import SQL
from odoo.tools.sql import column_exists
from odoo.tools.misc import file_path

from .zip_prefix import ZIP_PREFIX_STATE

_logger = logging.getLogger(__name__)

# Refresh of res_zip.sql from posta-romana.ro, made by tools/build_delta.py; it can be applied more
# than once. The streets of small towns from OpenStreetMap (ODbL) are in the module l10n_ro_zip_osm.
DELTA_FILES = ("res_zip_delta.sql",)


def apply_zip_delta(env):
    """Apply the delta files on top of res_zip.sql, inside the current transaction."""
    for name in DELTA_FILES:
        _logger.info("Applying postal code update %s", name)
        with open(file_path(f"l10n_ro_zip/data/{name}"), encoding="utf-8") as sql_file:
            # the files are also run with psql: their BEGIN/COMMIT would end Odoo's transaction
            sql_script = "".join(line for line in sql_file if line.strip() not in ("BEGIN;", "COMMIT;"))
        env.cr.execute(sql_script)


# last id in res_zip.sql: rows above it were inserted later (delta files, users)
RES_ZIP_SQL_MAX_ID = 51898


def remove_duplicate_streets(env):
    """Delete the street rows a delta inserted twice: a row above res_zip.sql's ids that
    repeats an older row (same code, county, city, street type, street, sector and office).
    The older row stays, and a row a partner uses is never deleted."""
    env.cr.execute(
        """
        DELETE FROM res_zip z
         USING res_zip k
         WHERE z.id > %s AND k.id < z.id
           AND COALESCE(z.street_name, '') != ''
           AND k.name = z.name AND k.state = z.state AND k.city = z.city
           AND COALESCE(k.street_type, '') = COALESCE(z.street_type, '')
           AND COALESCE(k.street_name, '') = COALESCE(z.street_name, '')
           AND COALESCE(k.sector, '') = COALESCE(z.sector, '')
           AND COALESCE(k.office, '') = COALESCE(z.office, '')
           AND NOT EXISTS (SELECT 1 FROM res_partner p WHERE p.zip_id = z.id)
        """,
        (RES_ZIP_SQL_MAX_ID,),
    )
    return env.cr.rowcount


def _city_key(expr):
    """Locality name as compared between res_zip and res_city: without diacritics, case,
    hyphens and double spaces. The old res_zip.sql has "ª" for "Ș"."""
    return SQL(
        "lower(regexp_replace(replace(unaccent(replace(%s, 'ª', 'S')), '-', ' '), '\\s+', ' ', 'g'))",
        expr,
    )


def link_cities(env):
    """Link to res_city the rows of res_zip that have none, by county and locality name,
    also when the post office writes "Village (Commune)". A row is linked only to a single
    candidate, or to the single candidate with the same postal code."""
    zip_city = _city_key(SQL("z.city"))
    same_name = SQL("%s = %s", zip_city, _city_key(SQL("c.name->>'en_US'")))
    # the commune of a village comes with l10n_ro_city, when it is installed; the column, not the
    # field: without the dependency, l10n_ro_city may be loaded after this module on an upgrade
    if column_exists(env.cr, "res_city", "l10n_ro_municipality"):
        city_commune = _city_key(SQL("(c.name->>'en_US') || ' (' || c.l10n_ro_municipality || ')'"))
        same_name = SQL("(%s OR %s = %s)", same_name, zip_city, city_commune)
    env.cr.execute(
        SQL(
            """
            WITH cand AS (
                SELECT z.id AS zip_id, c.id AS city_id, c.zipcode = z.name AS same_zip,
                       COUNT(*) OVER (PARTITION BY z.id) AS n,
                       COUNT(*) FILTER (WHERE c.zipcode = z.name) OVER (PARTITION BY z.id) AS n_zip
                  FROM res_zip z
                  JOIN res_city c ON c.state_id = z.state_id AND %(same_name)s
                 WHERE z.city_id IS NULL
            )
            UPDATE res_zip z SET city_id = cand.city_id
              FROM cand
             WHERE z.id = cand.zip_id AND (cand.n = 1 OR (cand.n_zip = 1 AND cand.same_zip))
            """,
            same_name=same_name,
        )
    )
    return env.cr.rowcount


def link_states(env, only_missing=True):
    """County of the rows of res_zip from the first two digits of the postal code."""
    prefixes = SQL(", ").join(SQL("(%s, %s)", prefix, code) for prefix, code in ZIP_PREFIX_STATE.items())
    env.cr.execute(
        SQL(
            """
            UPDATE res_zip z SET state_id = s.id
              FROM (VALUES %s) AS p (prefix, code), res_country_state s, res_country c
             WHERE c.code = 'RO' AND s.country_id = c.id AND s.code = p.code
               AND SUBSTRING(z.name, 1, 2) = p.prefix %s
            """,
            prefixes,
            SQL("AND z.state_id IS NULL") if only_missing else SQL(),
        )
    )
    return env.cr.rowcount


def link_sectors(env):
    """The rows of Bucharest go to the locality of their sector ("Sector1" ... "Sector6")."""
    env.cr.execute(
        SQL(
            """
            UPDATE res_zip z SET city_id = rc.id, state_id = rc.state_id
              FROM res_city rc, res_country_state s, res_country c
             WHERE c.code = 'RO' AND s.country_id = c.id AND s.code = 'B' AND rc.state_id = s.id
               AND COALESCE(z.sector, '') != ''
               AND lower(replace(rc.name->>'en_US', ' ', '')) = 'sector' || trim(z.sector)
            """
        )
    )
    return env.cr.rowcount


def link_localities(env):
    """Link the rows without a locality to res_city: same name and postal code first, then
    same name, then the names written differently, and the Bucharest codes to their sector.
    Run on install and whenever Romanian localities are created (l10n_ro_city installed in the
    same run or later)."""
    env.cr.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    env.cr.execute(
        """
        UPDATE res_zip rz
           SET city_id = rc.id FROM res_city rc
         WHERE unaccent(rz.city) = unaccent(rc.name->>'en_US')
           AND rz.state_id = rc.state_id
           AND rz.name = rc.zipcode
           AND rz.city_id IS NULL
        """
    )
    env.cr.execute(
        """
        UPDATE res_zip rz
           SET city_id = rc.id FROM res_city rc
         WHERE unaccent(rz.city) = unaccent(rc.name->>'en_US')
           AND rz.state_id = rc.state_id
           AND rz.city_id IS NULL
        """
    )
    link_cities(env)
    link_sectors(env)


def post_init_hook(env):
    """Import SQL file res_zip.sql to populate res_zip table"""
    _logger.info("Importing zip codes from res_zip.sql")

    sql_file_path = file_path("l10n_ro_zip/data/res_zip.sql")

    env.cr.execute("SELECT COUNT(*) FROM res_zip")
    count = env.cr.fetchone()[0]
    if count == 0:
        with open(sql_file_path, encoding="utf-8") as sql_file:
            sql_script = sql_file.read()
            env.cr.execute(sql_script)
        # Resetăm secvența pentru a evita conflicte la inserări ulterioare prin ORM
        env.cr.execute("SELECT setval('res_zip_id_seq', (SELECT MAX(id) FROM res_zip))")
        _logger.info("Zip codes imported successfully")
    else:
        _logger.info("Zip codes already imported, skipping SQL import (%d records found)", count)

    apply_zip_delta(env)

    country_ro = env.ref("base.ro", raise_if_not_found=False)

    if country_ro:
        env.cr.execute("""UPDATE res_zip SET country_id = %s WHERE country_id IS NULL""", (country_ro.id,))

    sql = "CREATE EXTENSION IF NOT EXISTS unaccent;"
    env.cr.execute(sql)

    # județul, după primele două cifre ale codului poștal
    link_states(env, only_missing=False)

    link_localities(env)

    _logger.info("State_id, country_id and city_id update completed")
