## 18.0.0.3.3 (2026-07-01)

- **Emailul este complet separat de trimiterea facturilor în SPV.** Cron-ul de
  trimitere (`E-Factura: Send TO SPV`) rula fetch status → trimitere SPV →
  email de raport → reprogramare într-o singură tranzacție. Când emailul de
  raport eșua cu `SerializationFailure: could not serialize access due to
  concurrent update` (conflict pe `account_move` cu importul din marketplace,
  declanșat de `flush`-ul din `unlink`-ul mailului cu `auto_delete`), se făcea
  rollback la **tot**: la trimiterile efective (facturile reapăreau ca „de
  trimis") și la reprogramarea cron-ului (lanțul de auto-trimitere se rupea,
  lăsând restul loturilor netrimise ore întregi).
  - Trimiterile în SPV se **comit imediat** după `_generate_and_send_invoices`,
    înainte de orice pas de email (fără commit în modul test).
  - Emailul de raport este izolat în `savepoint` + `try/except` (eșecul se
    loghează, nu oprește cron-ul) și trecut pe livrare prin coada de mail
    (`force_send=False`), scoțând SMTP-ul și `unlink`-ul cu `auto_delete` din
    tranzacția cron-ului.
  - Emailul către client (după validare SPV, în cron-ul de fetch) este izolat
    la fel: un eșec de email nu mai poate da rollback la statusurile citite din
    SPV, iar factura se reia la rularea următoare (flag-ul
    `l10n_ro_spv_validated_email_sent` rămâne nesetat).

## 18.0.0.3.2 (2026-06-30)

- **Permite retrimiterea facturilor respinse de ANAF.** Garda de idempotență
  bloca retrimiterea oricărei facturi care avea `l10n_ro_edi_index` setat. Însă
  indexul rămâne pe factură și după ce ANAF *respinge* încărcarea (fluxul de
  fetch/download din core trece documentul pe `invoice_sending_failed`, dar nu
  șterge indexul). Astfel, o factură respinsă și apoi corectată nu mai putea fi
  retrimisă. Acum indexul rămas este tratat ca risc de duplicat doar când NU
  există un document `invoice_sending_failed` care să-l anuleze: o încărcare
  respinsă este „moartă" la ANAF, deci factura corectată trebuie să fie
  retrimisibilă. Modificat în `_l10n_ro_edi_send_invoice`.

## 18.0.0.3.1 (2026-06-30)

- **Trunchiere referință comandă (BT-13) la 200 de caractere.** Pe facturile de
  revânzare cu multe comenzi consolidate, câmpul „Referință client" (`ref`)
  putea depăși 200 de caractere și ajungea ca atare în `cac:OrderReference/cbc:ID`
  (BT-13), iar ANAF respingea transmiterea cu eroarea **BR-RO-L200** („Numărul
  maxim permis de caractere pentru Referința comenzii (BT-13) este 200").
  Acum BT-13 este limitat la 200 de caractere la generarea XML-ului, simetric
  cu limitarea deja existentă pe `cbc:SalesOrderID` (BT-14). Modificat în
  `_add_invoice_header_nodes` (CIUS-RO) și `_ubl_add_order_reference_node` (BIS3).

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
  - **Notă:** această protecție este un *backport* al comportamentului **nativ
    din Odoo 19 standard** (`l10n_ro_edi`): pe 19 există deja starea
    `invoice_not_indexed`, garda de pre-send „already sent" și recuperarea prin
    „Synchronise to SPV". Pe Odoo 19 dezvoltarea de față nu mai este necesară
    pentru cazul duplicatelor.



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
