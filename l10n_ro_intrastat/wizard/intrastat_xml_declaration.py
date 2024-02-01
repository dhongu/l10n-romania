# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import models


class IntrastatDeclaration(models.TransientModel):
    _name = "l10n_ro_intrastat.intrastat_xml_declaration"
    _description = "Intrastat XML Declaration"
