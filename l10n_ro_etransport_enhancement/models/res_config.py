# © 2025 Deltatech
#              Dan Stoica
# See README.rst file on addons root folder for license details

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_ro_etransport_get_order_value = fields.Boolean()
    l10n_ro_etransport_get_validated_qty = fields.Boolean()


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_ro_etransport_get_order_value = fields.Boolean(
        related="company_id.l10n_ro_etransport_get_order_value",
        string="UIT: get price from order",
        readonly=False,
        help="Compute UIT prices from sales orders (if delivery) or purchase orders (if reception).",
    )

    l10n_ro_etransport_get_validated_qty = fields.Boolean(
        related="company_id.l10n_ro_etransport_get_validated_qty",
        string="UIT: get only validated quantity",
        readonly=False,
        help="Get only validated quantity from the picking instead of picking quantity",
    )
