## 19.0.0.3.22 (2026-07-29)

- **Răspunsurile neașteptate de la SPV nu mai crapă interfața.** ANAF răspunde
  frecvent cu HTTP 200 și un corp care nu este payload-ul așteptat (JSON de
  eroare la limita de apeluri sau `id_incarcare` inexistent, text simplu, pagină
  HTML de gateway în mentenanță). `make_efactura_request` din `l10n_ro_edi`
  tratează doar codurile 204/400/401/403/500, așa că un asemenea corp ajungea la
  apelanți și crăpa cu `lxml.etree.XMLSyntaxError: Start tag expected, '<' not
  found` pe *Fetch status* (`stareMesaj`), cu `BadZipFile` pe `descarcare` sau
  cu un PDF corupt salvat de la `transformare`.
  - Se validează primii octeți ai răspunsului față de payload-ul așteptat pe
    endpoint (XML pe `upload`/`uploadb2c`/`stareMesaj`, ZIP pe `descarcare`,
    PDF pe `transformare`, JSON pe listele de mesaje).
  - Când răspunsul nu poate fi payload-ul așteptat, se întoarce `{'error': ...}`
    cu mesajul de eroare ANAF extras din JSON (sau un extras curățat din corpul
    brut), care apare în chatter-ul facturii și în log — deci și diagnosticul
    devine posibil, fără RPC_ERROR.
  - Endpoint-urile necunoscute nu sunt validate, ca să nu blocăm fluxuri noi.
  - Acoperă și copia funcției din `l10n_ro_message_spv`. Doar cod Python, nu
    necesită actualizarea modulului — este suficient un restart.

## 19.0.0.3.21 (2026-07-29)

Port of the 18.0 fix (18.0.0.2.15 / 18.0.0.2.16) that was never forwarded to
19.0: the 19.0 catch-up port of this module predates it.

- **Foreign-customer invoices are no longer offered for SPV upload in "Send &
  Print".** The core `_is_ro_edi_applicable` only checks the issuing company is
  Romanian (`country_code == 'RO'`), so invoices issued to foreign customers
  (e.g. the HU series of a Romanian company) were uploaded to the SPV. The
  check now also excludes invoices whose commercial partner has a country
  explicitly set to something other than RO, matching the filter already
  present on the auto-send cron and on `action_send_to_spv_only`. Partners
  without a country are left untouched to avoid regressions on domestic B2C
  invoices. In 19.0 the wizard builds its checkboxes from
  `_get_default_extra_edis`, so the "Send E-Factura to SPV" checkbox no longer
  shows up at all for those invoices.
- **No more double customer email.** An invoice could be emailed twice: once by
  the operator's manual "Send & Print" at posting time, and again by the
  validated-invoice cron after the SPV validated it (the
  `l10n_ro_spv_validated_email_sent` flag was only set by the cron, so a manual
  send went unnoticed). `account.move.send._send_mails` now sets the flag for
  every invoice actually emailed to the customer through any path. The SPV
  upload path uses `sending_methods={"manual"}` (no email), so cron-only
  invoices are still emailed once, after validation.

## 19.0.0.3.20 (2026-07-28)

- **Import SPV: linia se recalculează din `cbc:LineExtensionAmount` când
  furnizorul completează greșit `cac:Price/cbc:BaseQuantity`.** Core-ul Odoo
  derivă prețul unitar din BT-146 / BT-149 și suprascrie astfel valoarea
  calculată din BT-131. Când furnizorul transmite `BaseQuantity` egal cu
  `InvoicedQuantity` în loc de 1 — tipar întâlnit la mai multe programe de
  facturare — prețul unitar rezultat este de `InvoicedQuantity` ori mai mic
  (ex. 0,00315 lei/m în loc de 1,26 lei/m), iar diferența ajunge tăcut într-o
  linie „Rounding" **fără TVA**. Factura intră cu total corect, dar cu **TVA
  subevaluat**, fără nicio eroare afișată.
  - BT-131 (`cbc:LineExtensionAmount`) este câmp obligatoriu și reprezintă
    valoarea autoritativă a liniei, în timp ce BT-149 este opțional și
    servește doar la exprimarea prețului. Când cele două se contrazic, linia
    se recalculează din BT-131.
  - Se compară subtotalul importat cu BT-131 și se corectează **doar** peste
    toleranța de rotunjire dedusă din numărul de zecimale al BT-146; abaterile
    mici, legitime (preț unitar transmis rotunjit la 2 zecimale), rămân pe
    seama liniei de rotunjire din core.
  - Fiecare linie corectată este semnalată în logurile importului, deci apare
    în chatter-ul facturii.
  - Doar cod Python, nu necesită actualizarea modulului.

## 19.0.0.3.18 (2026-07-03)

- **Opțiune de dezactivare a importului automat de facturi primite din SPV.**
  Cron-ul nativ `E-Factura: Synchronize with ANAF` creează automat ciorne de
  facturi de la furnizori din mesajele primite în SPV (funcție nouă în Odoo 19,
  inexistentă pe 18). S-a adăugat un câmp per companie `l10n_ro_edi_no_auto_bill`
  (Setări → Contabilitate → secțiunea „eFactura SPV") care, când e activat, sare
  peste crearea automată a acestor facturi.
  - Implicit **dezactivat** (`False`): comportamentul nativ rămâne neschimbat;
    activarea este o alegere explicită per companie.
  - Este gardată **doar** metoda dedicată `_l10n_ro_edi_process_bill_messages`;
    procesarea răspunsurilor pentru facturile trimise (acceptat/refuzat) și
    curățarea facturilor neindexate din același cron rămân neatinse.

## 19.0.0.3.17 (2026-07-03)

- **Descrierea nu mai apare dublată în Description + Name.** Când linia avea o
  descriere suplimentară, același text era pus atât în `cbc:Description` cât
  și în `cbc:Name`, rezultând două tag-uri identice. Comportamentul rămâne cel
  al parametrului (descrierea liniei merge în `cbc:Name`), dar tag-ul
  `cbc:Description` se omite când ar fi identic cu `cbc:Name` — rămâne prezent
  doar când descrierea depășește 100 de caractere, ca să poarte textul complet
  (Name e trunchiat la 100, Description la 200). Doar cod Python, nu necesită
  actualizarea modulului.

## 19.0.0.3.16 (2026-07-03)

- **Tag-ul `cbc:Description` este omis când linia nu are descriere proprie.**
  Cu `efactura.use_line_description` activ, dacă numele liniei este identic cu
  `display_name`-ul produsului (linie generată automat, fără text suplimentar),
  în XML ajungea numele produsului (inclusiv codul `[COD]`) ca descriere.
  `get_description` returnează acum doar descrierea suplimentară a liniei
  (numele liniei fără numele produsului), iar când aceasta este goală nodul
  `cbc:Description` (opțional, BT-154) este pus pe `None` și tag-ul nu mai
  apare deloc în XML. `cbc:Name` rămâne numele produsului.
  - Eliminat și fallback-ul pe `product.name` la descrierea implicită
    (independent de parametru): numele produsului nu mai este duplicat în
    Description — el există deja în `cbc:Name` și în
    `cac:SellersItemIdentification`.
  - Doar cod Python, nu necesită actualizarea modulului.

## 19.0.0.3.15 (2026-07-01)

- **Emailul către client este acum un cron separat.** Trimiterea emailului
  pentru facturile validate de SPV era executată în interiorul cron-ului de
  fetch (`_cron_l10n_ro_edi_fetch_status`). Munca este însă complet condusă de
  query și idempotentă (facturi `invoice_validated` cu
  `l10n_ro_spv_validated_email_sent = False`), deci a fost mutată într-un cron
  propriu, `E-Factura: Trimite email facturi validate`
  (`_cron_l10n_ro_spv_send_validated_emails`, rulează la 15 minute).
  - Emailul rulează independent de fluxul de citire/scriere SPV, pe orarul lui.
  - Fiecare companie este izolată în propriul `savepoint`: un eșec la o companie
    nu oprește emailurile pentru celelalte și lasă flag-ul nesetat, deci se reia
    la rularea următoare.
  - Necesită actualizarea modulului (`-u`) pentru a instala noul `ir.cron`.

## 19.0.0.3.14 (2026-07-01)

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

## 19.0.0.3.13 (2026-06-30)

- **Trunchiere referință comandă (BT-13) la 200 de caractere.** Pe facturile de
  revânzare cu multe comenzi consolidate, câmpul „Referință client" (`ref`)
  putea depăși 200 de caractere și ajungea ca atare în `cac:OrderReference/cbc:ID`
  (BT-13), iar ANAF respingea transmiterea cu eroarea **BR-RO-L200** („Numărul
  maxim permis de caractere pentru Referința comenzii (BT-13) este 200").
  Acum BT-13 este limitat la 200 de caractere la generarea XML-ului, simetric
  cu limitarea deja existentă pe `cbc:SalesOrderID` (BT-14), în
  `_ubl_add_order_reference_node`.
