# ©  2024-now Dan Stoica <danila(@)terrabit(.)ro
# See README.rst file on addons root folder for license details

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _l10n_ro_prepare_invoice_for_download(self):
        res = super()._l10n_ro_prepare_invoice_for_download()
        return res.with_delay()

    def action_post(self):
        res = super().action_post()
        errors = []
        for move in self:
            if move.move_type in ["out_invoice", "out_refund"] and move.commercial_partner_id.is_company:
                country_ro = self.env.ref("base.ro")
                parteners = list(set([move.partner_id, move.commercial_partner_id, move.partner_shipping_id]))
                for partner in parteners:
                    if not partner.country_id:
                        errors += [_("Partenerul %s nu are completata tara") % partner.name]
                    elif partner.country_id == country_ro:
                        if not partner.street:
                            errors += [_("Partenerul %s nu are completata strada") % partner.name]

                        if not partner.city:
                            errors += [_("Partenerul %s nu are completata localitatea") % partner.name]

                        state_bucuresti = self.env.ref("base.RO_B")
                        if partner.state_id == state_bucuresti and partner.city:
                            if "sector" not in partner.city.lower():
                                errors += [_("localitatea pertenerului %s trebuie sa fie de forma SectorX ") % partner.name]
                if errors:
                    errors_text = "\n".join(errors)
                    raise UserError(errors_text)
        return res

    def l10n_ro_edi_resend(self):
        self.ensure_one()

        # delete jobs if exists
        key = "ro_efactura_{}".format(self.id)
        existing = self.env["queue.job"].sudo().search([("identity_key", "=", key)])
        existing.sudo().unlink()

        edi_document_vals_list = []
        for edi_format in self.journal_id.edi_format_ids:
            is_edi_needed = self.is_invoice(include_receipts=False) and edi_format._is_required_for_invoice(self)
            if is_edi_needed:
                errors = edi_format._check_move_configuration(self)
                if errors:
                    raise UserError(_("Invalid invoice configuration:\n\n%s") % "\n".join(errors))
                # delete edi documents
                existing_edi_document = self.edi_document_ids.filtered(lambda x: x.edi_format_id == edi_format)
                existing_edi_document.sudo().unlink()
                edi_document_vals_list.append(
                    {
                        "edi_format_id": edi_format.id,
                        "move_id": self.id,
                        "state": "to_send",
                    }
                )

        # clear transaction id
        self.write({"l10n_ro_edi_transaction": False})

        # re-create edi documents
        self.env["account.edi.document"].create(edi_document_vals_list)
        self.edi_document_ids.with_delay(identity_key=key)._process_documents_web_services()
        self.env.ref("queue_job_cron_jobrunner.queue_job_cron")._trigger()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    l10n_ro_label_length = fields.Integer(string="Desc. length", compute="_compute_label_length")
    l10n_ro_product_length = fields.Integer(string="Prod. length", compute="_compute_label_length")

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
            if line.move_id.move_type not in ["in_invoice", "in_refund"] or not line.move_id.l10n_ro_edi_download:
                is_supplier_from_anaf = False
        if not is_supplier_from_anaf:
            super()._compute_price_unit()
