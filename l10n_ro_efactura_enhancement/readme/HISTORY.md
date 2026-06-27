## 18.0.0.3.0 (2026-06-26)

- **Protecție anti-duplicat la trimiterea în SPV.** O factură putea ajunge de
  două ori la ANAF (două `index_incarcare` pentru același număr de factură),
  fie printr-o dublă declanșare (cron de auto-send + „Send & Print" manual
  aproape simultan), fie după un timeout la răspunsul ANAF (încărcarea ajungea
  la SPV, dar Odoo nu reținea indexul și o re-trimitea). Două măsuri:
  - **Gardă de idempotență** în `_l10n_ro_edi_send_invoice`: dacă factura are
    deja un document `invoice_sent`/`invoice_validated` sau un index de
    încărcare, trimiterea este evitată (mesaj în chatter), pentru a nu crea un
    al doilea upload la ANAF (API-ul `upload` nu este idempotent).
  - **Tratarea timeout-ului** (`requests.Timeout`, inclusiv `ReadTimeout`, care
    în core nu era prins): trimiterea nu mai e marcată drept eroare
    re-trimitabilă; factura este marcată `l10n_ro_edi_send_uncertain` și
    **exclusă din cronul de auto-send**, cu un mesaj care cere verificare
    manuală în SPV. Un buton pe factură debifează marcajul după clarificare.



- **No more double customer email.** Previously an invoice could be emailed
  twice: once by the operator's manual "Send & Print" at posting time, and
  again by the SPV fetch-status cron after the SPV validated it (the
  `l10n_ro_spv_validated_email_sent` flag was only set by the cron, so a manual
  send went unnoticed). `account.move.send._send_mails` is now extended to set
  the flag for every invoice actually emailed to the customer through any path,
  so the post-validation cron skips invoices the operator already emailed. The
  SPV upload path uses `sending_methods={"manual"}` (no email), so cron-only
  invoices are still emailed once after validation.

## 18.0.0.2.15 (2026-06-24)

- **Foreign-customer invoices are no longer uploaded to the SPV via Send &
  Print.** The core `_is_ro_edi_applicable` only checks the issuing company is
  Romanian (`country_code == 'RO'`), so the standard Send & Print wizard would
  upload invoices issued to foreign customers (e.g. Shopify HU) to the SPV and
  later re-email the customer after validation. The check now also excludes
  invoices whose commercial partner has a country explicitly set to something
  other than RO, matching the existing filter on the auto-send cron and
  `action_send_to_spv_only`. Partners without a country are left untouched to
  avoid regressions on domestic B2C invoices.

## 18.0.0.2.14 (2026-06-18)

- **SPV cron report no longer falls back to the company email.** Recipients
  come exclusively from `l10n_ro_spv_cron_report_email`; when that field is
  empty the report is simply not sent (previously it fell back to the company
  email). Help texts and the settings view were updated accordingly.

## 18.0.0.2.13 (2026-06-09)

- **SPV cron report email** now uses the standard `mail.template` mechanism
  (QWeb body + standard Odoo email layout) instead of a raw `mail.mail`. The
  report is branded and easy to customize, with the per-run statistics passed
  through the rendering context. The report is still sent to the accounting
  team regardless of the "send to SPV without email" company setting.

## 18.0.0.2.12 (2026-06-09)

- **Customer invoice email is now sent only after SPV validation**, not at
  upload time. Previously, a rejected invoice retried by the auto-send cron
  emailed the customer again on every retry.
  - The auto-send cron always uploads with `sending_methods={"manual"}` (no
    email).
  - The fetch-status cron sends the customer email once the invoice reaches
    `invoice_validated`, guarded by the new `l10n_ro_spv_validated_email_sent`
    flag (idempotent; a failed email retries on a later run). The already
    validated invoice is not re-uploaded to the SPV.
  - Partners whose sending method is not email are flagged as done without
    emailing.
- Added a post-migration that flags already-uploaded invoices as handled, so
  the new flow does not retroactively email customers for invoices already sent
  under the old behavior.

## 18.0.0.2.11 (2026-06-09)

- **SPV cron report** now splits the success bucket into two rows: "Validate de
  SPV" (`invoice_validated`, confirmed) and "Trimise în SPV — în așteptare
  validare" (`invoice_sent`, uploaded but not yet validated). `invoice_sent`
  only means the XML was uploaded; the SPV can still reject it asynchronously.

## 18.0.0.2.10 (2026-06-09)

- **Fixed SPV auto-send cron crash** (`'bool' object has no attribute 'get'`).
  The cron called `_generate_and_send_invoices` with `from_cron=True`, a branch
  that reads `move.sending_data` (only populated by the Send & Print wizard).
  Replaced with `allow_raising=False`, which keeps the "log on chatter, don't
  abort the batch" behavior without touching `sending_data`.
- The automatic send is now attributed to **OdooBot** instead of the user
  running the cron.
- **Settings layout fix**: the "eFactura SPV" section uses a `<block>` instead
  of a raw `<div>`/`<h2>` so it aligns with the standard Settings grid; added
  `string`/`help` on the settings.
