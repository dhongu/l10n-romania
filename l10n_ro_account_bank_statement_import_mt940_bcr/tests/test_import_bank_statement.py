# Copyright (C) 2016 Forest and Biomass Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from odoo.tests.common import TransactionCase
from odoo.modules.module import get_module_resource


class TestBCRImport(TransactionCase):
    """Run test to import MT940 BCR import."""

    def setUp(self):
        super(TestBCRImport, self).setUp()
        self.statement_import_model = self.env['account.bank.statement.import']
        self.bank_statement_model = self.env['account.bank.statement']

    def test_statement_import(self):
        """Test correct creation of single statement."""
        bcr_file_path = get_module_resource(
            'l10n_ro_account_bank_statement_import_mt940_bcr',
            'test_files', 'test_bcr_940.txt')
        bcr_file = open(bcr_file_path, 'rb').read()
        bcr_data_file = base64.b64encode(bcr_file)
        bank_statement = self.statement_import_model.create(dict(data_file=bcr_data_file))
        bank_statement.import_file()
        bank_st_record = self.bank_statement_model.search([('name', '=', '00138/1')])[0]
        self.assertEquals(bank_st_record.balance_start, 3885.24)
        self.assertEquals(bank_st_record.balance_end_real, 3671.88)

        line = bank_st_record.line_ids[-1]
        self.assertEquals(line.name, 'PLATA FACT 4603309')
        self.assertEquals(line.amount, -210.60)
