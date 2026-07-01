import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Maximum number of automatic SPV send retries for an invoice that keeps
# failing. Each failed attempt creates a new ``invoice_sending_failed``
# document, so we use that count as the natural retry counter.
MAX_SPV_SEND_RETRIES = 3


class AccountMove(models.Model):
    _inherit = "account.move"

    # l10n_ro_edi_state = fields.Selection( selection_add=[ ('invoice_sending_failed', 'Error')])

    # Tracks whether the customer invoice email has already been sent after the
    # SPV validated the invoice. The email is sent only once, after validation
    # (not at upload time), so a rejected/retried invoice never emails the
    # customer repeatedly.
    l10n_ro_spv_validated_email_sent = fields.Boolean(
        string="Email factură trimis după validare SPV",
        copy=False,
        default=False,
    )

    def check_partner(self, partner):
        """Check if the partner has a country set, raise UserError if not."""
        if not partner.country_id:
            raise UserError(self.env._("You can not post invoice without country for partner: %s", partner.name))
        if partner.country_id.code == "RO":
            if not partner.state_id:
                raise UserError(self.env._("You can not post invoice without state for partner: %s", partner.name))
            if not partner.city:
                raise UserError(self.env._("You can not post invoice without city for partner: %s", partner.name))
            if not partner.street:
                raise UserError(self.env._("You can not post invoice without street for partner: %s", partner.name))

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
            date_to = fields.Date.today() - timedelta(days=delay_days)
            date_from = fields.Date.today() - timedelta(days=days + delay_days)
            domain = [
                ("move_type", "in", ("out_invoice", "out_refund")),
                ("state", "=", "posted"),
                ("date", "<", date_to),
                ("date", ">=", date_from),
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

            # Persist the SPV fetch results before the (decoupled) customer
            # email step below. Emailing is isolated from the SPV read/write so
            # a mail failure (SMTP error, serialization conflict during the
            # send's flush, …) can never roll back the fetched statuses.
            if not self.env.registry.in_test_mode():
                self.env.cr.commit()  # pylint: disable=invalid-commit

            # The customer invoice email is sent only AFTER the SPV validates the
            # invoice, not at upload time. This way a rejected invoice that gets
            # retried by the auto-send cron never emails the customer over and
            # over. The l10n_ro_spv_validated_email_sent flag makes this
            # idempotent and lets a failed email retry on a later run.
            if not company.l10n_ro_spv_cron_no_email:
                to_email = self.search(
                    [
                        ("move_type", "in", ("out_invoice", "out_refund")),
                        ("state", "=", "posted"),
                        ("date", "<", date_to),
                        ("date", ">=", date_from),
                        ("l10n_ro_edi_state", "=", "invoice_validated"),
                        ("l10n_ro_spv_validated_email_sent", "=", False),
                        ("company_id", "=", company.id),
                    ],
                    limit=limit,
                )
                if to_email:
                    _logger.info(
                        "📧 Sending customer email for SPV-validated invoices: %s",
                        to_email.mapped("name"),
                    )
                    # Email is fully decoupled from the SPV flow: any failure is
                    # logged and rolled back to the savepoint (so the
                    # l10n_ro_spv_validated_email_sent flag isn't set and the
                    # invoice is retried on a later run) without aborting the cron.
                    try:
                        with self.env.cr.savepoint():
                            to_email._l10n_ro_spv_send_validated_email()
                    except Exception:
                        _logger.exception(
                            "⚠️ Customer validated-email failed for %s; SPV statuses unaffected",
                            company.name,
                        )

        if need_retrigger:
            at = fields.Datetime.now() + timedelta(minutes=2)
            # asteapata ca sa se termine trimiterea facturilor in SPV prin job-ul de mai sus
            _logger.info("⏳ Retrigger cron scheduled in 2 minutes")
            self.env.ref("l10n_ro_efactura_enhancement.ir_cron_l10n_ro_edi_fetch_status")._trigger(at)

    def _l10n_ro_spv_send_validated_email(self):
        """Send the customer invoice email for SPV-validated invoices, once.

        The invoices are already validated, so ``account.move.send`` won't
        re-upload them to the SPV (``_is_ro_edi_applicable`` requires an empty
        ``l10n_ro_edi_state``); only the email is sent. Partners whose sending
        method isn't email are flagged as done without emailing, so they aren't
        re-queried on every run. ``allow_raising=False`` keeps send errors on the
        move's chatter instead of aborting the batch.
        """
        to_mail = self.filtered(
            lambda inv: (inv.commercial_partner_id.with_company(inv.company_id).invoice_sending_method or "email")
            == "email"
        )
        if to_mail:
            self.env["account.move.send"]._generate_and_send_invoices(
                to_mail,
                sending_methods={"email"},
                allow_raising=False,
            )
        # Flag every processed invoice (emailed or skipped) so it isn't requeried.
        self.l10n_ro_spv_validated_email_sent = True

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

                # Never email the customer at upload time. The customer invoice
                # email is sent later, only after the SPV validates the invoice
                # (see _cron_l10n_ro_edi_fetch_status). This avoids emailing the
                # customer again on every retry of a rejected invoice. "manual"
                # generates/uploads to the SPV without sending any email.
                kwargs = {"sending_methods": {"manual"}}

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

            # Persist the SPV sends immediately, before the (decoupled) report
            # email below. The report is a non-critical internal notification:
            # a failure there (SMTP error, serialization conflict during the
            # mail's flush/unlink, …) must never roll back the actual uploads
            # or the cron retrigger.
            if not self.env.registry.in_test_mode():
                self.env.cr.commit()  # pylint: disable=invalid-commit

            # Recompute states after the send to build the run report.
            # NB: 'invoice_sent' only means the XML was uploaded to the SPV and is
            # awaiting validation — the SPV can still reject it later (async, via
            # the fetch-status cron). Only 'invoice_validated' is a confirmed
            # success, so we report the two separately instead of lumping them as
            # "sent successfully".
            invoices.invalidate_recordset(["l10n_ro_edi_state"])
            validated = invoices.filtered(lambda inv: inv.l10n_ro_edi_state == "invoice_validated")
            pending = invoices.filtered(lambda inv: inv.l10n_ro_edi_state == "invoice_sent")
            failed_now = invoices - validated - pending
            # Report email fully decoupled from the SPV send: isolated in a
            # savepoint so any failure is logged instead of aborting the cron
            # (the sends are already committed above).
            try:
                with self.env.cr.savepoint():
                    self._l10n_ro_spv_send_cron_report(
                        company,
                        {
                            "candidates": candidates,
                            "attempted": invoices,
                            "validated": validated,
                            "pending": pending,
                            "failed_now": failed_now,
                            "retrying": retrying,
                            "exhausted": exhausted,
                        },
                    )
            except Exception:
                _logger.exception(
                    "⚠️ SPV cron report failed for %s; sends unaffected",
                    company.name,
                )

            if need_retrigger:
                at = fields.Datetime.now() + timedelta(minutes=5)
                # asteapata ca sa se termine trimiterea facturilor in SPV prin job-ul de mai sus
                _logger.info("⏳ Retrigger cron scheduled in 5 minutes")
                self.env.ref("l10n_ro_efactura_enhancement.ir_cron_l10n_ro_edi_auto_send")._trigger(at)

    def _l10n_ro_spv_send_cron_report(self, company, stats):
        """Send a statistics email summarizing one SPV auto-send cron run.

        Recipients come exclusively from ``company.l10n_ro_spv_cron_report_email``
        (comma separated). When that field is empty the report is not sent (no
        fallback to the company email). Nothing is sent on a fully idle run (no
        candidates and no retry-exhausted invoices) to avoid empty nightly
        emails.
        """
        candidates = stats["candidates"]
        exhausted = stats["exhausted"]
        if not candidates and not exhausted:
            _logger.info("ℹ️ SPV cron report skipped for %s: nothing to report", company.name)
            return

        recipients = company.l10n_ro_spv_cron_report_email
        if not recipients:
            _logger.info(
                "ℹ️ SPV cron report not sent for %s: 'Email raport cron SPV' not set",
                company.name,
            )
            return

        def _names(records, limit=50):
            if not records:
                return "—"
            names = records.mapped("name")
            shown = ", ".join(names[:limit])
            if len(names) > limit:
                shown += self.env._(" … (+%s)", len(names) - limit)
            return shown

        rows = [
            (self.env._("Validate de SPV"), len(stats["validated"]), _names(stats["validated"])),
            (
                self.env._("Trimise în SPV — în așteptare validare"),
                len(stats["pending"]),
                _names(stats["pending"]),
            ),
            (self.env._("Eșuate la această rulare"), len(stats["failed_now"]), _names(stats["failed_now"])),
            (self.env._("Reîncercări (eșuaseră anterior)"), len(stats["retrying"]), _names(stats["retrying"])),
            (
                self.env._("Sărite — reîncercări epuizate (necesită atenție)"),
                len(exhausted),
                _names(exhausted),
            ),
        ]
        # Send through the standard mail.template mechanism (QWeb body + Odoo
        # email layout) instead of a raw mail.mail. The per-run stats are passed
        # to the template via the rendering context (exposed as ``ctx`` inside
        # the QWeb body_html). NB: this report goes to the internal accounting
        # team and is sent regardless of the company's "send without email"
        # setting, which only suppresses the customer invoice email.
        now = fields.Datetime.now()
        template = self.env.ref(
            "l10n_ro_efactura_enhancement.mail_template_l10n_ro_spv_cron_report",
            raise_if_not_found=False,
        )
        if not template:
            _logger.warning("⚠️ SPV cron report template not found; skipping report for %s", company.name)
            return
        # force_send=False: the report is queued as a mail.mail and delivered by
        # the standard email queue cron, not sent synchronously here. This keeps
        # SMTP delivery and the auto_delete unlink (whose flush was crashing the
        # SPV send transaction on concurrent account_move updates) out of the
        # SPV cron entirely — the email is fully separated from the SPV send.
        template.with_context(
            spv_rows=rows,
            spv_total=len(stats["attempted"]),
            spv_run=fields.Datetime.to_string(now),
        ).sudo().send_mail(
            company.id,
            force_send=False,
            email_values={
                "email_to": recipients,
                "email_from": company.email or company.partner_id.email or recipients,
                "auto_delete": True,
            },
        )
        _logger.info("📧 SPV cron report queued to %s for %s", recipients, company.name)

    def action_send_to_spv_only(self):
        """Trimite facturile doar in SPV, fara email."""
        invoices = self.filtered(lambda m: m.move_type in ("out_invoice", "out_refund") and m.state == "posted")
        if not invoices:
            raise UserError(self.env._("Nu exista facturi confirmate selectate pentru trimitere in SPV."))

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
            raise UserError(
                self.env._("Facturile selectate au clienti din afara Romaniei si nu pot fi trimise in SPV.")
            )

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
