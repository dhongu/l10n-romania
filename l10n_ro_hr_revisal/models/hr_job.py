from odoo import fields, models


class HrJob(models.Model):
    _inherit = "hr.job"

    code_cor = fields.Char(help="Classification code of occupations")
