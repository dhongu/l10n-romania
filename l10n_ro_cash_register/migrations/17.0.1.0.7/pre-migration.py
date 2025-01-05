import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("_____________ Migration pre-script  _____________")

    # drop account_move_unique_name

    cr.execute("""
        DROP INDEX IF EXISTS account_move_unique_name;
    """)
