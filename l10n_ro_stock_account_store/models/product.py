# Copyright (C) 2024 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "l10n.ro.mixin"]

    def _get_product_accounts(self):
        accounts = super()._get_product_accounts()

        return accounts
