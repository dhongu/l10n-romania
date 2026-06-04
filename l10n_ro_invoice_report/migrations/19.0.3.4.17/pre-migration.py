# ©  2008-2026 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Convert res_partner.payment_bank_id to company-dependent storage.

    Older versions stored ``payment_bank_id`` as a regular integer (Many2one)
    column. The field is now ``company_dependent=True``, which in Odoo 17+ is
    stored as a jsonb column keyed by company id. PostgreSQL cannot cast
    integer to jsonb automatically, so the data must be migrated explicitly.

    We rely on the official ``odoo.upgrade.util`` helper when available
    (Odoo.sh / Enterprise upgrade context) and fall back to a portable SQL
    migration otherwise (on-premise / plain ``-u`` updates).
    """
    cr.execute(
        """
        SELECT data_type
          FROM information_schema.columns
         WHERE table_name = 'res_partner'
           AND column_name = 'payment_bank_id'
        """
    )
    row = cr.fetchone()
    if not row:
        # Column does not exist yet; Odoo will create it as jsonb.
        return
    if row[0] == "jsonb":
        # Already migrated.
        return

    _logger.info(
        "Migrating res_partner.payment_bank_id from %s to company-dependent (jsonb) storage",
        row[0],
    )

    try:
        from odoo.upgrade import util
    except ImportError:
        util = None

    if util is not None:
        util.make_field_company_dependent(
            cr,
            "res.partner",
            "payment_bank_id",
            "many2one",
            target_model="res.partner.bank",
        )
        return

    # Portable fallback: preserve the existing value for every company.
    _logger.info("odoo.upgrade.util not available, using SQL fallback")
    cr.execute("SELECT array_agg(id) FROM res_company")
    company_ids = cr.fetchone()[0] or []

    cr.execute("ALTER TABLE res_partner RENAME COLUMN payment_bank_id TO payment_bank_id_old")
    cr.execute("ALTER TABLE res_partner ADD COLUMN payment_bank_id jsonb")

    for company_id in company_ids:
        cr.execute(
            """
            UPDATE res_partner
               SET payment_bank_id =
                   COALESCE(payment_bank_id, '{}'::jsonb)
                   || jsonb_build_object(%s, payment_bank_id_old)
             WHERE payment_bank_id_old IS NOT NULL
            """,
            (str(company_id),),
        )

    cr.execute("ALTER TABLE res_partner DROP COLUMN payment_bank_id_old")
