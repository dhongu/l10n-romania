# ©  2024-now Dan Stoica <danila(@)terrabit(.)ro
# See README.rst file on addons root folder for license details

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    l10n_ro_label_length = fields.Integer(
        string="Desc. length", compute="_compute_label_length"
    )
    l10n_ro_product_length = fields.Integer(
        string="Prod. length", compute="_compute_label_length"
    )

    @api.onchange("product_id", "name")
    def _compute_label_length(self):
        for line in self:
            if line.name:
                line.l10n_ro_label_length = len(line.name)
            else:
                line.l10n_ro_label_length = 0
            if line.product_id:
                line.l10n_ro_product_length = len(line.product_id.display_name)
            else:
                line.l10n_ro_product_length = 0

    @api.depends("product_id", "product_uom_id")
    def _compute_price_unit(self):
        """
        Anuleaza functia compute daca factura este de furnizor si are tranzactie edi (este de pe ANAF)
        """
        is_supplier_from_anaf = True
        for line in self:
            if (
                line.move_id.move_type not in ["in_invoice", "in_refund"]
                or not line.move_id.l10n_ro_edi_download
            ):
                is_supplier_from_anaf = False
        if not is_supplier_from_anaf:
            super()._compute_price_unit()
