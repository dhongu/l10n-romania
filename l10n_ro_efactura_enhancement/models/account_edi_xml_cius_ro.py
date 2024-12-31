# ©  2024 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import models


class AccountEdiXmlUBLRO(models.AbstractModel):
    _inherit = "account.edi.xml.ubl_ro"

    def _export_invoice_vals(self, invoice):
        vals_list = super()._export_invoice_vals(invoice)

        return vals_list

    def _export_invoice_constraints(self, invoice, vals):
        partner = invoice.commercial_partner_id

        if partner.country_id.code == "RO" and not partner.is_company:
            if not partner.vat:
                partner.with_context(no_vat_validation=True).write({"vat": "0000000000000"})
            if not partner.street:
                partner.write({"street": "Principala"})

            if partner.state_id and partner.state_id.code == "B":
                if not partner.city:
                    partner.write({"city": "SECTOR1"})
                if "SECTOR" not in partner.city.upper():
                    partner.write({"city": "SECTOR1"})

        constraints = super()._export_invoice_constraints(invoice, vals)

        return constraints
