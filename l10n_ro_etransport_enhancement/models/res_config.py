# © 2025 Deltatech
#              Dan Stoica
# See README.rst file on addons root folder for license details

from odoo import fields, models

from .etransport_api import DEFAULT_ETRANSPORT_TIMEOUT


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_ro_etransport_get_order_value = fields.Boolean()
    l10n_ro_etransport_timeout = fields.Integer(
        string="eTransport Timeout (s)",
        default=DEFAULT_ETRANSPORT_TIMEOUT,
        help="Maximum time to wait for an answer from the ANAF eTransport API. "
        "The Odoo standard uses 10 seconds, which is often too short.",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_ro_etransport_get_order_value = fields.Boolean(
        related="company_id.l10n_ro_etransport_get_order_value",
        string="UIT: get price from order",
        readonly=False,
        help="Compute UIT prices from sales orders (if delivery) or purchase orders (if reception).",
    )
    l10n_ro_etransport_timeout = fields.Integer(
        related="company_id.l10n_ro_etransport_timeout",
        string="eTransport Timeout (s)",
        readonly=False,
    )
