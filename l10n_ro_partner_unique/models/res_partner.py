# Copyright (C) 2015 Forest and Biomass Romania
# Copyright (C) 2020 NextERP Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _get_vat_nrc_constrain_domain(self):
        domain = [
            ("parent_id", "=", False),
            ("vat", "=", self.vat),
            "|",
            ("nrc", "=", self.nrc),
            ("nrc", "=", False),
        ]
        return domain

    @api.constrains("vat", "nrc")
    def _check_vat_nrc_unique(self):
        for record in self:
            if record.vat and record.nrc:
                domain = record._get_vat_nrc_constrain_domain()
                results = self.env["res.partner"].search(domain)
                if len(results) > 1:
                    raise ValidationError(_("The VAT and NRC pair (%s, %s) must be unique!") % (record.vat, record.nrc))
