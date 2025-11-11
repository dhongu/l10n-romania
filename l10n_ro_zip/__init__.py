# © 2025 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from . import models


import logging
from odoo.tools.misc import file_path
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Import SQL file res_zip.sql to populate res_zip table"""
    _logger.info("Importing zip codes from res_zip.sql")

    sql_file_path = file_path("l10n_ro_zip/data/res_zip.sql")

    with open(sql_file_path) as sql_file:
        sql_script = sql_file.read()
        # Executăm script-ul SQL pentru a popula tabela
        env.cr.execute(sql_script)
    _logger.info("Zip codes imported successfully")

    country_ro = env.ref("base.ro", raise_if_not_found=False)

    if country_ro:
        env.cr.execute("""UPDATE res_zip SET country_id = %s WHERE country_id IS NULL""", (country_ro.id,))

    # Obținem toate înregistrările din res.country.state care au l10n_ro_prefix_zip setat
    states = env["res.country.state"].search([("l10n_ro_prefix_zip", "!=", False)])

    sql = "CREATE EXTENSION IF NOT EXISTS unaccent;"
    env.cr.execute(sql)

    # Pentru fiecare judet, actualizăm înregistrările din res_zip care au state-ul potrivit
    for state in states:
        sql = """
              UPDATE res_zip
              SET state_id = %s
              WHERE SUBSTRING(name, 1, 2) = %s
              """
        env.cr.execute(sql, (state.id, state.l10n_ro_prefix_zip))

    # Actualizăm și city_id dacă există potriviri
    sql = """
          UPDATE res_zip rz
          SET city_id = rc.id FROM res_city rc
          WHERE unaccent(rz.city) = unaccent(rc.name->>'en_US')
            AND rz.state_id = rc.state_id
            AND rz.name = rc.zipcode
          """
    env.cr.execute(sql)

    # Actualizăm și city_id dacă există potriviri
    sql = """
          UPDATE res_zip rz
          SET city_id = rc.id FROM res_city rc
          WHERE unaccent(rz.city) = unaccent(rc.name->>'en_US')
            AND rz.state_id = rc.state_id
            AND city_id is null
          """
    env.cr.execute(sql)

    sectors = {
        "1": "l10n_ro_city.RO_179141",
        "2": "l10n_ro_city.RO_179150",
        "3": "l10n_ro_city.RO_179169",
        "4": "l10n_ro_city.RO_179178",
        "5": "l10n_ro_city.RO_179187",
        "6": "l10n_ro_city.RO_179196",
    }
    for sector, city_ref in sectors.items():
        city = env.ref(city_ref)
        sql = """
              UPDATE res_zip
              SET city_id = %(city_id)s
              WHERE sector = %(sector)s
              """
        env.cr.execute(
            sql,
            {
                "sector": sector,
                "city_id": city.id,
                "city": city.name,
            },
        )

    _logger.info("State_id, country_id and city_id update completed")
