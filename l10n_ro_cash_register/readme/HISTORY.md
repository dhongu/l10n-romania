## 19.0.1.4.0

**Nou** — monetarul casieriei: numărarea numerarului pe cupiuri.

- Cupiuri de numerar pe monedă (*Contabilitate > Configurare > Cupiuri numerar*), livrate pentru
  leu (500 lei – 1 ban) și euro (500 € – 1 cent).
- Pe registrul de casă, **Numără numerarul** adaugă câte un rând pe fiecare cupiură a monedei
  casieriei; registrul arată numerarul numărat și diferența față de soldul contului casei.
- **Înregistrează diferența** deschide operațiunea de casă precompletată: plusul pe contul de profit,
  lipsa pe contul de pierdere al jurnalului; fără conturi pe jurnal, pe planul RO 7588 și 65882 (nu
  conturile 999xxx de diferențe de numerar pe care Odoo le creează pentru companie). Contul se
  poate schimba (473 în curs de clarificare, 4282 lipsă imputată casierului).
- **Tipărește monetarul**: situația numerarului pe cupiuri, cu subtotal pe bancnote și monede,
  sold scriptic, diferență și semnături.
- Bifa **Monetar obligatoriu la închiderea zilei** pe jurnalul de casă: ziua nu se închide
  nenumărată sau cu diferență neînregistrată. Monetarul unei zile închise nu se mai modifică.
- Operațiunea de casă păstrează contul corespondent primit din context, în loc să-l înlocuiască
  mereu cu contul de transfer al companiei.

## 19.0.1.3.1

**Corectat** — numărul registrului de casă continua numerotarea notelor de casă.

Registrul și notele jurnalului de casă au același format (`CASA/2026/00001`), iar cache-ul de
secvență din `sequence.mixin` are cheia (format, jurnal), comună ambelor. Un registru creat în
aceeași tranzacție cu postarea unei note — de exemplu registrul zilei, creat automat la postarea
unei plăți pe casierie — primea următorul număr al notelor, nu pe al lui: apăreau goluri în
numerotarea registrelor. Registrul are acum cache-ul de secvență propriu.

- Mesajele de blocare la o zi închisă și de refuz al unei zile din viitor afișează data în formatul
  limbii utilizatorului (03.09.2026), nu ISO.
- Formularul registrului: moneda și compania stau sub dată și jurnal, fără golul de sub solduri
  după închidere.
- Traduceri RO pentru acțiunile „Generează registrele de casă lipsă” și „Elimină conturile de
  plăți în curs” și pentru mesajul de registru duplicat.
- Fișa consultant actualizată cu închiderea zilei, blocarea postării și redeschiderea; capturi
  regenerate.

## 19.0.1.3.0

**Nou** — închiderea zilei de casă.

- Butonul **Închide ziua** pe registrul de casă îngheață soldul final (cine, când, cât). După
  închidere, contul casei nu mai primește înregistrări datate în ziua închisă sau înaintea ei:
  postarea, trecerea în ciornă și ștergerea unei astfel de note sunt refuzate. O mișcare în urmă
  ar schimba soldul reportat în ziua închisă (OMFP 2634/2015, Anexa 1 pct. 58 lit. d) și h)).
- **Redeschide** redeschide ziua și toate zilele închise de după ea din aceeași casierie (soldul se
  reportează din zi în zi) și lasă urma în istoricul fiecărui registru.
- Pe un registru închis nu se pot schimba data, casieria sau numărul (s-ar muta blocarea fără
  urmă). Nu se poate închide o zi din viitor sau una cu sold negativ.
- Corecțiile pentru o zi închisă se fac prin stornare sau notă de corecție datată în ziua curentă.
- Un registru închis nu se poate șterge; butoanele de adăugare a încasărilor, plăților și
  operațiunilor nu mai apar pe el.

Ideea vine din modulul de casă și bancă scris de Alexandru Grecu pentru MD Trade Concept SRL,
unde închiderea doar semnala diferențele apărute după închidere; aici ea le previne.

## 19.0.1.2.2

- Own module icon in the flat style of the Terrabit modules, instead of the missing or generic one.

## 19.0.1.2.1

**Corectat** — reîmprospătarea registrului la postare cerea drepturi de contabilitate.

`_l10n_ro_cash_registers_to_refresh()` aduna registrele de reîmprospătat pe rând, prin
`registers |= register_model.sudo().search(...)`. Recordset-ul de start nu era `sudo()`, iar
unirea `|` păstrează contextul operandului din stânga — deci rezultatul final pierdea `sudo`-ul
căutării din dreapta, contrar intenției din cod. Orice utilizator fără grupul *Contabilitate/
Administrator* (de exemplu un operator de vânzări cu doar drepturi de facturare) care postează
o notă contabilă pe un cont de casă lovea de `AccessError` la reîmprospătarea soldurilor,
pentru că accesul la modelul registrului este rezervat acelui grup.

`sudo()` este acum aplicat de la recordset-ul de pornire, ca să se păstreze pe toată unirea.

## 19.0.1.2.0

**Corectat** — soldurile registrului nu se mai învechesc.

Soldul inițial și soldul final erau calculate o singură dată, la crearea registrului, și nu
se mai actualizau când apăreau mișcări pe contul de casă. Cum registrul zilei este creat
automat la postarea primei plăți sau de acțiunea de generare, el se năștea aproape
întotdeauna pe o zi încă goală, iar soldurile rămâneau blocate — fără niciun semnal vizibil.
Recalculul era posibil doar manual, din butonul **Refresh**, și numai pentru registrele
selectate: o corecție într-o zi lăsa greșite toate zilele următoare.

Soldurile se recalculează acum automat la postarea, anularea sau ștergerea notelor care
ating contul de casă, pentru ziua respectivă și pentru toate zilele ulterioare din același
jurnal. Conform OMFP 2634/2015, Anexa 1 pct. 58 lit. e) și n), programul trebuie să asigure
*reluarea automată* în calcul a soldurilor obținute anterior.

Registrele existente sunt recalculate la actualizarea modulului.

**Corectat** — operațiunile se listează în ordine cronologică.

Liniile moșteneau ordinea implicită descrescătoare a înregistrărilor contabile, astfel încât
coloana de sold descria o succesiune de solduri intermediare care nu existase niciodată.

**Corectat** — registrul unei companii nu mai preia mișcări ale altei companii.

Selecția liniilor filtrează acum explicit pe companie.

**Eliminat** — `action_recompute_from_previous_balance`.

Metoda căuta registrul precedent fără condiție pe dată și fără să se excludă pe sine, deci
putea prelua soldul registrului curent sau al unuia ulterior și scria rezultatul direct peste
soldurile calculate. Putea produce astfel un sold de deschidere diferit de soldul de închidere
al zilei precedente. Nu era expusă în interfață și nu avea niciun apelant.

**Adăugat** — buton **Tipărește** în formularul și în lista registrelor.

Raportul exista, dar era accesibil doar din meniul de acțiuni și trecea neobservat.

**Îmbunătățit** — raportul tipărit urmează formularul 14-4-7A.

Documentul poartă acum codul formularului și coloanele **Nr. act de casă**, **Nr. anexe**
(numărul atașamentelor notei contabile) și **Explicații**, alături de partener. Totalurile
apar pe rânduri distincte — *Total încasări*, *Total plăți*, *Sold la sfârșitul zilei* — în
locul rândului unic de sold final, iar rândul de report este denumit explicit *Sold reportat
din ziua precedentă*. S-au adăugat rubricile de semnătură pentru casier și pentru
compartimentul financiar-contabil, precum și mențiunea programului informatic și a versiunii,
cerută pe orice listare de Anexa 1 pct. 58 lit. k).

Sumele se afișează în moneda registrului, nu în moneda companiei, pentru registrele de casă
în valută.

Etichetele antetului au fost restructurate ca să nu mai depindă de indentarea din șablon,
care rupea traducerile la fiecare reformatare.

## 19.0.1.1.8

Versiuni anterioare — vezi istoricul repozitoriului.
