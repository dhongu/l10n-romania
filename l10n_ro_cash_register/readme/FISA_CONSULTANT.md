# Fișă Modul: Registrul de casă zilnic, cu închiderea zilei (14-4-7A)

**Poziție plan:** C20  
**Modul:** `l10n_ro_cash_register`  
**Suită:** `l10n-romania`  
**FR:** FR-28  
**Capitol manual:** Cap 8.4  
**Utilizator principal:** Casier, contabil, contabil-șef (redeschiderea zilei)  
**Prioritate:** 🔴 Ridicată (orice firmă cu casierie trebuie să întocmească zilnic registrul de casă)

---

## 1. Scop business

Modulul transformă jurnalul de numerar într-un **registru de casă zilnic**: un document numerotat
pentru fiecare casierie și zi, cu sold reportat din ziua precedentă, mișcările zilei și soldul de la
sfârșitul zilei, tipărit în forma formularului **14-4-7A**. Din registru, casierul înregistrează
încasări, plăți și alte operațiuni de casă, iar la sfârșitul zilei **închide ziua**: soldul se
îngheață și nicio notă pe contul casei nu mai poate fi postată, trecută în ciornă sau ștearsă cu
o dată din ziua închisă sau dinaintea ei. Contabilul-șef poate **redeschide** ziua, cu urmă în
istoric.

Modulul nu acoperă importul extraselor bancare (MT940) și nici reconcilierea bancară; acestea sunt
module complementare.

## 2. Bază legală și context

- **Registrul de casă** — cod **14-4-7A**, poziția 27 în Nomenclatorul documentelor
  financiar-contabile (**OMFP 2634/2015, Anexa 2**, Grupa a IV-a „Mijloace bănești și decontări”).
  Norma specifică: se întocmește **zilnic**, de casier, pe baza documentelor justificative de
  încasare și plată; stabilește soldul de casă la sfârșitul fiecărei zile, care se reportează în
  ziua următoare. Conținutul minim (Anexa 1 pct. 2 și 10): contul casei, data, nr. act de casă,
  nr. anexe, explicații, încasări, plăți, sold reportat și sold final, semnături.
- **Anexa 1 pct. 58 lit. d) și h)** — programul informatic trebuie să asigure controlul datelor
  introduse și să împiedice modificarea datelor din perioadele închise. Închiderea zilei de casă
  aplică această regulă pe contul casei: după închidere, o mișcare datată în urmă ar schimba un
  sold deja reportat și tipărit.
- **Anexa 1 pct. 58 lit. k)** — orice listare poartă denumirea programului informatic și versiunea;
  raportul tipărit are această mențiune în subsol.
- **Anexa 1 pct. 12, 36 și 56** — listarea pe hârtie nu este obligatorie zilnic: obligatorie este
  **întocmirea** zilnică; documentele se pot păstra electronic, cu condiția să poată fi listate
  oricând.
- **Legea 70/2015** (plafoanele de încasări și plăți în numerar) — **nu** este verificată de modul;
  vezi secțiunea 11.

> **Surse:** [OMFP 2634/2015, Anexele 2 și 3 — MFinanțe (PDF)](https://mfinante.gov.ro/documents/35673/219198/anexe2_3ordin2634_2015.pdf)
> · [Anexa 2 — Portal Legislativ](https://legislatie.just.ro/Public/DetaliiDocument/173807)
> · [Anexa 1 — ANAF (PDF)](https://static.anaf.ro/static/10/Anaf/legislatie/OMFP_2634_2015.pdf)

## 3. Utilizatori și roluri

| Rol | Ce face în modul |
|---|---|
| **Casier** | înregistrează încasările, plățile și operațiunile de casă din registru; închide ziua |
| **Contabil** | verifică soldurile, tipărește registrul, corelează cu notele contabile |
| **Contabil-șef** | redeschide o zi închisă, când o corecție nu se poate face printr-o notă datată azi |
| **Consultant implementare** | configurează jurnalul de numerar și explică regula închiderii |

Meniul și accesul la registru sunt rezervate grupului **Facturare / Contabilitate → Administrator**
(`account.group_account_manager`). **Modulul nu separă rolurile:** orice utilizator cu acces la
registru — inclusiv casierul care a închis ziua — poate și redeschide. Separarea „casierul închide,
contabilul-șef redeschide” se asigură prin procedură internă; programul garantează doar urma în
istoric (cine a închis, cine a redeschis, când și cu ce sold).

La testare, folosiți doi utilizatori din acest grup — unul în rol de casier, altul de
contabil-șef — ca să vedeți în registru cine a închis și cine a redeschis.

## 4. Conturi și date implicate

| Cont | Denumire | Rol în flux |
|---|---|---|
| **5311** | Casa în lei (analitic per casierie, ex. 531102 „Casa lei”) | contul implicit al jurnalului de numerar; din el se calculează soldurile |
| **581** | Viramente interne | alimentarea casei din bancă; contul corespondent propus implicit în wizardul de operațiune |
| **4111** | Clienți | încasări de la clienți |
| **401** | Furnizori | plăți către furnizori |
| **542** | Avansuri de trezorerie | avansuri în numerar date angajaților |
| **7588** / **6588** | Alte venituri / cheltuieli din exploatare (în planul Odoo RO: 758800 / 658810) | **Cont profit** / **Cont pierderi** pe jurnal, pentru plusurile și minusurile de casă constatate |

Date minime pentru demo (sunt cele din capturi):

- casieria **Casa lei** (jurnal de tip numerar, cod `CASA`);
- parteneri: client **Alfa Distribuție SRL**, furnizor **Papetăria Centrală SRL**, angajat
  **Ionescu Andrei**;
- trei facturi: două facturi de vânzare către Alfa (413,22 + TVA 21% = 500,00 lei; 247,93 + TVA =
  300,00 lei) și factura de rechizite PC-2291 de la Papetăria (165,29 + TVA = 200,00 lei);
- trei zile consecutive de operațiuni (vezi „Note de monografie”): ziua 1 alimentare 1.000 lei,
  ziua 2 încasare 500 / plată 200 / avans 150, ziua 3 încasare 300;
- utilizatorii **Maria Popescu** (casier) și **Elena Dumitrescu** (contabil-șef).

## 5. Configurare inițială

1. Instalați `l10n_ro_account_sequence` și `l10n_ro_cash_register` pe o companie cu planul de
   conturi românesc.
2. **Facturare / Contabilitate → Configurare → Jurnale** → deschideți jurnalul de tip **Numerar**
   și verificați:
   - **Cont numerar** = analiticul de 5311 al casieriei; fiecare casierie are **propriul** analitic
     (două jurnale pe același cont își amestecă soldurile);
   - **Prefix secvență** (codul jurnalului) — dă și numărul registrului, ex. `CASA/2026/00002`;
   - **Cont profit** / **Cont pierderi** = 7588 / 6588 (plusuri / minusuri de casă). Planul Odoo RO
     propune la crearea jurnalului conturile generice **999001 / 999002**, care nu există în planul
     de conturi românesc și trebuie înlocuite; minusul imputabil casierului se trece ulterior pe
     4282 printr-o notă separată.

   ![Jurnalul de casă](screenshots/01_jurnal_cash.png)

   - în filele **Plăți de primit** și **Plăți efectuate**, metodele de plată folosesc **contul
     casei** (531102), nu un cont de „plăți în curs”. La jurnalele create după instalarea
     `l10n_ro_account_sequence`, setarea se face automat. La un jurnal **existent**, rulați din
     lista jurnalelor acțiunea **Elimină conturile de plăți în curs** (meniul **Acțiuni**) —
     altfel încasările și plățile rămân pe contul în curs și **nu apar în registru**. Atenție:
     acțiunea **mută și liniile deja postate** de pe contul în curs pe contul casei; rulați-o doar
     cu acordul contabilului.
3. Pe companie, contul de **transfer intern** (581) este completat — wizardul de operațiune îl
   propune implicit ca și cont corespondent.
4. Pentru istoric existent: în lista jurnalelor, selectați casieria și rulați acțiunea **Generează
   registrele de casă lipsă** (meniul **Acțiuni**), care creează registrele pentru toate zilele cu
   mișcări pe contul casei, plus ziua curentă. Există și un cron cu aceeași acțiune, livrat
   **inactiv**.
5. Atribuiți utilizatorilor grupul **Administrator** pe Facturare / Contabilitate (vezi secțiunea 3).

## 6. Flux de utilizare

### Pasul 1 — Lista registrelor de casă

**Facturare / Contabilitate → Contabilitate → Tranzacții → Registrul de casă**, sau un clic pe
cardul casieriei din tabloul de bord (pentru companiile din România, cardul de numerar deschide
registrul, nu lista generică de plăți).

Lista are **un rând pe casierie și zi**: număr, dată, jurnal, **Sold inițial**, **Sold final** și
**Stare** (*Deschisă* / *Închisă*).

![Lista registrelor de casă](screenshots/02_lista_registre.png)

**Găsiți pe ecran:** coloanele **Sold inițial** și **Sold final** pe fiecare zi și coloana
**Stare**. În captură: zilele 2, 3 și 4 septembrie, plus registrul zilei curente (creat de acțiunea
de generare, fără mișcări, deci cu sold inițial = sold final).
**Verificați:** soldul inițial al fiecărei zile este egal cu soldul final al zilei anterioare (în
captură: 0 → 1.000; 1.000 → 1.150; 1.150 → 1.450); zilele deja închise (aici, ziua 1) nu au între
ele o zi rămasă deschisă. Zilele 2 și 3 sunt încă deschise — închiderea lor urmează în pașii 5–6.

Modulul **nu impune ordinea** închiderii. Atenție: închiderea unei zile blochează și **toate
zilele dinaintea ei** (pasul 7), chiar dacă acestea apar încă *Deschisă*; închideți zilele în
ordine, una câte una.

Registrul unei zile se creează automat la postarea unei plăți pe casierie sau prin acțiunea de
generare a registrelor lipsă. Nu pot exista două registre pentru aceeași casierie și zi. Numărul
registrului urmează **ordinea creării**, nu ordinea zilelor: un registru creat târziu pentru o zi
din urmă primește următorul număr liber. Registrul are formatul `CASA/2026/NNNNN`, ca notele de
casă fără tip, dar **contor propriu**: registrul `CASA/2026/00002` și nota `CASA/2026/00002` sunt
documente diferite.

### Pasul 2 — Formularul registrului și operarea zilei

Deschideți registrul zilei. Bara de sus are butoanele **Tipărire**, **Împrospătare**, **Încasare**
①, **Plată** ②, **Operație** ③ și **Închide ziua**; în dreapta, starea (*Deschisă* / *Închisă*).

![Formularul registrului de casă, cu butoanele de operare](screenshots/03_formular_registru.png)

- ① **Încasare** — deschide o încasare (plată de primit) pe casierie, cu data registrului; primește
  număr de **chitanță** (ex. `CHCASA/2026/00001`) și se lettrează cu factura clientului;
- ② **Plată** — deschide o plată (plată efectuată) pe casierie, cu data registrului; primește număr
  de **dispoziție de plată** (ex. `PLCASA/2026/00001`) și se lettrează cu factura furnizorului;
- ③ **Operație** — deschide wizardul de operațiune de casă (pasul 3), pentru operațiunile fără
  factură.

Încasările și plățile **pe factură** se fac cu **Încasare / Plată** — sau direct din factură, cu
butonul de înregistrare a plății, alegând jurnalul casei — nu din wizard: doar așa au act de casă numerotat și
închid factura.

Fila **Linii registrul de casă** listează notele postate pe contul casei în ziua respectivă, în
ordinea înregistrării: numărul actului de casă, partener, sumă (plus = încasare, minus = plată) și
referință (factura achitată sau explicația).
**Sold final** = **Sold inițial** + totalul liniilor (în captură: 1.000 + 150 = 1.150 lei).

Soldurile se recalculează automat la postarea, trecerea în ciornă sau ștergerea oricărei note pe
contul casei — pentru ziua respectivă și pentru toate zilele următoare. **Împrospătare** rămâne
doar pentru recalcul manual.

### Pasul 3 — Operațiune de casă (wizard)

Butonul **Operație** deschide fereastra **Operațiune registrul de casă**, pentru operațiunile
**fără factură**: alimentarea casei din bancă sau depunerea numerarului la bancă (581), avansuri de
trezorerie (542), restituiri de avans, plusuri de casă etc.:

![Wizardul de operațiune de casă](screenshots/04_wizard_operatiune.png)

- **Operație**: *Depunere* (intrare în casă) sau *Retragere* (ieșire din casă);
- **Suma**, **Descriere** (apare ca explicație în registru), **Partener**;
- **Cont** — contul corespondent; implicit 581, se schimbă după natura operațiunii (542, 7588
  etc.);
- **Jurnal** și **Data** vin din registru.

**Confirmare** creează și postează imediat nota contabilă: *Depunere* = debit casă / credit cont
ales; *Retragere* = debit cont ales / credit casă. Actul de casă primește numărul notei
(`CASA/2026/NNNNN`), fără serie de chitanță sau dispoziție, și nu se lettrează cu nicio factură.

### Pasul 4 — Tipărirea registrului

**Tipărire** (din formular sau, pentru mai multe zile, din listă, după selectarea rândurilor)
produce registrul în forma formularului **14-4-7A**:

![Raportul „Registrul de casă” (14-4-7A)](screenshots/05_raport_pdf.png)

**Găsiți pe ecran:** antetul cu compania, CIF și NRC; rândul **Sold reportat din ziua
precedentă**; liniile zilei (NrCrt, nr. act de casă, nr. anexe, explicații, partener, încasări,
plăți, sold cumulat); rândurile **Total încasări**, **Total plăți**, **Sold la sfârșitul zilei**;
rubricile de semnătură; în subsol, programul și versiunea.
**Verificați:** soldul reportat = soldul final al zilei anterioare (1.000,00); soldul reportat +
total încasări − total plăți = sold la sfârșitul zilei (1.000 + 500 − 350 = 1.150,00); soldul
cumulat de pe ultima linie este egal cu soldul de la sfârșitul zilei.
Coloana **Nr. anexe** numără atașamentele notei contabile (documentele justificative scanate).

### Pasul 5 — Închiderea zilei

După ce ultima operațiune a zilei este înregistrată și registrul verificat, casierul apasă
**Închide ziua**. Apare confirmarea:

![Confirmarea închiderii zilei](screenshots/06_confirmare_inchidere.png)

Mesajul spune exact efectul: după închidere, **nicio înregistrare pe contul casei nu mai poate fi
datată în această zi sau înaintea ei** până la redeschidere. **Ok** închide ziua.

Închiderea este refuzată dacă:

- ziua este **în viitor**;
- soldul final este **negativ** — casieria nu poate plăti mai mult decât are; corectați întâi
  înregistrările.

### Pasul 6 — Registrul închis

![Registrul de casă închis](screenshots/07_registru_inchis.png)

- ① starea devine **Închisă**;
- ② apar **Sold la închidere** (soldul înghețat), **Închisă de** și **Închisă la**.

**Verificați:** *Sold la închidere* = *Sold final* (1.150,00 lei); *Închisă de* este casierul
care a apăsat butonul.

Pe un registru închis: butoanele **Încasare**, **Plată**, **Operație** și **Închide ziua** dispar,
locul lor îl ia **Redeschide**; data, casieria și numărul nu se mai pot modifica; registrul nu se
poate șterge.

### Pasul 7 — O postare în ziua închisă este refuzată

Exemplu: după închiderea zilei 2, contabilul descoperă o plată de 80 lei către furnizor, făcută
în ziua 2 dar neînregistrată, și încearcă să posteze nota cu data zilei 2 (din jurnalul de casă,
**Postează**). Odoo refuză:

![Mesajul de blocare la postarea în ziua închisă](screenshots/08_blocare_postare.png)

Mesajul numește registrul închis, casieria și ziua. Aceeași regulă se aplică la **trecerea în
ciornă** și la **ștergerea** unei note postate pe contul casei, datate în ziua închisă **sau
înaintea ei** (o mișcare mai veche ar schimba soldul reportat în ziua închisă). Notele datate
**după** ultima zi închisă și notele pe alte casierii nu sunt afectate.

Corecția se face, de regulă, **fără redeschidere**. Documentul justificativ (dispoziția de plată,
chitanța furnizorului) își păstrează **data reală** (ziua 2); doar înregistrarea în registru se face
azi. Plafoanele de numerar (Legea 70/2015) se judecă tot pe ziua reală a plății.

- **stornare** sau **notă de corecție datată în ziua curentă** — zilele închise rămân neschimbate,
  iar diferența apare în registrul zilei de azi, cu explicația ei;
- **redeschiderea** (pasul 8) doar când corecția trebuie să apară chiar în ziua greșită, cu acordul
  contabilului-șef.

### Pasul 8 — Redeschiderea zilei

Pe registrul închis, contabilul-șef apasă **Redeschide** (programul nu restricționează butonul pe
rol — vezi secțiunea 3). Confirmarea avertizează că se redeschid
și **zilele închise de după aceasta din aceeași casierie** (soldul se reportează din zi în zi,
deci o corecție în ziua redeschisă le schimbă și lor soldurile):

![Confirmarea redeschiderii](screenshots/09_confirmare_redeschidere.png)

După **Ok**, registrul revine la starea **Deschisă**, butoanele de operare reapar, iar istoricul
fiecărui registru redeschis păstrează urma: cine a închis, cine a redeschis și soldul de la
închidere.

![Registrul redeschis, cu urma în istoric](screenshots/10_registru_redeschis.png)

**Verificați în istoric:** schimbarea *Deschisă → Închisă* cu numele casierului; mesajul
„Registru de casă redeschis de … (soldul la închidere era …)” și schimbarea *Închisă → Deschisă*
cu numele contabilului-șef. După corecție, **închideți din nou** ziua și toate zilele redeschise,
în ordine.

### Note de monografie și raportare

Notele din capturi (casieria **Casa lei**, cont 5311, analitic 531102):

```
Ziua 1  Alimentare casă din bancă (CEC 0045)   Dr 5311   1.000  =  Cr 581    1.000
        (partea de bancă, din extras:            Dr 581    1.000  =  Cr 5121   1.000)
Ziua 2  Chitanța CHCASA/2026/00001 — Alfa       Dr 5311     500  =  Cr 4111     500   (factura INV/2026/00001)
        Dispoziția PLCASA/2026/00001 — Papetăria Dr 401      200  =  Cr 5311     200   (factura PC-2291)
        Avans deplasare Cluj — Ionescu Andrei   Dr 542      150  =  Cr 5311     150   (wizard)
Ziua 3  Chitanța următoare — Alfa               Dr 5311     300  =  Cr 4111     300   (a doua factură)
```

Solduri: ziua 1: 0 → 1.000; ziua 2: 1.000 → 1.150; ziua 3: 1.150 → 1.450.

- Avansul de trezorerie se justifică ulterior prin decont (Dr 6xx / Dr 4426 = Cr 542), iar restul
  nefolosit se restituie în casă (Dr 5311 = Cr 542) — notele de decont nu sunt generate de modul.
- Plata uitată de 80 lei din pasul 7, înregistrată ca notă de corecție **datată azi**:
  `Dr 401  80 = Cr 5311  80`, cu explicația „Plată factura PC-2297 din ziua 2, înregistrată
  ulterior”.
- **Ce citește registrul:** doar notele **postate** pe contul implicit al jurnalului (5311 analitic).
  Mișcările pe 542 sau pe alte conturi de trezorerie nu intră în registrul de casă.
- **Raportare:** registrul tipărit (14-4-7A) se arhivează zilnic (electronic sau pe hârtie). La
  sfârșitul lunii, soldul **analiticului** 5311xx al casieriei din balanța analitică este egal cu
  soldul ultimei zile din registrul acelei casierii; sinteticul 5311 este suma soldurilor tuturor
  casieriilor în lei.

## 7. Legături cu alte module / declarații

| Modul | Rol |
|---|---|
| `account` | jurnale, plăți, note contabile |
| `l10n_ro_account_sequence` | numerotarea actelor de casă (dispoziții, chitanțe) și a registrului |
| `l10n_ro_cash_register_report` (suita `l10n_ro_ent`) | raport pe interval de zile, cu drill-down și export PDF/XLSX; aceleași cifre, fără numerotare (Enterprise) |
| `l10n_ro_account_bank_statement_import_mt940_*` | importul extraselor bancare — complementar, în afara acestui modul |

**Ce e automat:** crearea registrului zilei la postarea unei plăți pe casierie; calculul și
recalcularea soldurilor în lanț; nota contabilă din wizardul de operațiune; blocarea postării,
trecerii în ciornă și ștergerii notelor pe casă datate într-o zi închisă sau înaintea ei;
redeschiderea în cascadă a zilelor închise ulterioare; urma în istoric.

**Ce rămâne manual:** apăsarea **Închide ziua** în fiecare zi (nu există închidere automată);
tipărirea și semnarea registrului; activarea cronului de generare a registrelor lipsă, dacă se
dorește; corecțiile (stornare / notă datată azi / redeschidere aprobată); respectarea plafoanelor
de numerar.

## 8. Verificări pentru consultant

- [ ] Registrul unei zile are număr cu prefixul codului jurnalului (ex. `CASA/2026/…`), cu contor
      propriu, independent de notele de casă.
- [ ] Metodele de plată ale casieriei folosesc contul casei (nu un cont de plăți în curs).
- [ ] O încasare din butonul **Încasare** primește număr de chitanță și închide factura clientului.
- [ ] O plată postată pe casierie într-o zi fără registru creează registrul zilei.
- [ ] **Generează registrele de casă lipsă** creează registre pentru toate zilele cu mișcări, plus azi.
- [ ] *Depunere* din wizard: notă postată cu debit 5311; *Retragere*: notă cu credit 5311.
- [ ] Soldul inițial al fiecărei zile = soldul final al zilei anterioare (lista din pasul 1).
- [ ] O notă postată într-o zi anterioară actualizează singură soldurile zilei și ale zilelor
      următoare, fără **Împrospătare**.
- [ ] Raportul tipărit: sold reportat + total încasări − total plăți = sold la sfârșitul zilei;
      subsolul are programul și versiunea.
- [ ] **Închide ziua** pe o zi trecută cu sold pozitiv: starea *Închisă*, *Sold la închidere* =
      *Sold final*, *Închisă de* = utilizatorul curent.
- [ ] Postarea unei note pe casă datate în ziua închisă **sau înaintea ei** este refuzată cu
      mesajul din pasul 7; la fel trecerea în ciornă și ștergerea unei note postate din acea zi.
- [ ] O notă pe casă datată **după** ziua închisă, sau pe altă casierie, se postează normal.
- [ ] Pe registrul închis nu se pot modifica data, jurnalul, numărul și nu se poate șterge.
- [ ] **Închide ziua** pe o zi din viitor sau cu sold negativ este refuzată.
- [ ] Un utilizator fără acces de Administrator contabilitate nu vede meniul registrului.
- [ ] **Redeschide** pe ziua 2, cu ziua 3 tot închisă: ambele devin *Deschisă*, fiecare cu mesajul
      de redeschidere în istoric.

## 9. Mesaje de eroare frecvente

| Mesaj | Cauză | Remediere |
|---|---|---|
| Registrul de casă … al casieriei … din … este închis. O înregistrare pe contul casei datată … i-ar schimba soldul: redeschideți întâi registrul. | postare, trecere în ciornă sau ștergere a unei note pe casă datate într-o zi închisă sau înaintea ei | notă de corecție / stornare datată azi; doar la nevoie, redeschiderea zilei de către contabilul-șef |
| Nu se poate închide o zi din viitor (…). | **Închide ziua** pe un registru cu dată ulterioară zilei curente | închideți ziua după ce s-a încheiat |
| Soldul registrului de casă … este negativ (…): casieria nu poate plăti mai mult decât are. Corectați înregistrările înainte de a închide ziua. | plățile zilei depășesc soldul disponibil (de obicei o încasare neînregistrată sau o dată greșită) | înregistrați încasarea lipsă sau corectați data notei, apoi închideți |
| Un registru de casă închis nu se poate modifica; redeschideți-l întâi. | schimbarea datei, casieriei sau numărului pe un registru închis | **Redeschide**, modificați, închideți din nou |
| Un registru de casă închis nu se poate șterge; redeschideți-l întâi. | ștergerea unui registru închis | **Redeschide** înainte de ștergere |
| Există deja un registru de casă pentru această casierie și zi. | al doilea registru pentru aceeași casierie și zi | folosiți registrul existent al zilei |
| Încasarea / plata nu apare în registru | metoda de plată a jurnalului folosește un cont de plăți în curs, nu contul casei | **Elimină conturile de plăți în curs** pe jurnal (secțiunea 5), apoi verificați registrul |

## 10. Capturi de ecran

Capturile din `readme/screenshots/` sunt **generate automat** de `tests/test_screenshots.py`
(mixinul `ScreenshotCase` din `l10n_ro_doc_screenshots`, import defensiv), cu interfața în
**română**, pe planul de conturi RO și în RON, pe datele demo din secțiunea 4:

1. `01_jurnal_cash.png` — jurnalul de numerar „Casa lei” (cont 531102, prefix `CASA`, conturi de
   profit / pierderi 758800 / 658810).
2. `02_lista_registre.png` — lista registrelor: ziua 1 închisă, celelalte deschise, solduri în lanț.
3. `03_formular_registru.png` — registrul zilei 2, cu butoanele Încasare / Plată / Operație și
   liniile zilei (chitanță, dispoziție de plată, avans).
4. `04_wizard_operatiune.png` — wizardul de operațiune de casă (Depunere / Retragere).
5. `05_raport_pdf.png` — registrul tipărit, formular 14-4-7A.
6. `06_confirmare_inchidere.png` — confirmarea de la **Închide ziua**.
7. `07_registru_inchis.png` — registrul închis: Sold la închidere, Închisă de, Închisă la.
8. `08_blocare_postare.png` — mesajul de blocare la postarea unei note pe casă în ziua închisă.
9. `09_confirmare_redeschidere.png` — confirmarea de la **Redeschide**.
10. `10_registru_redeschis.png` — registrul redeschis, cu urma închiderii și redeschiderii în istoric.

Regenerare (testele modulului rulează pe o bază cu date demo):

```bash
./odoo/odoo-bin -c odoo.conf -d <db> -i l10n_ro,l10n_ro_cash_register,l10n_ro_doc_screenshots \
    --test-tags=fise_screenshots --stop-after-init
```

> Capturile cer modulul de tooling `l10n_ro_doc_screenshots` (suita `l10n_ro_ent`) și Playwright;
> dacă lipsesc, testul se sare.

## 11. Observații pentru manual

- Prezentați registrul ca **document zilnic numerotat** (14-4-7A), iar închiderea zilei ca
  **semnătura electronică a casierului** pe soldul zilei: după ea, ziua nu se mai schimbă fără
  urmă.
- Insistați pe regula de corecție: **după închidere, corecția se face azi** (stornare / notă de
  corecție); redeschiderea e excepția, aprobată de contabilul-șef, și redeschide în cascadă toate
  zilele închise de după ea, care trebuie apoi închise din nou.
- Blocarea privește doar **contul implicit al casieriei**; o casierie cu cont 5311 comun cu alta
  amestecă soldurile — un analitic de 5311 per casierie este obligatoriu.
- Limitări de spus clientului: plafoanele de numerar din Legea 70/2015 nu sunt verificate; nu
  există tipărire individuală a unui act de casă din linia registrului; cronul de generare a
  registrelor lipsă este livrat inactiv; închiderea zilei nu este automată și nu se impune ordinea
  zilelor; redeschiderea nu este restricționată pe rol; registrul este corect **doar pentru
  casieriile în moneda companiei (lei)** — soldurile se calculează în lei, deci o casierie în
  valută (5314, formularul 14-4-7/aA) nu este suportată.
- Pentru analiză pe perioade (mai multe zile, export XLSX), recomandați în paralel raportul
  `l10n_ro_cash_register_report` (Enterprise); cifrele sunt aceleași.
