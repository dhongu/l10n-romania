# -*- coding: utf-8 -*-
# ©  2008-2019 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details




from odoo import models, fields, api, _



class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _prepare_picking(self):

        res = super(PurchaseOrder, self)._prepare_picking()
        res['origin'] = self.partner_ref or self.origin

        return res