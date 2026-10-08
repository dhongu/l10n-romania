Registrul de casă ca **document numerotat**, cod 14-4-7A (OMFP 2634/2015).

**Funcționalități:**

- un document per (casierie, zi), cu numerotare proprie prin secvență, unic pe dată și jurnal;
- sold inițial preluat automat din ziua precedentă și sold final calculat;
- mișcările zilei — încasări, plăți, explicația operațiunii și partenerul;
- chatter și activități pe document, pentru urmărire și responsabil;
- tipărire în forma cerută de formular.
- **închiderea zilei**: soldul se îngheață, iar contul casei nu mai primește înregistrări în ziua
  închisă sau înaintea ei până la redeschiderea explicită a registrului. Corecțiile pentru o zi închisă se fac prin
  stornare sau notă de corecție datată în ziua curentă. Nu se închide o zi din viitor sau cu sold negativ.
- **monetarul**: numărarea fizică a numerarului pe cupiuri (bancnote și monede), comparată cu
  soldul contului casei, cu diferența afișată ca plus sau lipsă și tipărită în „Monetar – situația
  numerarului pe cupiuri”, semnată de casier și de cel care verifică. Se poate face obligatoriu la
  închiderea zilei, per casierie.

## Monetarul

Butonul **Numără numerarul** de pe registru adaugă câte un rând pentru fiecare cupiură activă a
monedei casieriei (leu și euro sunt livrate cu modulul; alte valute se adaugă din *Contabilitate >
Configurare > Cupiuri numerar*). Casierul completează numărul de bucăți; registrul arată numerarul
numărat și diferența față de soldul scriptic: pozitivă = plus de casă, negativă = lipsă.

Monetarul este un document de control intern al casieriei; forma și periodicitatea numărării le
stabilește conducerea entității prin procedurile proprii (inclusiv cele de inventariere, OMFP
1802/2014, pct. 83 alin. (2)). Efect contabil are doar diferența, înregistrată pe baza constatării:

| Situație | Notă contabilă |
| --- | --- |
| Plus de casă | 5311 = 7588 |
| Lipsă neimputabilă | 6588 = 5311 (65882, nedeductibilă) |
| Lipsă imputată casierului (salariat) | 4282 = 5311 |
| Diferență în curs de clarificare | 473 = 5311 (lipsă) / 5311 = 473 (plus) |

**Înregistrează diferența** deschide operațiunea de casă precompletată cu sensul, suma și contul
implicit: contul de profit, respectiv de pierdere, al jurnalului de casă; dacă jurnalul nu le are,
pe planul de conturi RO 7588 pentru plus și 65882 pentru lipsă, altfel contul de diferențe de
numerar al companiei. Contabilul poate alege alt cont (473, 4282). Modulul nu impută automat
lipsa: recuperarea de la salariat se face pe baza unei note de constatare și evaluare a pagubei,
prin acordul părților și în limita a 5 salarii minime brute (Codul muncii, art. 254 alin. (3)–(4)),
iar în lipsa acordului pe cale judecătorească. Lipsa de numerar neimputabilă este tratată de
regulă ca cheltuială nedeductibilă, fiind efectuată în afara scopului activității economice (Codul
fiscal, art. 25 alin. (1)); încadrarea finală rămâne la aprecierea consultantului fiscal.

Cu bifa **Monetar obligatoriu la închiderea zilei** pe jurnalul de casă, ziua se închide doar după
numărare și doar dacă numerarul numărat este egal cu soldul contului casei. După închidere,
monetarul nu se mai modifică până la redeschiderea zilei.

Soldurile și mișcările se citesc din notele contabile postate de pe contul de casă al
jurnalului (`default_account_id`, ex. 5311).

## Care variantă alegeți

Suita oferă două forme de registru de casă, cu **aceleași cifre**, citite din aceleași linii
contabile. Diferă ce puteți face cu ele:

- **acest modul** produce **documentul**: numerotat, cu o filă per zi, arhivabil și tipăribil în
  forma formularului. Este varianta pentru evidența care se păstrează și se prezintă la control.
  Merge pe Odoo Community.
- **`l10n_ro_cash_register_report`** (suita `l10n_ro_ent`) produce **raportul**: interval de mai
  multe zile, filtru de jurnale, derulare pe niveluri, drill-down la nota contabilă și export
  PDF/XLSX. Este varianta pentru verificare și analiză, dar **nu numerotează** nimic. Cere
  Odoo Enterprise (`account_reports`).

Cele două nu se exclud și pot fi instalate împreună. Când sunt amândouă, folosiți documentul de
aici pentru evidența oficială și raportul pentru verificări pe perioade.
