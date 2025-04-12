import logging

from odoo import models
from odoo.http import request

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = ["ir.http"]

    @classmethod
    def get_nearest_lang(cls, lang_code: str) -> str:
        res = super().get_nearest_lang(lang_code)
        country_code = request.geoip.country_code
        if country_code == "RO" and not lang_code:
            res = "ro_RO"
        return res
