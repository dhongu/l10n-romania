# Procedura generală de operare în Odoo pentru importuri de marfă cu locație de tranzit și Declarație Vamală de Import (DVI)

Prezentul capitol descrie fluxul complet, standardizat și optimizat de operare în sistemul Odoo pentru un import de marfă din afara Uniunii Europene, în regim **FOB**, cu recepție în locație virtuală de tranzit și vămuire prin Declarație Vamală de Import (DVI).

Fluxul asigură:
- Respectarea integrală a regulilor contabile românești (OMFP 1802/2014 și Legea 82/1991);
- Capitalizarea corectă a taxelor vamale în costul de achiziție al mărfurilor;
- Evidența separată a TVA-ului la import (deductibil);
- Calculul automat al diferențelor de curs valutar;
- Trasabilitate completă de la comandă până la stocul final.

## Pasul 1 – Crearea Comenzii de Achiziție (Purchase Order)

**Acțiune:**
Se creează o comandă de achiziție (PO) către furnizorul extern pentru articolele importate.

**Modul:**
`Purchasing → Purchase Orders`

**Impact:**
- Rezervă marfa în sistem.
- Nu generează nicio notă contabilă.

## Pasul 2 – Recepția în Locația de Tranzit (Inventory Receipt)

**Acțiune:**
Deoarece marfa este livrată în regim **FOB**, proprietatea se transferă la plecarea din țara de origine. Se efectuează recepția într-o locație virtuală/intermediară denumită **„Transit/In-Coming”**.

**Modul:**
`Inventory → Receipts`

**Monografie contabilă (automată):**
- **327** (Mărfuri în curs de aprovizionare) = **408** (Furnizori – facturi nesosite)
**Suma:** Valoarea totală în valută convertită la cursul BNR din **data recepției**.

## Pasul 3 – Înregistrarea Facturii de Marfă (Vendor Bill)

**Acțiune:**
Se înregistrează factura comercială primită de la furnizor și se asociază cu PO-ul creat la Pasul 1.

**Modul:**
`Accounting → Vendors → Bills`

**Monografie contabilă:**
- **408** (Furnizori – facturi nesosite) = **401.ext** (Furnizori externi)

Se închide contul 408 și se stabilește datoria fermă pe contul 401.ext la **cursul BNR din data emiterii facturii**.

## Pasul 4 – Plata Facturii și Diferențele de Curs Valutar

**Acțiune:**
Se efectuează plata facturii către furnizor (de obicei înainte de sosirea mărfii în vamă).

**Modul:**
`Accounting → Bank → Register Payment`

**Monografie contabilă:**
- **401.ext** (Furnizori externi) = **5124** (Banca în valută)
- **665** (Diferențe nefavorabile de curs) / **765** (Diferențe favorabile de curs)

**Observație:** Acesta este singurul moment în care se înregistrează automat diferențele de curs valutar.

## Pasul 5 – Înregistrarea DVI – Taxe și TVA (Journal Entry)

**Acțiune:**
După sosirea mărfii în vamă se înregistrează manual datele din DVI.

**Modul:**
`Accounting → Journal Entries`
**Referință:** MRN (Movement Reference Number) din DVI

**Monografie contabilă:**
- **4426** (TVA Deductibil) = **446** — suma TVA B00
- **371.tranzit** (Taxe Vamale) = **446** — suma taxă vamală A00

> **Nu este nevoie de un cont/partener „401.Vama”.** Taxele şi TVA-ul vamal se varsă la bugetul de
> stat prin Trezorerie, nu către un furnizor; contul de decontare este **446**, al cărui sold
> reprezintă chiar sumele datorate bugetului (OMFP 1802/2014, funcţiunea contului 446). Urmărirea per
> declaraţie se face prin reconciliere pe 446, cu MRN-ul ca referinţă — vezi capitolul „Biroul vamal
> nu este partener” din DESCRIPTION.
>
> Paşii 5 şi 6 de mai sus descriu varianta **manuală**, pentru fluxul cu locaţie de tranzit. Când se
> foloseşte wizardul modulului, nota se generează automat — vezi „Completarea wizardului DVI” mai jos.

## Pasul 6 – Plata Datoriei către Vamă

**Acțiune:**
Se efectuează plata efectivă a taxelor vamale și a TVA-ului la import către organele vamale (stingerea datoriei create la Pasul 5).

**Modul:**
`Accounting → Payments → Register Payment`
(sau `Accounting → Journal Entries` dacă se face manual)

**Monografie contabilă:**
- **446** = **5121** (Banca în RON) — suma totală (taxă vamală A00 + TVA B00)

**Observații:**
- Plata se face **exclusiv în RON**.
- Nu generează diferențe de curs valutar.
- După această plată, contul 446 rămâne cu sold zero pentru respectivul DVI.

## Pasul 7 – Repartizarea Costurilor Adiționale (Landed Costs)

**Acțiune:**
Se repartizează taxele vamale plătite asupra mărfii aflate încă în tranzit.

**Modul:**
`Inventory → Operations → Landed Costs`

**Acțiune:**
Se selectează nota contabilă din Pasul 5 și recepția din Pasul 2.

**Monografie contabilă:**
- **327** (Mărfuri în curs de aprovizionare) = **371.tranzit** (Cont clearing taxe) — suma taxă vamală A00

**Impact:**
Valoarea mărfii în tranzit crește cu valoarea taxelor vamale (capitalizare în costul de achiziție).

## Pasul 8 – Transferul Final în Depozit (Internal Transfer)

**Acțiune:**
După finalizarea vămuirii, se transferă marfa din locația de tranzit în depozitul fizic.

**Modul:**
`Inventory → Internal Transfers` (din „Transit” în „WH/Stock”)

**Monografie contabilă:**
- **371** (Mărfuri în depozit) = **327** (Mărfuri în curs de aprovizionare)

**Valoarea transferată include:**
Preț marfă (valută la cursul BNR recepție) + Taxe vamale A00.




# Incoterms – Reguli internaționale de livrare în comerțul exterior

Prezentul capitol explică regulile **Incoterms® 2020** (International Commercial Terms) emise de Camera Internațională de Comerț (ICC), care stabilesc clar **repartizarea costurilor, riscurilor și responsabilităților** între vânzător și cumpărător în contractele internaționale.

Cunoașterea Incoterm-ului este esențială pentru:
- Momentul transferului proprietății și riscului asupra mărfii;
- Stabilirea momentului recepției contabile în Odoo;
- Calculul corect al landed costs;
- Determinarea responsabilităților vamale și de transport.

## Principalele Incoterms utilizate la import (2020)

| Incoterm | Denumire completă                          | Momentul transferului riscului | Transport principal (pe mare/aer) | Vămuire export | Vămuire import | Asigurare | Recomandat pentru importuri în România |
|----------|--------------------------------------------|--------------------------------|-----------------------------------|----------------|----------------|-----------|----------------------------------------|
| **EXW**  | Ex Works (La fabrica / depozitul vânzătorului) | La preluarea mărfii de la sediul vânzătorului | Cumpărător | Vânzător | Cumpărător | Cumpărător | Doar când ai logistică proprie în China |
| **FCA**  | Free Carrier (Liber la transportator)      | Predare la transportator (de obicei depozit) | Cumpărător | Vânzător | Cumpărător | Cumpărător | Foarte folosit (mai avantajos decât EXW) |
| **FOB**  | Free On Board (Liber la bordul navei)      | După încărcarea pe navă (port de încărcare) | Cumpărător | Vânzător | Cumpărător | Cumpărător | **Cel mai folosit la importuri maritime din China** |
| **CFR**  | Cost and Freight (Cost + Freight)          | După încărcarea pe navă       | Vânzător  | Vânzător | Cumpărător | Cumpărător | Bun când vrei ca vânzătorul să se ocupe de freight |
| **CIF**  | Cost, Insurance and Freight (Cost + Asigurare + Freight) | După încărcarea pe navă | Vânzător | Vânzător | Cumpărător | Vânzător (minim) | Folosit când vrei asigurare inclusă de vânzător |
| **DAP**  | Delivered at Place (Livrat la loc)         | La sosirea în locul convenit (ex: depozitul tău) | Vânzător | Vânzător | Cumpărător | Vânzător | Bun pentru transport rutier / aerian |
| **DDP**  | Delivered Duty Paid (Livrat cu taxe vamale plătite) | La sosirea în depozitul cumpărătorului | Vânzător | Vânzător | **Vânzător** | Vânzător | Vânzătorul plătește taxa vamală + TVA |

### Impactul Incoterm-ului asupra procedurii Odoo

| Incoterm | Momentul recepției contabile (Pasul 2) | Cine plătește taxele vamale + TVA | Landed Costs (Pasul 7) | Observații |
|----------|----------------------------------------|------------------------------------|------------------------|----------|
| **EXW**  | La preluarea de la furnizor            | Cumpărător                         | Include transport China–RO + taxe | Cel mai mare efort logistic |
| **FCA**  | La predarea către transportator        | Cumpărător                         | Include transport + taxe | Recomandat în locul EXW |
| **FOB**  | La încărcarea pe navă (Bill of Lading) | Cumpărător                         | Include freight + taxe | **Cel mai frecvent la importuri maritime** |
| **CFR / CIF** | La încărcarea pe navă              | Cumpărător                         | Include doar taxe (freight deja plătit de vânzător) | Freight inclus în preț |
| **DAP**  | La sosirea în România (depozit)        | Cumpărător                         | Doar taxe vamale | Riscul rămâne la vânzător până la graniță |
| **DDP**  | La sosirea în depozitul tău            | **Vânzătorul**                     | Nu se fac landed costs pentru taxe | Cel mai simplu pentru cumpărător |

### Recomandarea pentru importuri din China (2026)

- **Cel mai folosit:** **FOB** (echilibru bun între preț și control).
- **Cel mai avantajos logistic:** **FCA** (mai modern și mai sigur decât FOB).
- **Cel mai simplu (dar mai scump):** **DDP** (vânzătorul se ocupă de tot, inclusiv vamă).
- **De evitat dacă nu ai experiență:** **EXW** (prea multe responsabilități pe tine încă din China).

**Notă importantă:**
Incoterm-ul trebuie menționat explicit în comanda de achiziție (PO) și în factura furnizor. El determină direct modul în care se face recepția în Odoo și care costuri intră în landed costs.


# Completarea wizardului DVI — ce cifră unde

Wizardul se deschide cu butonul **„DVI”** de pe factura furnizorului extern. Are patru câmpuri de
sume, toate **editabile liber**. Valorile se **transcriu din declaraţia vamală**, nu se recalculează
din factură.

| Câmp | Ce se pune | Sursa în DVI |
|---|---|---|
| **Taxă vamală** | taxa vamală datorată | poziţia **A00** |
| **Bază de impozitare** | baza pe care vama a calculat TVA-ul | baza poziţiei **B00** |
| **TVA plătit în vamă** | TVA-ul efectiv datorat | valoarea poziţiei **B00** |
| **Cotă TVA** | cota aplicată de vamă la data acceptării declaraţiei | din declaraţie |
| **Număr DVI** | MRN-ul declaraţiei | antetul declaraţiei |

> ⚠️ **Valoarea propusă nu este baza legală.** La deschiderea wizardului, câmpul „Bază de impozitare”
> este precompletat cu **netul facturii furnizorului** (`invoice.amount_untaxed_signed`). Este doar un
> punct de plecare comod, nu o determinare conform art. 289 — nu conţine taxa vamală, comisionul şi
> nici cheltuielile accesorii. Vezi capitolul „Baza de impozitare a TVA la import” din DESCRIPTION.

## Erori frecvente şi cum se evită

**Baza propusă lăsată neatinsă.** Cazul tipic: factura externă este de 58.927,59 lei, iar în DVI baza
este 67.663 lei, pentru că valoarea în vamă include şi transportul extern. Diferenţa de 8.735,41 lei
înseamnă TVA subevaluat, care se propagă în decont. **Comparaţi întotdeauna baza propusă cu baza din
DVI înainte de a confirma.**

**Valoarea statistică folosită ca bază.** Valoarea statistică şi baza de impozitare sunt mărimi
diferite; pot coincide numeric, dar nu întotdeauna. Se ia baza poziţiei B00, nu valoarea statistică.

**TVA nerecalculat după modificarea bazei.** Câmpul „TVA plătit în vamă” **nu se recalculează
automat** la schimbarea bazei sau a cotei — nu există `onchange` în wizard. Dacă modificaţi baza,
**modificaţi şi valoarea TVA**, altfel nota contabilă se postează cu suma veche, fără nicio eroare.

**Cota implicită greşită.** Cota propusă este taxa de achiziţie implicită a companiei (de regulă cea
standard). Pentru mărfuri cu cotă redusă — alimente de bază, medicamente, cărţi — cota corectă este
cea redusă. Verificaţi câmpul înainte de confirmare.

**Transportul uitat din cost.** Dacă transportul extern este facturat separat, el intră în costul de
achiziţie al mărfii (OMFP 1802/2014 pct. 6) — printr-o linie de landed cost sau direct pe stoc, **o
singură dată**. Faptul că aceeaşi sumă apare şi în baza TVA nu este o dublare: baza TVA nu debitează
niciun cont de stoc.

## Monografia generată de modul

**La validarea wizardului** se creează un `stock.landed.cost` legat de recepţiile comenzii de
achiziţie, cu câte o linie pentru taxa vamală şi pentru comision.

**La validarea landed cost-ului:**

```
Dr 371/301  = Cr 446    taxa vamală      -> intră în costul stocului
Dr 4426     = Cr 446    TVA la import    -> deductibilă, NU măreşte costul
```

Nota contabilă primeşte ca referinţă **numărul de DVI** (MRN), nu secvenţa internă, astfel încât plata
din extrasul bancar să poată fi reconciliată pe contul 446 per declaraţie.

**La descărcarea gestiunii:** `Dr 607 = Cr 371`.

> Din 19.0.1.3.0 comisionul vamal se creditează pe **446**, nu pe 447. Pe bazele existente contul nu se
> schimbă automat — vezi nota de migrare din DESCRIPTION, capitolul „Biroul vamal nu este partener”.

## Onorariul comisionarului vamal (brokerul)

**Nu se operează prin wizardul DVI.** Brokerul e furnizor obişnuit: are CUI, emite factură cu TVA şi
are sold pe 401.

1. Creaţi un produs de tip **serviciu** cu bifa **„Is a Landed Cost”** (fila Achiziţii), cu cont de
   cheltuială 628 (sau 622).
2. Înregistraţi factura brokerului pe acest produs, cu TVA-ul lui. Linia se marchează automat ca linie
   de landed cost.
3. **Dacă politica contabilă prevede capitalizarea** onorariului în costul mărfii: apăsaţi butonul
   **„Create Landed Costs”** de pe factură, selectaţi recepţia şi validaţi.
   **Dacă nu se capitalizează:** nu apăsaţi nimic — factura rămâne cheltuială pe 628.

```
Factura brokerului:        Dr 628  = Cr 401     onorariu
                           Dr 4426 = Cr 401     TVA deductibilă
Landed cost din factură:   Dr 371  = Cr 628     doar dacă se capitalizează
```

Butonul **este** switch-ul de politică contabilă; nu există un câmp separat de configurat.

## Verificări după validare

- [ ] Baza din nota contabilă corespunde bazei poziţiei B00 din DVI.
- [ ] TVA-ul din 4426 corespunde valorii B00 din DVI.
- [ ] Costul unitar al produsului a crescut cu (taxă vamală + comision + transport) / cantitate.
- [ ] Nota contabilă are ca referinţă MRN-ul declaraţiei.
- [ ] Transportul extern apare o singură dată în costul stocului.
