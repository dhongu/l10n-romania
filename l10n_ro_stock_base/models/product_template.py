# Copyright (C) 2021 NextERP Romania
# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


def _l10n_ro_remove_duplicates(arch, xpaths):
    """Keep only the first node of each xpath.

    While the OCA ``l10n_ro_stock`` module is still installed, its views add
    the same fields to the same forms, so they would be shown twice.
    """
    for xpath in xpaths:
        for node in arch.xpath(xpath)[1:]:
            node.getparent().remove(node)
    return arch


NET_WEIGHT_XPATHS = [
    "//label[@for='l10n_ro_net_weight']",
    "//div[@name='l10n_ro_net_weight']",
]


class ProductTemplate(models.Model):
    _inherit = "product.template"

    l10n_ro_net_weight = fields.Float(
        "Net Weight",
        compute="_compute_l10n_ro_net_weight",
        inverse="_inverse_l10n_ro_net_weight",
        digits="Stock Weight",
        store=True,
    )
    l10n_ro_net_weight_uom_name = fields.Char(
        string="Net Weight unit of measure label",
        compute="_compute_l10n_ro_net_weight_uom_name",
    )

    def _compute_l10n_ro_net_weight_uom_name(self):
        self.l10n_ro_net_weight_uom_name = self._get_weight_uom_name_from_ir_config_parameter()

    @api.depends("product_variant_ids.l10n_ro_net_weight")
    def _compute_l10n_ro_net_weight(self):
        self._compute_template_field_from_variant_field("l10n_ro_net_weight")

    def _inverse_l10n_ro_net_weight(self):
        self._set_product_variant_field("l10n_ro_net_weight")

    def _get_related_fields_variant_template(self):
        # Written on the first variant after it is created, like the weight.
        return super()._get_related_fields_variant_template() + ["l10n_ro_net_weight"]

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == "form":
            _l10n_ro_remove_duplicates(arch, NET_WEIGHT_XPATHS)
        return arch, view


class ProductProduct(models.Model):
    _inherit = "product.product"

    l10n_ro_net_weight = fields.Float("Net Weight", digits="Stock Weight")

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == "form":
            _l10n_ro_remove_duplicates(arch, NET_WEIGHT_XPATHS)
        return arch, view
