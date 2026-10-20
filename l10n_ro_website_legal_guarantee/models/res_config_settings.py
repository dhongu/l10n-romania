# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    legal_guarantee_footer = fields.Boolean(related="website_id.legal_guarantee_footer", readonly=False)
    legal_guarantee_product = fields.Boolean(related="website_id.legal_guarantee_product", readonly=False)
    legal_guarantee_checkout = fields.Boolean(related="website_id.legal_guarantee_checkout", readonly=False)
