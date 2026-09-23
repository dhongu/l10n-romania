DVI - declaraţie vamala de import
================================

Acest modul face legătura între factura de achiziţie şi DVI (landed cost).
Se generează automat un DVI cu două linii şi cu TVA.

Conturile de decontare cu bugetul folosite de modul (446) trebuie să fie conturi de reconciliere,
pentru a se putea închide prin bancă, per declaraţie vamală.

Baza legală privind înregistrarea contabilă a operaţiunilor de import
--------------------------------------------------------------------

Prezentul capitol sintetizează cadrul legal aplicabil operaţiunilor de import (achiziţie marfă externă + Declaraţie Vamală de Import – DVI), cu accent pe următoarele aspecte:

* Factura comercială externă se înregistrează în contabilitate la cursul BNR din data emiterii facturii;
* Cursul valutar din vamă (cursul vamal lunar) se utilizează exclusiv pentru calculul valorii în vamă, al taxelor vamale (A00) şi al TVA-ului la import (B00) din DVI;
* Toate înregistrările contabile (factură, taxe vamale, stocuri) se efectuează şi se prezintă doar în moneda naţională (RON).

### 1. Legea contabilităţii nr. 82/1991 (republicată)

* **Art. 3 alin. (1):** „Contabilitatea se ţine în limba română şi în moneda naţională.”
* **Art. 3 alin. (2):** „Contabilitatea operaţiunilor efectuate în valută se ţine atât în moneda naţională, cât şi în valută, potrivit reglementărilor elaborate în acest sens.”

Toate operaţiunile de import (inclusiv factura furnizor şi DVI) se înregistrează şi se prezintă în situaţiile financiare exclusiv în RON.

### 2. OMFP nr. 1802/2014

* **Pct. 319:** „O tranzacţie în valută trebuie înregistrată iniţial la cursul de schimb valutar, comunicat de Banca Naţională a României, de la data efectuării operaţiunii.” -> Factura comercială externă (Vendor Bill) se înregistrează la cursul BNR din data emiterii facturii.
* **Pct. 6 (definiţia costului de achiziţie):** „Costul de achiziţie al bunurilor cuprinde preţul de cumpărare, taxele de import şi alte taxe (cu excepţia acelora pe care persoana juridică le poate recupera de la autorităţile fiscale)…”
* **Pct. 75 alin. (1) lit. a):** Bunurile se evaluează şi se înregistrează la data intrării în entitate la cost de achiziţie (care include taxele vamale plătite conform DVI).
* **Pct. 94 lit. a):** Elementele monetare exprimate în valută se evaluează la cursul BNR la data bilanţului; diferenţele de curs se înregistrează pe conturile 665 sau 765.

Taxele vamale (A00) se capitalizează în costul stocurilor (contul 327 -> 371), iar toate valorile finale rămân exclusiv în RON.

### 3. Legea nr. 227/2015 – Codul Fiscal

* **Art. 289 (Baza de impozitare pentru import):** vezi capitolul dedicat de mai jos — este articolul care stabileşte **ce sume intră în baza TVA la import**.
* **Art. 290 alin. (1) (Cursul de schimb valutar):** „Dacă elementele folosite la stabilirea bazei de impozitare a unui import de bunuri se exprimă în valută, cursul de schimb valutar se stabileşte conform prevederilor europene care reglementează calculul valorii în vamă.”
* **Art. 299 alin. (1) lit. c):** Dreptul de deducere a TVA aferente importului de bunuri se exercită pe baza Declaraţiei vamale de import (DVI) sau a actului constatator emis de organele vamale (TVA B00 calculat la cursul vamal).

> **Corecţie (2026-09-22).** Textul despre cursul de schimb citat anterior în dreptul art. 289 aparţine de fapt **art. 290 alin. (1)**. Art. 289 reglementează cu totul altceva — componenţa bazei de impozitare — iar omisiunea lui din acest capitol a fost sursa unei confuzii reale la client (baza propusă de sistem interpretată ca bază legală). Vezi capitolul următor.

Cursul din DVI se foloseşte doar pentru determinarea valorii în vamă, calculul taxei vamale (A00) şi al TVA-ului la import (B00). Nu afectează înregistrarea facturii comerciale în contabilitate.

### 4. Regulamentul de punere în aplicare (UE) 2015/2447 al Comisiei

* **Art. 146 (Conversia monetară în scopul determinării valorii în vamă):** „În situaţia în care valoarea în vamă a mărfurilor este exprimată într-o altă monedă decât cea naţională, cursul de schimb folosit la determinarea acestei valori este cursul de schimb stabilit şi comunicat de Banca Naţională a României în penultima zi de miercuri a lunii anterioare lunii în care se utilizează.”

Cursul vamal este un curs lunar fix, aplicabil exclusiv în cadrul procedurii vamale pentru calculul valorii statistice, taxelor vamale şi TVA la import. Nu se utilizează pentru înregistrarea facturii furnizor în contabilitate.

### Concluzie

Cadrul legal este clar şi unitar:
* **Factura furnizor** -> curs BNR (data facturii) + înregistrare în RON.
* **DVI** -> curs vamal lunar (Reg. UE 2015/2447 art. 146 + Cod Fiscal art. 290 alin. (1)) doar pentru taxe vamale şi TVA la import.
* **Toate înregistrările contabile** (inclusiv costul stocurilor) -> exclusiv în RON.

Baza de impozitare a TVA la import — ce intră şi ce nu
------------------------------------------------------

Aceasta este întrebarea care apare cel mai des la operarea modulului: **ce cifră se pune în câmpul
„Bază de impozitare” din wizardul DVI?** Răspunsul nu ţine de configurare, ci de art. 289 din Legea
227/2015.

### Textul legal

**Art. 289 alin. (1):** „Baza de impozitare pentru importul de bunuri este **valoarea în vamă a
bunurilor, stabilită conform legislaţiei vamale în vigoare**, la care se adaugă **orice taxe,
impozite, comisioane şi alte taxe datorate în afara României, precum şi cele datorate ca urmare a
importului bunurilor în România**, cu excepţia taxei pe valoarea adăugată care urmează a fi
percepută.”

**Art. 289 alin. (2):** „Baza de impozitare cuprinde **cheltuielile accesorii, precum comisioanele,
cheltuieli de ambalare, transport şi asigurare, care intervin până la primul loc de destinaţie a
bunurilor în România**, în măsura în care aceste cheltuieli **nu au fost cuprinse în baza de
impozitare stabilită conform alin. (1)** […]. Primul loc de destinaţie a bunurilor îl reprezintă
destinaţia indicată în documentul de transport sau în orice alt document în baza căruia bunurile sunt
importate în România ori, în absenţa unei astfel de menţiuni, primul loc de descărcare a bunurilor în
România.”

**Art. 289 alin. (3):** baza nu cuprinde elementele de la art. 286 alin. (4) lit. a)–d) — rabaturi,
remize, risturne şi sconturi acordate la data exigibilităţii, daune-interese şi penalităţi, dobânzi de
întârziere, ambalaje care circulă prin schimb fără facturare.

### Formula practică

```
Bază TVA import = valoare în vamă
                + taxa vamală (A00) + accize + alte drepturi de import
                + cheltuieli accesorii până la primul loc de destinaţie în RO,
                  DOAR dacă nu sunt deja în valoarea în vamă
                − TVA însăşi
```

Sintagma „**în măsura în care nu au fost cuprinse** în baza stabilită conform alin. (1)” este clauza
anti-dublă-numărare: transportul deja inclus în valoarea în vamă **nu se mai adaugă a doua oară**.

**Primul loc de destinaţie nu este frontiera**, ci destinaţia din documentul de transport (CMR) — în
practică depozitul importatorului — iar în lipsa menţiunii, primul loc de descărcare în România.

### Valoarea în vamă vs. baza TVA — unde intră transportul

Regulamentul (UE) 952/2013 (Codul Vamal al Uniunii) stabileşte valoarea în vamă pornind de la valoarea
de tranzacţie (art. 70), la care art. 71 alin. (1) lit. (e) **adaugă** cheltuielile de transport,
asigurare, încărcare şi manipulare **până la locul de introducere pe teritoriul vamal al Uniunii**;
art. 72 lit. (a) **exclude** transportul de după intrarea pe teritoriul vamal al Uniunii.

| Segment de transport | Valoare în vamă (bază taxă vamală) | Bază TVA import |
|---|---|---|
| Din ţara terţă până la frontiera UE | **DA** — CVU art. 71 alin. (1) lit. (e) | DA, indirect, prin valoarea în vamă (art. 289 alin. (1)) |
| De la frontiera UE până la primul loc de destinaţie din RO | **NU** — CVU art. 72 lit. (a) | **DA** — art. 289 alin. (2) |
| După primul loc de destinaţie din RO | NU | NU |

Pentru un import din Republica Moldova vămuit în România, frontiera UE **este** frontiera română —
deci întregul transport extern se regăseşte deja în valoarea în vamă.

### Valoarea statistică din DVI nu este baza de impozitare

Sunt două mărimi cu scopuri diferite: valoarea statistică serveşte statisticii de comerţ exterior
(Reg. de punere în aplicare (UE) 2020/1197, Anexa V, Secţiunea 10), baza de impozitare serveşte
calculului TVA (art. 289).

Valoarea statistică este valoarea mărfurilor **la frontiera statului membru de import** şi, pentru
mărfuri puse în liberă circulaţie, se utilizează chiar valoarea în vamă. De aceea ea **conţine deja
transportul extern** şi, în cazul simplu, **coincide numeric cu valoarea în vamă** — dar coincide cu
*baza de impozitare* numai când nu există taxă vamală, accize sau cheltuieli accesorii ulterioare
frontierei.

Diferă când: (a) există taxă vamală sau accize — se adaugă la baza TVA, dar nu la valoarea statistică;
(b) există transport intern de la frontieră până la primul loc de destinaţie, nedeclarat în vamă — se
adaugă la baza TVA (alin. (2)), dar nu la valoarea statistică; (c) marfa intră în UE prin alt stat
membru şi se vămuieşte în România; (d) există reduceri cunoscute la data exigibilităţii (alin. (3)).

> **Regula de operare:** baza contabilizată trebuie să fie **identică cu baza din DVI** (elementul de
> calcul al TVA, poziţia B00), nu cu netul facturii externe. Nu se recalculează, se **transcrie**.

### Transportul: intră în două locuri diferite, fără să fie dublă înregistrare

1. **Fiscal** — intră în baza TVA la import (art. 289), care este doar o mărime de calcul; nu
   debitează niciun cont de stoc.
2. **Contabil** — intră în **costul de achiziţie** al mărfii. OMFP 1802/2014 pct. 6: „costul de
   achiziţie al bunurilor cuprinde preţul de cumpărare, taxele de import şi alte taxe (cu excepţia
   acelora pe care persoana juridică le poate recupera de la autorităţile fiscale), **cheltuielile de
   transport, manipulare** şi alte cheltuieli care pot fi atribuibile direct achiziţiei bunurilor
   respective […] Cheltuielile de transport sunt incluse în costul de achiziţie şi atunci când funcţia
   de aprovizionare este externalizată.”

Dubla înregistrare apare **doar** dacă transportul e capitalizat de două ori pe latura de stoc — o
dată prin factura de transport pusă direct pe 371 şi încă o dată printr-o linie de landed cost.
Alegeţi una dintre variante:

```
Varianta A (prin landed cost, recomandată când marfa e deja recepţionată):
    Dr 628/624 analitic „transport de repartizat” = Cr 401      la factura transportatorului
    Dr 371                                        = Cr 628/624  la validarea landed cost-ului

Varianta B (direct pe stoc, fără landed cost):
    Dr 371 = Cr 401
```

**TVA la import nu măreşte costul stocului** — pct. 6 exclude explicit taxele recuperabile de la
autorităţile fiscale.

### Transportul aferent importului este scutit de TVA

**Art. 294 alin. (1) lit. d):** „Sunt scutite de taxă: […] prestările de servicii, **inclusiv
transportul şi serviciile accesorii transportului** […] dacă acestea sunt **direct legate de importul
de bunuri şi valoarea acestora este inclusă în baza de impozitare a bunurilor importate potrivit
art. 289**.”

Scutirea nu este opţională. Dacă valoarea transportului a fost efectiv inclusă în baza din DVI,
transportatorul trebuie să factureze **fără TVA**, cu menţiunea scutirii. Dacă valoarea **nu** a fost
inclusă în baza importului, condiţia nu e îndeplinită şi transportatorul facturează normal, cu cota
standard.

Justificarea scutirii se face cu documentele prevăzute de instrucţiunile aprobate prin ordin al
ministrului finanţelor (HG 1/2016, pct. 65) — în practică transportatorul solicită copie după DVI-ul
care dovedeşte includerea. TVA facturată pe o operaţiune scutită riscă să fie respinsă la deducere în
control.

### Cotele aplicabile

Cota se ia la data faptului generator, adică la data acceptării declaraţiei vamale (art. 285
alin. (1)–(2)): **21% standard**, **11% redusă** (art. 291, astfel cum a fost modificat prin Legea
141/2025, în vigoare de la 1 august 2025). Cota redusă acoperă, între altele, **alimentele de bază** —
atenţie la importurile de produse alimentare, unde taxa de achiziţie implicită a companiei (de regulă
cea standard) nu este cota corectă.

Biroul vamal nu este partener
------------------------------

Întrebare recurentă la implementare: *se creează câte un partener pentru fiecare birou vamal, ca să i
se urmărească soldul?* **Nu.**

### Birourile vamale nu au CUI propriu

Entitatea juridică este **Autoritatea Vamală Română** — instituţie publică cu personalitate juridică
în subordinea Ministerului Finanţelor (Legea 268/2021). Direcţiile regionale vamale şi birourile ori
punctele vamale de interior se înfiinţează şi se desfiinţează **prin ordin al preşedintelui AVR**,
cele de frontieră prin hotărâre de Guvern. Sunt structuri în subordine, nu entităţi juridice separate.

Ce are fiecare birou vamal este un **cod de nomenclator**, nu un cod fiscal: cod ANAF plus cod de
birou vamal în format COL. Localizarea nativă îl modelează ca `Selection`, nu ca `res.partner` — vezi
`CUSTOMS_OFFICES` din `l10n_ro_edi_stock/models/stock_picking.py`, de forma
`('12801', "BVI Alba Iulia (ROBV0300)")`.

### Soldul se urmăreşte pe cont, nu pe partener

Taxa vamală, accizele şi TVA-ul vamal se varsă la **bugetul de stat, prin Trezorerie**, pe conturi de
venituri bugetare. Nu există o relaţie de tip furnizor cu biroul vamal.

Contrapartida este contul **446 „Alte impozite, taxe şi vărsăminte asimilate”**, cont de decontare cu
bugetul statului. Funcţiunea din OMFP 1802/2014 este explicită: se creditează cu „valoarea **taxelor
vamale aferente aprovizionărilor din import** (213, 214, 301, 302, 303, **371**, 381)”, se debitează
cu „plăţile efectuate la bugetul de stat […] (512)”, iar „soldul contului reprezintă sumele datorate
bugetului statului”.

Soldul pe care doriţi să-l urmăriţi **există deja** — pe cont, nu pe o fişă de terţ. Urmărirea per
declaraţie se face prin reconciliere pe 446, cu **MRN-ul ca ancoră**: modulul scrie numărul de DVI în
`dvi_number` pe landed cost şi îl propagă ca `ref` pe nota contabilă, tocmai ca linia din extrasul
bancar să poată fi potrivită cu obligaţia.

Un partener „Vama” ar adăuga doar o fişă de terţ care nu se închide niciodată prin facturi.

### Cine este totuşi partener

**Comisionarul vamal (brokerul).** El emite factură, are CUI şi are sold pe 401. Onorariul lui este o
cheltuială cu serviciile (622/628), nu o datorie către un organism public — şi **nu se operează prin
wizardul DVI**.

Se foloseşte mecanismul nativ Odoo, care rezolvă deja tot ce trebuie: produs de tip serviciu cu
**„Is a Landed Cost”** bifat, pus pe factura brokerului. Linia se marchează automat ca linie de landed
cost, iar pe factură apare butonul **„Create Landed Costs”**, care creează un `stock.landed.cost` legat
de factură prin `vendor_bill_id`.

```
Factura brokerului:        Dr 628  = Cr 401     onorariu
                           Dr 4426 = Cr 401     TVA deductibilă
Landed cost din factură:   Dr 371  = Cr 628     soldează contul de tranzit
```

Aşa obţineţi partener, scadenţar, TVA deductibilă şi reconciliere — toate native. **Switch-ul de
politică contabilă este chiar butonul:** dacă onorariul nu se capitalizează, nu apăsaţi „Create Landed
Costs” şi factura rămâne cheltuială pe 628. Landed cost-urile create astfel intră automat şi sub
protecţia FIFO din `l10n_ro_invoice_dvi_protect`, care verifică legătura `vendor_bill_id`.


Rămâne pentru **comisionul datorat autorităţii vamale**, nu pentru onorariul brokerului. Este creditat
pe un cont **446** — datorie faţă de bugetul de stat.

> **Schimbare în 19.0.1.3.0.** Până la această versiune, comisionul era creditat pe **447**. Funcţiunea
> contului 447 „Fonduri speciale — taxe şi vărsăminte asimilate” din OMFP 1802/2014 îl rezervă
> datoriilor „către **alte organisme publice**” şi îl arată creditat **exclusiv prin 635**; nu apare
> nicăieri creditat prin conturi de stoc.
>
> ⚠️ **Migrare.** Produsul folosit pentru comision este memorat în parametrul de sistem
> `dvi.customs_commission_product_id`, deci schimbarea se aplică **numai instalărilor noi**. Pe bazele
> existente produsul rămâne pe 447, cu istoric pe el — contul **nu** este repoziţionat automat, ca să
> nu se rescrie tăcut înregistrări deja făcute. Contul se schimbă manual pe produs, după ce soldul de
> 447 a fost închis.
