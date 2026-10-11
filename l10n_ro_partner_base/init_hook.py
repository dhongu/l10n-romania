# Copyright 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    """Prepare the database before the module's fields are created.

    1. res_partner.l10n_ro_vat_number is stored and computed from vat: on a
       database with many partners the ORM recompute at install is very slow,
       so the column is added and filled with SQL.
    2. When the OCA l10n_ro_config module is already installed the column
       exists with data, so nothing is recomputed.

    TODO: decide whether the hook should also link the existing ir.model.data
    of the shared fields to this module (not done yet; needs a test on a copy).
    """
    cr = env.cr
    cr.execute(
        """SELECT 1 FROM information_schema.columns
           WHERE table_name='res_partner' AND column_name='l10n_ro_vat_number'"""
    )
    if not cr.fetchone():
        cr.execute("ALTER TABLE res_partner ADD COLUMN l10n_ro_vat_number varchar")
        cr.execute(
            r"""UPDATE res_partner
                SET l10n_ro_vat_number = NULLIF(regexp_replace(vat, '[^\.\d]', '', 'g'), '')"""
        )
        _logger.info("l10n_ro_vat_number computed with SQL")

    # CAEN lives only on res.company now: take it over from the company's
    # partner when the OCA l10n_ro_config module left it there ("0000" = unset)
    cr.execute(
        """SELECT 1 FROM information_schema.columns
           WHERE table_name='res_company' AND column_name='l10n_ro_caen_code'"""
    )
    if not cr.fetchone():
        cr.execute("ALTER TABLE res_company ADD COLUMN l10n_ro_caen_code varchar")
        cr.execute(
            """SELECT 1 FROM information_schema.columns
               WHERE table_name='res_partner' AND column_name='l10n_ro_caen_code'"""
        )
        if cr.fetchone():
            cr.execute(
                """UPDATE res_company c
                   SET l10n_ro_caen_code = p.l10n_ro_caen_code
                   FROM res_partner p
                   WHERE p.id = c.partner_id
                     AND p.l10n_ro_caen_code IS NOT NULL
                     AND p.l10n_ro_caen_code <> '0000'"""
            )
            _logger.info("l10n_ro_caen_code copied from partner to company")

    # The uniqueness of partners used to be enforced by the OCA module
    # l10n_ro_partner_unique, which has no parameter value of its own and then
    # defaults to "vat". Keep that behaviour on databases where it is installed.
    cr.execute(
        """SELECT 1 FROM ir_module_module
           WHERE name = 'l10n_ro_partner_unique' AND state = 'installed'"""
    )
    if cr.fetchone():
        param = env["ir.config_parameter"].sudo()
        if not param.get_param("l10n_ro_partner_unique.vat_nrc_unique"):
            param.set_param("l10n_ro_partner_unique.vat_nrc_unique", "vat")
            _logger.info("l10n_ro_partner_unique.vat_nrc_unique set to 'vat'")
