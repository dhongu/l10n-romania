import logging
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Maximum number of automatic SPV send retries for an invoice that keeps
# failing. Each failed attempt creates a new ``invoice_sending_failed``
# document, so we use that count as the natural retry counter.
MAX_SPV_SEND_RETRIES = 3


class AccountMove(models.Model):
    _inherit = "account.move"

    # l10n_ro_edi_state = fields.Selection( selection_add=[ ('invoice_sending_failed', 'Error')])

    def check_partner(self, partner):
        """Check if the partner has a country set, raise UserError if not."""
        if not partner.country_id:
            raise UserError(_("You can not post invoice without country for partner: %s") % partner.name)
        if partner.country_id.code == "RO":
            if not partner.state_id:
                raise UserError(_("You can not post invoice without state for partner: %s") % partner.name)
            if not partner.city:
                raise UserError(_("You can not post invoice without city for partner: %s") % partner.name)
            if not partner.street:
                raise UserError(_("You can not post invoice without street for partner: %s") % partner.name)

    def action_post(self):
        for move in self:
            if move.move_type in ["out_invoice", "out_refund"]:
                move.check_partner(move.partner_id)
                move.check_partner(move.partner_shipping_id)
        return super().action_post()

    def _need_ubl_cii_xml(self, ubl_cii_format=None):
        res = super()._need_ubl_cii_xml(ubl_cii_format)

        return res

    def _cron_l10n_ro_edi_fetch_status(self, limit=20, days=30, delay_days=0):
        need_retrigger = False
        _logger.info("⏱️ Cron job for fetch status from SPV")
        domain = [("l10n_ro_edi_access_token", "!=", False)]
        ro_companies = self or self.env["res.company"].sudo().search(domain)
        for company in ro_companies:
            domain = [
                ("move_type", "in", ("out_invoice", "out_refund")),
                ("state", "=", "posted"),
                ("date", "<", fields.Date.today() - timedelta(days=delay_days)),
                ("date", ">=", fields.Date.today() - timedelta(days=days + delay_days)),
                ("l10n_ro_edi_state", "=", "invoice_sent"),
                ("company_id", "=", company.id),
            ]

            invoices = self.search(domain, limit=limit, order="date")

            if invoices:
                invoices_name = invoices.mapped("name")
                _logger.info(f"🔍 Fetch status for invoices: {invoices_name}")
                invoices._l10n_ro_edi_fetch_invoice_sent_documents()
                need_retrigger = True
            else:
                _logger.info("No invoices to fetch status")

        if need_retrigger:
            at = fields.Datetime.now() + timedelta(minutes=2)
            # asteapata ca sa se termine trimiterea facturilor in SPV prin job-ul de mai sus
            _logger.info("⏳ Retrigger cron scheduled in 2 minutes")
            self.env.ref("l10n_ro_efactura_enhancement.ir_cron_l10n_ro_edi_fetch_status")._trigger(at)

    def _cron_l10n_ro_edi_auto_send(self, limit=20, days=30, delay_days=0):
        """Trimiterea automata a facturilor din ziua precedenta in SPV"""
        _logger.info("⏱️ Cron job for sending invoices to SPV")

        need_retrigger = False
        self._cron_l10n_ro_edi_fetch_status(limit=limit, days=days, delay_days=delay_days)

        domain = [("l10n_ro_edi_access_token", "!=", False)]
        ro_companies = self or self.env["res.company"].sudo().search(domain)
        for company in ro_companies:
            # Both never-sent invoices and previously failed ones have
            # l10n_ro_edi_state = False (the computed state only reflects
            # 'invoice_sent'/'invoice_validated'). We select them together and
            # filter out failed invoices that exceeded the retry limit, so a
            # transient failure is retried automatically on the next runs.
            domain = [
                ("move_type", "in", ("out_invoice", "out_refund")),
                ("state", "=", "posted"),
                ("date", "<", fields.Date.today() - timedelta(days=delay_days)),
                ("date", ">=", fields.Date.today() - timedelta(days=days + delay_days)),
                ("commercial_partner_id.country_id.code", "=", "RO"),
                ("l10n_ro_edi_state", "=", False),
                ("company_id", "=", company.id),
            ]

            candidates = self.search(domain, order="date desc")

            # Skip invoices whose send already failed MAX_SPV_SEND_RETRIES times
            # to avoid hammering SPV with the same broken document forever.
            def _within_retry_limit(invoice):
                failed = invoice.l10n_ro_edi_document_ids.filtered(lambda d: d.state == "invoice_sending_failed")
                return len(failed) < MAX_SPV_SEND_RETRIES

            exhausted = candidates.filtered(lambda inv: not _within_retry_limit(inv))
            if exhausted:
                _logger.info(
                    "❌ Invoices skipped (retry limit %d reached): %s",
                    MAX_SPV_SEND_RETRIES,
                    exhausted.mapped("name"),
                )
            candidates = candidates - exhausted

            retrying = candidates.filtered(
                lambda inv: inv.l10n_ro_edi_document_ids.filtered(lambda d: d.state == "invoice_sending_failed")
            )
            if retrying:
                _logger.info("🔁 Retrying previously failed invoices: %s", retrying.mapped("name"))

            _logger.info(f"📤 Invoices to send to SPV: {candidates.mapped('name')}")

            if len(candidates) > limit:
                invoices = candidates[:limit]
                need_retrigger = True
                _logger.info("🔁 More invoices to send to SPV, retriggering cron...")
            else:
                invoices = candidates

            # daca au fost deja generate PDF-uri pentru facturi, le stergem
            invoice_pdf_report_ids = invoices.mapped("invoice_pdf_report_id")
            invoice_pdf_report_ids.unlink()

            if invoices:
                invoices_name = invoices.mapped("name")
                _logger.info(f"📨 Sending invoices to SPV: {invoices_name}")
                _logger.info(f"Count of invoices to send in SPV: {len(invoices)}")

                sending_methods = {"manual"} if company.l10n_ro_spv_cron_no_email else None
                kwargs = {"sending_methods": sending_methods} if sending_methods else {}

                # Attribute the send to OdooBot instead of whoever happens to run
                # the cron, so the chatter/tracking shows a stable system author.
                odoobot = self.env.ref("base.user_root")
                kwargs["author_user_id"] = odoobot.id
                kwargs["author_partner_id"] = odoobot.partner_id.id

                # allow_raising=False: errors are logged on each move's chatter
                # instead of raising, so one broken invoice no longer aborts the
                # batch. We must NOT use from_cron=True here: that branch reads
                # move.sending_data (a Json field), which is only populated by the
                # Send & Print wizard. Since this cron sends invoices directly,
                # sending_data stays False and from_cron=True would crash with
                # "'bool' object has no attribute 'get'".
                self.env["account.move.send"]._generate_and_send_invoices(
                    invoices,
                    allow_raising=False,
                    **kwargs,
                )

            # Recompute states after the send to build the run report.
            invoices.invalidate_recordset(["l10n_ro_edi_state"])
            sent_ok = invoices.filtered(lambda inv: inv.l10n_ro_edi_state in ("invoice_sent", "invoice_validated"))
            failed_now = invoices - sent_ok
            self._l10n_ro_spv_send_cron_report(
                company,
                {
                    "candidates": candidates,
                    "attempted": invoices,
                    "sent_ok": sent_ok,
                    "failed_now": failed_now,
                    "retrying": retrying,
                    "exhausted": exhausted,
                },
            )

            if need_retrigger:
                at = fields.Datetime.now() + timedelta(minutes=5)
                # asteapata ca sa se termine trimiterea facturilor in SPV prin job-ul de mai sus
                _logger.info("⏳ Retrigger cron scheduled in 5 minutes")
                self.env.ref("l10n_ro_efactura_enhancement.ir_cron_l10n_ro_edi_auto_send")._trigger(at)

    def _l10n_ro_spv_send_cron_report(self, company, stats):
        """Send a statistics email summarizing one SPV auto-send cron run.

        Recipients come from ``company.l10n_ro_spv_cron_report_email`` (comma
        separated), falling back to the company email. Nothing is sent on a
        fully idle run (no candidates and no retry-exhausted invoices) to avoid
        empty nightly emails.
        """
        candidates = stats["candidates"]
        exhausted = stats["exhausted"]
        if not candidates and not exhausted:
            _logger.info("ℹ️ SPV cron report skipped for %s: nothing to report", company.name)
            return

        recipients = company.l10n_ro_spv_cron_report_email or company.email or company.partner_id.email
        if not recipients:
            _logger.warning(
                "⚠️ SPV cron report not sent for %s: no recipient configured "
                "(set 'Email raport cron SPV' or the company email)",
                company.name,
            )
            return

        def _names(records, limit=50):
            if not records:
                return "—"
            names = records.mapped("name")
            shown = ", ".join(names[:limit])
            if len(names) > limit:
                shown += _(" … (+%s)") % (len(names) - limit)
            return shown

        rows = [
            (_("Trimise cu succes în SPV"), len(stats["sent_ok"]), _names(stats["sent_ok"])),
            (_("Eșuate la această rulare"), len(stats["failed_now"]), _names(stats["failed_now"])),
            (_("Reîncercări (eșuaseră anterior)"), len(stats["retrying"]), _names(stats["retrying"])),
            (
                _("Sărite — reîncercări epuizate (necesită atenție)"),
                len(exhausted),
                _names(exhausted),
            ),
        ]
        body_rows = "".join(
            "<tr>"
            f"<td style='padding:4px 8px;border:1px solid #ddd;'>{label}</td>"
            f"<td style='padding:4px 8px;border:1px solid #ddd;text-align:right;'><b>{count}</b></td>"
            f"<td style='padding:4px 8px;border:1px solid #ddd;color:#666;'>{names}</td>"
            "</tr>"
            for label, count, names in rows
        )
        now = fields.Datetime.now()
        body = (
            f"<p>{_('Raport rulare cron trimitere e-Factura în SPV')} — "
            f"<b>{company.name}</b><br/>"
            f"{_('Data rulării')}: {fields.Datetime.to_string(now)}</p>"
            f"<p>{_('Total facturi procesate la această rulare')}: "
            f"<b>{len(stats['attempted'])}</b></p>"
            "<table style='border-collapse:collapse;font-size:13px;'>"
            f"<tr style='background:#f5f5f5;'>"
            f"<th style='padding:4px 8px;border:1px solid #ddd;text-align:left;'>{_('Categorie')}</th>"
            f"<th style='padding:4px 8px;border:1px solid #ddd;'>{_('Nr.')}</th>"
            f"<th style='padding:4px 8px;border:1px solid #ddd;text-align:left;'>{_('Facturi')}</th>"
            f"</tr>{body_rows}</table>"
        )

        mail_values = {
            "subject": _("[%s] Raport e-Factura SPV") % company.name,
            "body_html": body,
            "email_to": recipients,
            "email_from": company.email or company.partner_id.email or recipients,
            "auto_delete": True,
        }
        self.env["mail.mail"].sudo().create(mail_values).send()
        _logger.info("📧 SPV cron report sent to %s for %s", recipients, company.name)

    def action_send_to_spv_only(self):
        """Trimite facturile doar in SPV, fara email."""
        invoices = self.filtered(lambda m: m.move_type in ("out_invoice", "out_refund") and m.state == "posted")
        if not invoices:
            raise UserError(_("Nu exista facturi confirmate selectate pentru trimitere in SPV."))

        # SPV / e-Factura se aplica doar partenerilor din Romania. Excludem facturile
        # catre clienti non-RO ca sa nu fie trimise accidental in SPV.
        non_ro_invoices = invoices.filtered(lambda m: m.commercial_partner_id.country_id.code != "RO")
        if non_ro_invoices:
            _logger.info(
                "⏭️ Skipping non-RO invoices for SPV: %s",
                non_ro_invoices.mapped("name"),
            )
        invoices = invoices - non_ro_invoices
        if not invoices:
            raise UserError(_("Facturile selectate au clienti din afara Romaniei si nu pot fi trimise in SPV."))

        self.env["account.move.send"]._generate_and_send_invoices(
            invoices,
            sending_methods={"manual"},
        )

    def _l10n_ro_edi_send_invoice(self, xml_data):
        return super(AccountMove, self.with_context(active_id=self.id))._l10n_ro_edi_send_invoice(xml_data)

    @api.model
    def _cron_account_move_send(self, job_count=10):
        domain = [
            ("sending_data", "!=", False),
            ("state", "=", "posted"),
        ]
        limit = job_count + 1

        # fix pt facturile care au fost programate pentru trimitere in 17.0
        # stergem sending_data pentru facturile care nu au author_partner_id (migrate din 17.0)
        invoices = self.env["account.move"].search(domain, limit=limit)
        invalid_moves = invoices.filtered(lambda m: m.sending_data and not m.sending_data.get("author_partner_id"))
        if invalid_moves:
            _logger.info(
                "🔧 Resetting sending_data for %d invoice(s) missing 'author_partner_id': %s",
                len(invalid_moves),
                invalid_moves.mapped("name"),
            )
            invalid_moves.write({"sending_data": False})
            self.env.cr.flush()
            invalid_moves.invalidate_recordset(["sending_data"])

        return super()._cron_account_move_send(job_count=job_count)


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
