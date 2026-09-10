# ©  2026 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
"""Evenimentele de după UIT: ștergere, confirmare, modificare vehicul.

ANAF e simulat prin patch pe `ETransportActionsAPI`. Verificăm XML-ul randat,
ciclul de stare (sent → validated / failed) și că transferul e atins DOAR după
validare — nu după upload, când ANAF încă poate refuza.
"""

import base64
from unittest.mock import patch

from lxml import etree

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.l10n_ro_etransport_uit_actions.models.etransport_api_actions import ETransportActionsAPI

NS = "mfp:anaf:dgti:eTransport:declaratie:v2"
UPLOAD_OK = {"content": {"index_incarcare": "5001", "dateResponse": "202609101200"}}


@tagged("post_install", "-at_install")
class TestEtransportUitActions(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.write(
            {
                "vat": "RO1234567897",
                "country_id": cls.env.ref("base.ro").id,
                "account_fiscal_country_id": cls.env.ref("base.ro").id,
                "l10n_ro_edi_access_token": "test-token",
                "l10n_ro_edi_test_env": True,
            }
        )
        warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.company.id)], limit=1)
        partner = cls.env["res.partner"].create({"name": "Client UIT", "country_id": cls.env.ref("base.ro").id})
        product = cls.env["product.product"].create({"name": "Marfă UIT", "type": "consu", "weight": 1.0})
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": partner.id,
                "picking_type_id": warehouse.out_type_id.id,
                "location_id": warehouse.lot_stock_id.id,
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
                "l10n_ro_edi_stock_vehicle_number": "B123ABC",
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 5,
                            "location_id": warehouse.lot_stock_id.id,
                            "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
                        },
                    )
                ],
            }
        )
        # notificarea a fost deja validată de ANAF
        cls.env["l10n_ro_edi.document"].create(
            {
                "picking_id": cls.picking.id,
                "state": "stock_validated",
                "l10n_ro_edi_stock_uit": "3000000000000001",
                "l10n_ro_edi_stock_load_id": "4001",
                "attachment": base64.b64encode(b"<eTransport/>"),
            }
        )
        cls.picking.invalidate_recordset()

    def _wizard(self, event_type, **values):
        return self.env["l10n.ro.etransport.action.wizard"].create(
            {"picking_id": self.picking.id, "event_type": event_type, **values}
        )

    def _root(self, event):
        return etree.fromstring(base64.b64decode(event.attachment))

    # ------------------------------------------------------------------
    # Precondiții
    # ------------------------------------------------------------------

    def test_actions_enabled_only_on_validated_uit(self):
        self.assertEqual(self.picking.l10n_ro_edi_stock_document_uit, "3000000000000001")
        self.assertTrue(self.picking.l10n_ro_etransport_enable_actions)

        self.picking.l10n_ro_edi_stock_document_ids.unlink()
        self.picking.invalidate_recordset()
        self.assertFalse(self.picking.l10n_ro_etransport_enable_actions)
        with self.assertRaises(UserError):
            self._wizard("DEL").action_send()

    # ------------------------------------------------------------------
    # DEL
    # ------------------------------------------------------------------

    def test_delete_xml_and_sent_state(self):
        with patch.object(ETransportActionsAPI, "upload_data", return_value=UPLOAD_OK) as upload:
            self._wizard("DEL", remarks="  ", post_outage=True).action_send()

        event = self.picking.l10n_ro_etransport_event_ids
        self.assertEqual(len(event), 1)
        self.assertEqual(event.state, "sent")
        self.assertEqual(event.load_id, "5001")
        upload.assert_called_once()

        root = self._root(event)
        self.assertEqual(root.tag, f"{{{NS}}}eTransport")
        self.assertEqual(root.get("codDeclarant"), "1234567897")
        self.assertEqual(root.get("refDeclarant"), self.picking.name)
        self.assertEqual(root.get("declPostAvarie"), "D")
        stergere = root.find(f"{{{NS}}}stergere")
        self.assertEqual(stergere.get("uit"), "3000000000000001")
        # observația goală NU trebuie să ajungă atribut vid (Str200, minLength=1)
        self.assertIsNone(stergere.get("observatii"))

        # cu un eveniment în așteptare nu se mai poate trimite altul
        self.assertTrue(self.picking.l10n_ro_etransport_event_pending)
        self.assertFalse(self.picking.l10n_ro_etransport_enable_actions)

    def test_delete_validated_marks_uit_deleted(self):
        with patch.object(ETransportActionsAPI, "upload_data", return_value=UPLOAD_OK):
            self._wizard("DEL").action_send()
        event = self.picking.l10n_ro_etransport_event_ids

        with patch.object(ETransportActionsAPI, "get_status", return_value={"content": {"stare": "in prelucrare"}}):
            event.action_fetch_status()
        self.assertEqual(event.state, "sent")
        self.assertFalse(self.picking.l10n_ro_etransport_uit_deleted)

        with patch.object(ETransportActionsAPI, "get_status", return_value={"content": {"stare": "ok"}}):
            event.action_fetch_status()
        self.assertEqual(event.state, "validated")
        self.assertTrue(self.picking.l10n_ro_etransport_uit_deleted)
        self.assertFalse(self.picking.l10n_ro_etransport_enable_actions)
        # starea notificării standard NU e atinsă de evenimentele noastre
        self.assertEqual(self.picking.l10n_ro_edi_stock_state, "stock_validated")

    def test_upload_error_marks_failed_without_rollback(self):
        """O eroare sincronă NU ridică excepție: excepția ar anula tranzacția și
        ar pierde evenimentul respins + mesajul din chatter."""
        with patch.object(ETransportActionsAPI, "upload_data", return_value={"error": "Token expirat"}):
            action = self._wizard("DEL").action_send()
        self.assertEqual(action["tag"], "display_notification")
        self.assertEqual(action["params"]["type"], "danger")
        event = self.picking.l10n_ro_etransport_event_ids
        self.assertEqual(event.state, "failed")
        self.assertIn("Token expirat", event.message)
        self.assertFalse(self.picking.l10n_ro_etransport_uit_deleted)
        # doar evenimentele respinse pot fi șterse
        event.unlink()

    def test_status_error_marks_failed(self):
        with patch.object(ETransportActionsAPI, "upload_data", return_value=UPLOAD_OK):
            self._wizard("DEL").action_send()
        event = self.picking.l10n_ro_etransport_event_ids
        with patch.object(
            ETransportActionsAPI, "get_status", return_value={"content": {"stare": "XML cu erori nepreluat de sistem"}}
        ):
            self.env["l10n.ro.etransport.event"]._cron_fetch_status()
        self.assertEqual(event.state, "failed")
        self.assertFalse(self.picking.l10n_ro_etransport_uit_deleted)
        with self.assertRaises(UserError):
            self.picking.l10n_ro_etransport_event_ids.filtered(lambda e: e.state == "failed").write({"state": "sent"})
            self.picking.l10n_ro_etransport_event_ids.unlink()

    # ------------------------------------------------------------------
    # CON
    # ------------------------------------------------------------------

    def test_confirm_requires_type_and_renders(self):
        with self.assertRaises(UserError):
            self._wizard("CON").action_send()
        with patch.object(ETransportActionsAPI, "upload_data", return_value=UPLOAD_OK):
            self._wizard("CON", confirmation_type="20", remarks="lipsă 2 colete").action_send()
        event = self.picking.l10n_ro_etransport_event_ids
        confirmare = self._root(event).find(f"{{{NS}}}confirmare")
        self.assertEqual(confirmare.get("uit"), "3000000000000001")
        self.assertEqual(confirmare.get("tipConfirmare"), "20")
        self.assertEqual(confirmare.get("observatii"), "lipsă 2 colete")
        self.assertIsNone(self._root(event).get("declPostAvarie"))

    # ------------------------------------------------------------------
    # MVH
    # ------------------------------------------------------------------

    def test_modify_vehicle_applies_only_after_validation(self):
        with self.assertRaises(UserError):
            # aceeași plăcuță ca cea declarată
            self._wizard("MVH", vehicle_number="b123abc").action_send()
        with self.assertRaises(UserError):
            # plăcuțe duplicate
            self._wizard("MVH", vehicle_number="CJ01XYZ", trailer_1_number="cj01xyz").action_send()

        with patch.object(ETransportActionsAPI, "upload_data", return_value=UPLOAD_OK):
            self._wizard("MVH", vehicle_number="cj01xyz", trailer_1_number="cj02rem").action_send()
        event = self.picking.l10n_ro_etransport_event_ids
        modif = self._root(event).find(f"{{{NS}}}modifVehicul")
        self.assertEqual(modif.get("nrVehicul"), "CJ01XYZ")
        self.assertEqual(modif.get("nrRemorca1"), "CJ02REM")
        self.assertIsNone(modif.get("nrRemorca2"))
        self.assertRegex(modif.get("dataModificare"), r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")

        # după upload transferul NU e atins
        self.assertEqual(self.picking.l10n_ro_edi_stock_vehicle_number, "B123ABC")

        with patch.object(ETransportActionsAPI, "get_status", return_value={"content": {"stare": "ok"}}):
            event.action_fetch_status()
        self.assertEqual(event.state, "validated")
        self.assertEqual(self.picking.l10n_ro_edi_stock_vehicle_number, "cj01xyz")
        self.assertEqual(self.picking.l10n_ro_edi_stock_trailer_1_number, "cj02rem")
        self.assertFalse(self.picking.l10n_ro_edi_stock_trailer_2_number)
        # după validare UIT-ul e tot viu, se pot trimite alte evenimente
        self.assertTrue(self.picking.l10n_ro_etransport_enable_actions)

    def test_modify_vehicle_refused_keeps_plates(self):
        with patch.object(ETransportActionsAPI, "upload_data", return_value=UPLOAD_OK):
            self._wizard("MVH", vehicle_number="CJ01XYZ").action_send()
        event = self.picking.l10n_ro_etransport_event_ids
        with patch.object(ETransportActionsAPI, "get_status", return_value={"error": "UIT expirat"}):
            event.action_fetch_status()
        self.assertEqual(event.state, "failed")
        self.assertEqual(self.picking.l10n_ro_edi_stock_vehicle_number, "B123ABC")
