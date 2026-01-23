# © 2026 Deltatech
# See README.rst file on addons root folder for license details

import logging

import psycopg2

from odoo.tools import sql

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    # The goal is to avoid:
    # psycopg2.errors.CannotCoerce: cannot cast type integer to jsonb
    # which happens when Odoo 18 tries to convert the existing payment_bank_id (integer)
    # to jsonb (because it's now company_dependent).

    # We rename the column if it exists.
    # Since we don't have access to information_schema or pg_ catalogs,
    # we use a try-except block with a savepoint.

    try:
        with cr.savepoint():
            # Check if column exists by trying to select from it
            cr.execute("SELECT payment_bank_id FROM res_partner LIMIT 1")
    except psycopg2.Error:
        # Column likely doesn't exist, or table doesn't exist, nothing to do
        _logger.info("payment_bank_id does not exist in res_partner or table missing, skipping migration.")
    else:
        # Column exists, we migrate it
        _logger.info("Migrating payment_bank_id in res_partner to new jsonb format")
        try:
            # 1. Get the first company ID
            cr.execute("SELECT id FROM res_company ORDER BY id ASC LIMIT 1")
            res = cr.fetchone()
            if not res:
                _logger.warning("No company found, skipping data migration.")
                return
            company_id = res[0]

            # 2. Rename the old column
            sql.rename_column(cr, "res_partner", "payment_bank_id", "payment_bank_id_old")

            # 3. Create the new column as jsonb
            # Odoo 18 uses jsonb for company_dependent fields
            sql.create_column(cr, "res_partner", "payment_bank_id", "jsonb")

            # 4. Populate the new column for the first company
            # The format is {"company_id": value}
            query = """
                UPDATE res_partner
                SET payment_bank_id = jsonb_build_object(%s, payment_bank_id_old)
                WHERE payment_bank_id_old IS NOT NULL
            """
            cr.execute(query, (str(company_id),))
            _logger.info("Successfully migrated payment_bank_id data for company %s", company_id)

        except Exception as e:
            _logger.error("Failed to migrate payment_bank_id: %s", e)
