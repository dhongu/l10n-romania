import logging
from datetime import timedelta

import requests

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

    # Tracks whether the customer invoice email has already been sent, so it is
    # sent at most once. It is set both when the SPV fetch-status cron emails
    # the invoice after validation AND when the invoice is emailed through
    # account.move.send by any other path (notably the operator's manual
    # "Send & Print"). This prevents a double email: one manual send by the
    # operator and another by the cron after the SPV validates the invoice.
    l10n_ro_spv_validated_email_sent = fields.Boolean(
        string="Email factură trimis după validare SPV",
        copy=False,
        default=False,
    )

    # Set when a send to the SPV ended in an uncertain state (typically a
    # response timeout from ANAF): the upload MAY have reached the SPV even
    # though Odoo did not record an index. Such an invoice must NOT be
    # re-sent automatically by the auto-send cron, otherwise a second upload
    # is created at ANAF for the same invoice (duplicate). It requires a
    # manual check in the SPV and is cleared once resolved.
    l10n_ro_edi_send_uncertain = fields.Boolean(
        string="Trimitere SPV incertă (verificare manuală)",
        copy=False,
        default=False,
        help="Trimiterea către SPV s-a încheiat fără răspuns de la ANAF "
        "(timeout). Încărcarea poate să fi ajuns totuși în SPV. Factura nu se "
        "retrimite automat — verificați în SPV și debifați după clarificare.",
    )

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
                    to_email._l10n_ro_spv_send_validated_email()

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
                # Skip invoices whose previous send ended in an uncertain state
                # (response timeout): the upload may have reached the SPV, so an
                # automatic re-send would create a duplicate at ANAF. These need
                # a manual check in the SPV before being sent again.
                ("l10n_ro_edi_send_uncertain", "=", False),
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
                shown += _(" … (+%s)") % (len(names) - limit)
            return shown

        rows = [
            (_("Validate de SPV"), len(stats["validated"]), _names(stats["validated"])),
            (
                _("Trimise în SPV — în așteptare validare"),
                len(stats["pending"]),
                _names(stats["pending"]),
            ),
            (_("Eșuate la această rulare"), len(stats["failed_now"]), _names(stats["failed_now"])),
            (_("Reîncercări (eșuaseră anterior)"), len(stats["retrying"]), _names(stats["retrying"])),
            (
                _("Sărite — reîncercări epuizate (necesită atenție)"),
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
        template.with_context(
            spv_rows=rows,
            spv_total=len(stats["attempted"]),
            spv_run=fields.Datetime.to_string(now),
        ).sudo().send_mail(
            company.id,
            force_send=True,
            email_values={
                "email_to": recipients,
                "email_from": company.email or company.partner_id.email or recipients,
                "auto_delete": True,
            },
        )
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
        self.ensure_one()

        # Idempotency guard: never re-upload an invoice that already has a
        # successful upload in the SPV. The ANAF 'upload' endpoint is not
        # idempotent (each call creates a new index_incarcare for the same
        # invoice), so a second trigger (cron + manual Send & Print at almost
        # the same time, or a retry) would create a duplicate at ANAF.
        already_sent = self.l10n_ro_edi_document_ids.filtered(
            lambda d: d.state in ("invoice_sent", "invoice_validated")
        )
        if already_sent or self.l10n_ro_edi_index:
            index = self.l10n_ro_edi_index or already_sent[:1].key_loading
            _logger.warning(
                "E-Factura %s deja încărcată în SPV (index=%s); se evită re-trimiterea.",
                self.name,
                index,
            )
            self.message_post(
                body=_(
                    "Trimiterea către SPV a fost evitată: factura are deja o "
                    "încărcare în SPV (index de încărcare %s). Nu se retrimite, "
                    "pentru a nu crea un duplicat la ANAF.",
                    index,
                )
            )
            return

        try:
            res = super(AccountMove, self.with_context(active_id=self.id))._l10n_ro_edi_send_invoice(xml_data)
        except requests.Timeout:
            # Response timeout from ANAF: the upload MAY have reached the SPV
            # even though we did not receive the index. We must NOT mark this as
            # a retriable failure (the auto-send cron would re-upload it and
            # create a duplicate). Flag it for a manual SPV check instead.
            self.l10n_ro_edi_send_uncertain = True
            _logger.warning(
                "Timeout la trimiterea E-Factura %s; marcată pentru verificare manuală în SPV.",
                self.name,
            )
            self.message_post(
                body=_(
                    "Trimiterea către SPV a expirat (timeout) fără răspuns de la "
                    "ANAF. Încărcarea poate să fi ajuns totuși în SPV. Factura NU "
                    "se retrimite automat — verificați în SPV dacă a fost primită: "
                    "dacă da, completați indexul de încărcare; dacă nu, debifați "
                    "„Trimitere SPV incertă” și reluați trimiterea."
                )
            )
            return
        # A successful send resolves any previous uncertain state.
        if self.l10n_ro_edi_send_uncertain:
            self.l10n_ro_edi_send_uncertain = False
        return res

    def action_l10n_ro_edi_clear_send_uncertain(self):
        """Clear the 'uncertain send' flag after a manual SPV check, so the
        invoice can be picked up again by the normal send flow."""
        self.write({"l10n_ro_edi_send_uncertain": False})

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
