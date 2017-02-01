# -*- coding: utf-8 -*-
# ©  2016 Forest and Biomass Romania
# See README.rst file on addons root folder for license details

from openerp import models, fields


class res_country_state(models.Model):
    _inherit = 'res.country.state'

    order_code = fields.Char('Order Code')
