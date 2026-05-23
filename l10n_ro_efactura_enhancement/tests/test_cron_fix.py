# ©  2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
from unittest.mock import patch

from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestAccountMoveSendCronFix(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.partner = cls.env["res.partner"].create({
            "name": "Test Partner RO",
            "country_id": cls.env.ref("base.ro").id,
            "state_id": cls.env.ref("base.RO_B").id,
            "city": "Bucuresti",
            "street": "Str. Test 1",
        })
        cls.product = cls.env["product.product"].create({
            "name": "Test Product",
        })

    def _create_invoice(self, sending_data=None):
        invoice = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.partner.id,
            "invoice_line_ids": [(0, 0, {
                "product_id": self.product.id,
                "quantity": 1,
                "price_unit": 100,
            })],
        })
        invoice.action_post()
        if sending_data is not None:
            invoice.sending_data = sending_data
        return invoice

    def test_cron_account_move_send_keyerror(self):
        """Test că facturile fără author_partner_id în sending_data sunt resetate corect (fix migrare 17.0)."""
        invoice = self._create_invoice(sending_data={"some_key": "some_value"})
        # sending_data fără author_partner_id — simulează date migrate din 17.0
        self.assertFalse(invoice.sending_data.get("author_partner_id"))

        # Apelăm cron-ul — ar trebui să reseteze sending_data fără a ridica KeyError
        self.env["account.move"]._cron_account_move_send(job_count=10)

        invoice.invalidate_recordset(["sending_data"])
        # După reset, sending_data trebuie să fie False
        self.assertFalse(invoice.sending_data)
