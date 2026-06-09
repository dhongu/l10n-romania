import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Mark already-uploaded invoices as 'validation email handled'.

    Until this version the customer invoice email was sent at SPV-upload time.
    From now on it is sent only after the SPV validates the invoice. Without
    this guard, every invoice already uploaded (invoice_sent / invoice_validated)
    would be emailed again the first time the new post-validation flow runs.
    We flag them as done so only invoices uploaded from now on trigger the
    post-validation email.
    """
    cr.execute(
        """
        UPDATE account_move
           SET l10n_ro_spv_validated_email_sent = TRUE
         WHERE l10n_ro_edi_state IN ('invoice_sent', 'invoice_validated')
        """
    )
    _logger.info(
        "l10n_ro_efactura_enhancement: flagged %s already-uploaded invoices as validation-email handled",
        cr.rowcount,
    )
