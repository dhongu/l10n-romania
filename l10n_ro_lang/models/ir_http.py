import logging

from odoo import api, models
from odoo.http import request

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @api.model
    def get_nearest_lang(self, lang_code: str) -> str:
        res = super().get_nearest_lang(lang_code)
        # sa citesc din cookies
        lang = request.httprequest.cookies.get("frontend_lang", False)
        if not lang:
            country_code = request.geoip.country_code or "RO"
            if country_code == "RO" and not lang_code:
                res = "ro_RO"
        return res
