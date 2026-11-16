from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestNoticeDefault(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_type = cls.env["stock.picking.type"].search(
            [("code", "=", "incoming"), ("company_id", "=", cls.env.company.id)], limit=1
        )

    def _create_picking(self):
        return self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.picking_type.default_location_dest_id.id,
            }
        )

    def test_default_off(self):
        self.picking_type.l10n_ro_notice_default = False
        self.assertFalse(self._create_picking().l10n_ro_notice)

    def test_default_on(self):
        self.picking_type.l10n_ro_notice_default = True
        self.assertTrue(self._create_picking().l10n_ro_notice)

    def test_explicit_value_wins(self):
        self.picking_type.l10n_ro_notice_default = True
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.picking_type.default_location_dest_id.id,
                "l10n_ro_notice": False,
            }
        )
        self.assertFalse(picking.l10n_ro_notice)

    def test_default_get_from_type(self):
        self.picking_type.l10n_ro_notice_default = True
        values = (
            self.env["stock.picking"]
            .with_context(default_picking_type_id=self.picking_type.id)
            .default_get(["picking_type_id", "l10n_ro_notice"])
        )
        self.assertTrue(values.get("l10n_ro_notice"))

    def test_onchange_picking_type(self):
        self.picking_type.l10n_ro_notice_default = True
        picking = self.env["stock.picking"].new({"picking_type_id": self.picking_type.id})
        picking._onchange_picking_type_id_l10n_ro_notice()
        self.assertTrue(picking.l10n_ro_notice)
        self.picking_type.l10n_ro_notice_default = False
        picking._onchange_picking_type_id_l10n_ro_notice()
        self.assertFalse(picking.l10n_ro_notice)

    def test_default_get_explicit_context_wins(self):
        self.picking_type.l10n_ro_notice_default = True
        values = (
            self.env["stock.picking"]
            .with_context(
                default_picking_type_id=self.picking_type.id,
                default_l10n_ro_notice=False,
            )
            .default_get(["picking_type_id", "l10n_ro_notice"])
        )
        self.assertFalse(values.get("l10n_ro_notice"))
