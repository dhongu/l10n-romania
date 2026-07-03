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
