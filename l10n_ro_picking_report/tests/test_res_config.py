# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from lxml import etree

from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestResConfigSettings(TransactionCase):
    def test_settings_view_shows_options(self):
        view = self.env.ref("l10n_ro_picking_report.res_config_settings_view_form_reception_taxes")
        self.assertEqual(view.inherit_id, self.env.ref("stock.res_config_settings_view_form"))

        arch = etree.fromstring(self.env["res.config.settings"].get_view(view_type="form")["arch"])
        block = arch.xpath("//app[@name='stock']//block[@name='l10n_ro_picking_report_setting_container']")
        self.assertTrue(block)
        self.assertTrue(block[0].xpath(".//field[@name='taxes_on_reception']"))
        self.assertTrue(block[0].xpath(".//field[@name='banks_on_pickings']"))

    def test_settings_write_company(self):
        company = self.env.company
        company.write({"taxes_on_reception": True, "banks_on_pickings": True})

        settings = Form(self.env["res.config.settings"])
        settings.taxes_on_reception = False
        settings.banks_on_pickings = False
        settings.save().execute()

        self.assertFalse(company.taxes_on_reception)
        self.assertFalse(company.banks_on_pickings)
