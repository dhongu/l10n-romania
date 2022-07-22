# ©  2015-2021 Deltatech
# See README.rst file on addons root folder for license details

import json
import logging

from odoo import SUPERUSER_ID, http
from odoo.http import request

_logger = logging.getLogger(__name__)


class DUKController(http.Controller):
    @http.route("/duk_integrator", methods=["POST"], auth="none", csrf=False)
    def DUKIntegrator(self, **post):
        _logger.info("Beginning DUK integrator")
        _logger.info(post)

        duk = request.env["duk.integrator"]
        duk = duk.with_user(SUPERUSER_ID).sudo()

        data_file = request.httprequest.data

        duk = duk.create(
            {
                "data_file": data_file,
                "file_type": post.get("file_type"),
                "usage": post.get("usage", "v"),
                "local": True,
            }
        )

        duk.do_check_xml()

        return json.dumps(
            {
                "error": duk.error,
                "output": duk.output,
            }
        )
