from odoo.tests import common


class TestBankAccount(common.SavepointCase):
    def setUp(self):
        super(TestBankAccount, self).setUp()
        self.account = self.env["account.account"].create(
            {
                "name": "Test Account",
                "code": "1230001",
            }
        )

    def test_account_display_name(self):
        self.assertEqual(self.account.display_name, "123.1 Test Account")
