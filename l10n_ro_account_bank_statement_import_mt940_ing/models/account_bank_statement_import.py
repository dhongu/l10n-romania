# Copyright (C) 2016 Forest and Biomass Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models

from .mt940 import MT940Parser as Parser

_logger = logging.getLogger(__name__)


class AccountBankStatementImport(models.TransientModel):
    """Add parsing of mt940 files to bank statement import."""

    _inherit = "account.bank.statement.import"

    def _parse_file(self, data_file):
        """Each module adding a file support must extends this method. It processes the file if it can,
        returns super otherwise, resulting in a chain of responsability.
        This method parses the given file and returns the data required by the bank statement import process,
        as specified below.
        rtype: triplet (if a value can't be retrieved, use None)
            - currency code: string (e.g: 'EUR')
                The ISO 4217 currency code, case insensitive
            - account number: string (e.g: 'BE1234567890')
                The number of the bank account which the statement belongs to
            - bank statements data: list of dict containing (optional items marked by o) :
                - 'name': string (e.g: '000000123')
                - 'date': date (e.g: 2013-06-26)
                -o 'balance_start': float (e.g: 8368.56)
                -o 'balance_end_real': float (e.g: 8888.88)
                - 'transactions': list of dict containing :
                    - 'name': string (e.g: 'KBC-INVESTERINGSKREDIET 787-5562831-01')
                    - 'date': date
                    - 'amount': float
                    - 'unique_import_id': string
                    -o 'account_number': string
                        Will be used to find/create the res.partner.bank in odoo
                    -o 'note': string
                    -o 'partner_name': string
                    -o 'ref': string
        """

        parser = Parser()
        try:
            _logger.debug("Try parsing with MT940 IBAN ING.")
            return parser.parse(data_file)
        except ValueError as e:
            # Returning super will call next candidate:
            _logger.info(str(e))
            _logger.debug("Statement file was not a MT940 IBAN ING file.", exc_info=True)
            return super(AccountBankStatementImport, self)._parse_file(data_file)
