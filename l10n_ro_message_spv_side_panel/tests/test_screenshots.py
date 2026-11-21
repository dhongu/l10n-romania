# © 2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
#
# Capturi de ecran pentru fișa „Mesaje SPV: vedere împărțită" (RO, fișă) și pentru
# readme/USAGE.md (EN, Apps Store). Seedează mesaje SPV din ZIP-uri construite local,
# fără apeluri la ANAF.
#
# Rulare:
#   ./odoo/odoo-bin -c odoo.conf -d <db> \
#       -i l10n_ro_message_spv_side_panel,l10n_ro_doc_screenshots \
#       --test-tags=fise_screenshots --stop-after-init
import io
import unittest
import zipfile

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

from .test_message_spv_side_panel import INVOICE_XML

try:
    from odoo.addons.l10n_ro_doc_screenshots.tests.screenshot_case import (
        ScreenshotCase,
    )
except ImportError:
    ScreenshotCase = None

ACTION = "l10n_ro_message_spv_side_panel.action_l10n_ro_message_spv_split"

# (furnizor, număr, data, scadența, CUI, id mesaj)
INVOICES = [
    ("Termo Instal Distribuție SRL", "TID 4521", "2026-11-03", "2026-12-03", "RO14567890", "5120656685"),
    ("Clima Parts Europe SRL", "CPE-2026-1187", "2026-11-05", "2026-11-08", "RO21908765", "5120656671"),
    ("Electro Automatizări SRL", "EA 00917", "2026-11-06", "2026-12-06", "RO33018422", "5120260796"),
    ("Transport Rapid Logistic SRL", "TRL 3302", "2026-11-07", "2026-11-13", "RO18273645", "5120656649"),
]

# click pe factura TID 4521 (card sau rând) și așteptarea panoului; primul mesaj din listă e cel cu eroare, fără XML
OPEN_INVOICE_CARD = (
    "(async () => {"
    "  const card = [...document.querySelectorAll('.o_kanban_record')].find((c) => c.innerText.includes('TID 4521'));"
    "  if (card) { card.click(); }"
    "  await new Promise((r) => setTimeout(r, 3000));"
    "})()"
)
OPEN_INVOICE_ROW = (
    "(async () => {"
    "  const row = [...document.querySelectorAll('.o_data_row')].find((r) => r.innerText.includes('TID 4521'));"
    "  const cell = row && row.querySelector('.o_data_cell');"
    "  if (cell) { cell.click(); }"
    "  await new Promise((r) => setTimeout(r, 3000));"
    "})()"
)
OPEN_TOTALS = (
    "(async () => {"
    "  const card = [...document.querySelectorAll('.o_kanban_record')].find((c) => c.innerText.includes('TID 4521'));"
    "  if (card) { card.click(); }"
    "  await new Promise((r) => setTimeout(r, 3000));"
    "  const body = document.querySelector('.o_side_panel_body');"
    "  if (body) { body.scrollTop = body.scrollHeight; }"
    "  await new Promise((r) => setTimeout(r, 500));"
    "})()"
)


@tagged("-at_install", "post_install", "fise_screenshots")
class TestSpvSidePanelScreenshots(AccountTestInvoicingCommon, ScreenshotCase or object):
    screenshots_module = "l10n_ro_message_spv_side_panel"

    @classmethod
    @AccountTestInvoicingCommon.setup_country("ro")
    def setUpClass(cls):
        if ScreenshotCase is None:
            raise unittest.SkipTest("l10n_ro_doc_screenshots indisponibil")
        super().setUpClass()
        cls.prepare_ro_company(name="Demo SPV SRL")
        env = cls.env
        company = env.company
        admin = env.ref("base.user_admin")
        admin.write({"company_ids": [(6, 0, company.ids)], "company_id": company.id})
        admin.group_ids = [(3, env.ref("base.group_multi_company").id)]

        # fără CIF pe mesaj: CUI-ul furnizorului vine din XML, iar furnizorul nu există în Odoo
        messages = env["l10n.ro.message.spv"]
        cls.invoice_message = None
        for name, ref, date, due, vat, message_id in INVOICES:
            xml = (
                INVOICE_XML.replace(b"Termo Instal Distributie SRL", name.encode())
                .replace(b"TID 4521", ref.encode())
                .replace(b"2026-11-03", date.encode())
                .replace(b"2026-12-03", due.encode())
                .replace(b"RO14567890", vat.encode())
                .replace(b"Cumparator Test SRL", company.name.encode())
                .replace(b"Pompa circulatie 25/60", "Pompă circulație 25/60".encode())
            )
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w") as archive:
                archive.writestr(f"{message_id}.xml", xml)
            attachment = env["ir.attachment"].create({"name": f"{message_id}.zip", "raw": buffer.getvalue()})
            message = messages.create(
                {
                    "name": message_id,
                    "request_id": message_id,
                    "cif": False,
                    "message_type": "in_invoice",
                    "state": "downloaded",
                    "attachment_id": attachment.id,
                    "file_name": f"{message_id}.zip",
                    "company_id": company.id,
                }
            )
            message.get_xml_fom_zip()
            if ref == "TID 4521":
                cls.invoice_message = message
        # a message whose archive has not been downloaded: a draft, with no data from the XML
        messages.create(
            {
                "name": "5120656700",
                "cif": False,
                "message_type": "in_invoice",
                "state": "draft",
                "date": "2026-11-12 08:30:00",
                "company_id": company.id,
            }
        )
        messages.create(
            {
                "name": "5120656640",
                "cif": False,
                "message_type": "in_invoice",
                "state": "error",
                "partner_name": "Montaj Industrial Nord SRL",
                "ref": "MIN 0291",
                "invoice_date": "2026-11-11",
                "error": "Arhiva descărcată nu a putut fi citită.",
                "company_id": company.id,
            }
        )

    def _url(self, view_type):
        action = self.env.ref(ACTION)
        return f"action={action.id}&view_type={view_type}"

    def _shots(self):
        return [
            {
                "url": self._url("kanban"),
                "name": "01_meniu_vedere_impartita.png",
                "wait": ".o_kanban_record",
                "settle": 2000,
            },
            {
                "url": self._url("kanban"),
                "name": "02_panou_document.png",
                "wait": ".o_kanban_record",
                "eval": OPEN_INVOICE_CARD,
                "eval_wait": 1500,
                "highlight": [".o_side_panel [name='spv_party_vat']", ".o_side_panel .o_side_panel_next"],
                "settle": 2000,
            },
            {
                "url": self._url("kanban"),
                "name": "04_document_totaluri.png",
                "wait": ".o_kanban_record",
                "eval": OPEN_TOTALS,
                "eval_wait": 1500,
                "settle": 2000,
            },
            {
                "url": self._url("kanban"),
                "name": "05_actiuni_panou.png",
                "wait": ".o_kanban_record",
                "eval": OPEN_INVOICE_CARD,
                "eval_wait": 1500,
                "highlight": [
                    ".o_side_panel button[name='create_invoice']",
                    ".o_side_panel button[name='action_download_xml']",
                    ".o_side_panel button[name='action_download_pdf']",
                    ".o_side_panel button[name='action_download_attachment']",
                ],
                "settle": 2000,
            },
            {
                "url": f"action={self.env.ref(ACTION).id}&id={self.invoice_message.id}&view_type=form",
                "name": "07_formular_complet.png",
                "wait": ".o_form_view",
                "settle": 2000,
            },
            {
                "url": self._url("list"),
                "name": "06_lista_cu_panou.png",
                "wait": ".o_data_row",
                "eval": OPEN_INVOICE_ROW,
                "eval_wait": 1500,
                "settle": 2000,
            },
        ]

    def test_capture_fise(self):
        """RO: capturile fișei consultant."""
        self.capture_screenshots(self._shots(), viewport=(1920, 1100))

    def test_capture_usage(self):
        """EN: capturile pentru readme/USAGE.md."""
        self.capture_screenshots(self._shots(), lang="en_US", viewport=(1920, 1100))
