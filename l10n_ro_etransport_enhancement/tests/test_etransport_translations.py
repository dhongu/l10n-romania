# Copyright 2026
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

import re

from babel.messages.pofile import read_po

from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import file_open


@tagged("post_install", "-at_install")
class TestEtransportTranslations(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.lang"]._activate_lang("ro_RO")
        cls.env["ir.module.module"].search([("name", "=", "l10n_ro_etransport_enhancement")])._update_translations(
            filter_lang="ro_RO", overwrite=True
        )

    def test_document_name_uses_user_language(self):
        document = self.env["l10n.ro.etransport.document"].new({"document_type": "20", "name": "TEST-1"})
        self.assertEqual(document.with_context(lang="en_US").display_name, "Invoice TEST-1")
        self.assertEqual(document.with_context(lang="ro_RO").display_name, "Factură TEST-1")

    def test_field_help_and_label_are_translated(self):
        description = (
            self.env["stock.picking"]
            .with_context(lang="ro_RO")
            .fields_get(
                [
                    "l10n_ro_etransport_start_address",
                    "l10n_ro_edi_stock_required",
                ]
            )
        )
        self.assertEqual(description["l10n_ro_edi_stock_required"]["string"], "eTransport necesar")
        self.assertIn("Adresa efectivă de încărcare", description["l10n_ro_etransport_start_address"]["help"])

    def test_catalog_complete_and_preserves_named_placeholders(self):
        with file_open("l10n_ro_etransport_enhancement/i18n/ro.po", "rb") as source:
            catalog = read_po(source)
        self.assertGreater(len(catalog), 70)
        for message in catalog:
            if not message.id:
                continue
            self.assertTrue(message.string, message.id)
            self.assertEqual(
                sorted(re.findall(r"%\([^)]+\)[a-z]", message.id)),
                sorted(re.findall(r"%\([^)]+\)[a-z]", message.string)),
                message.id,
            )
