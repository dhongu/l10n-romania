# Copyright (C) 2019 NextERP Romania
# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    l10n_ro_consume_type_id = fields.Many2one("stock.picking.type", string="Romania - Consume Type")
    l10n_ro_usage_type_id = fields.Many2one("stock.picking.type", string="Romania - Usage Giving Type")

    def _get_picking_type_update_values(self):
        res = super()._get_picking_type_update_values()
        if self.company_id._l10n_ro_stock_is_romanian():
            if self.company_id.l10n_ro_consume_location_id:
                res.update({"l10n_ro_consume_type_id": {}})
            if self.company_id.l10n_ro_usage_location_id:
                res.update({"l10n_ro_usage_type_id": {}})
        return res

    def _get_picking_type_create_values(self, max_sequence):
        create_data, max_sequence = super()._get_picking_type_create_values(max_sequence)
        if self.company_id._l10n_ro_stock_is_romanian():
            usage_location = self.company_id.l10n_ro_usage_location_id
            consume_location = self.company_id.l10n_ro_consume_location_id
            code = self.code.replace(" ", "").upper()
            if consume_location:
                create_data["l10n_ro_consume_type_id"] = {
                    "name": self.env._("Consume"),
                    "code": "internal",
                    "use_create_lots": True,
                    "use_existing_lots": False,
                    "default_location_src_id": self.lot_stock_id.id,
                    "default_location_dest_id": consume_location.id,
                    "sequence": max_sequence + 6,
                    "barcode": code + "-CONSUME",
                    "sequence_code": "CONS",
                    "company_id": self.company_id.id,
                }
            if usage_location:
                create_data["l10n_ro_usage_type_id"] = {
                    "name": self.env._("Usage Giving"),
                    "code": "internal",
                    "use_create_lots": True,
                    "use_existing_lots": False,
                    "default_location_src_id": self.lot_stock_id.id,
                    "default_location_dest_id": usage_location.id,
                    "sequence": max_sequence + 7,
                    "barcode": code + "-USAGE",
                    "sequence_code": "USAGE",
                    "company_id": self.company_id.id,
                }
            max_sequence += 2
        return create_data, max_sequence

    def _get_sequence_values(self, name=False, code=False):
        sequences = super()._get_sequence_values(name=name, code=code)
        name = name or self.name
        code = code or self.code
        if self.company_id._l10n_ro_stock_is_romanian():
            sequences.update(
                {
                    "l10n_ro_consume_type_id": {
                        "name": name + " " + self.env._("Sequence Consume"),
                        "prefix": code + "/CONS/",
                        "padding": 5,
                        "company_id": self.company_id.id,
                    },
                    "l10n_ro_usage_type_id": {
                        "name": name + " " + self.env._("Sequence Usage Giving"),
                        "prefix": code + "/USAGE/",
                        "padding": 5,
                        "company_id": self.company_id.id,
                    },
                }
            )
        return sequences

    def _update_name_and_code(self, new_name=False, new_code=False):
        res = super()._update_name_and_code(new_name, new_code)
        for warehouse in self.filtered(lambda w: w.company_id._l10n_ro_stock_is_romanian()):
            sequence_data = warehouse._get_sequence_values(name=new_name, code=new_code)
            warehouse.l10n_ro_consume_type_id.sequence_id.sudo().write(sequence_data["l10n_ro_consume_type_id"])
            warehouse.l10n_ro_usage_type_id.sequence_id.sudo().write(sequence_data["l10n_ro_usage_type_id"])
        return res
