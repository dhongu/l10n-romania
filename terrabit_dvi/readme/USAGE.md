# Capitolul 4: Procedura generală de operare în Odoo pentru importuri de marfă cu locație de tranzit și Declarație Vamală de Import (DVI)

Prezentul capitol descrie fluxul complet, standardizat și optimizat de operare în sistemul Odoo pentru un import de marfă din afara Uniunii Europene, în regim **FOB**, cu recepție în locație virtuală de tranzit și vămuire prin Declarație Vamală de Import (DVI).

Fluxul asigură:
- Respectarea integrală a regulilor contabile românești (OMFP 1802/2014 și Legea 82/1991);
- Capitalizarea corectă a taxelor vamale în costul de achiziție al mărfurilor;
- Evidența separată a TVA-ului la import (deductibil);
- Calculul automat al diferențelor de curs valutar;
- Trasabilitate completă de la comandă până la stocul final.

## 4.1. Pasul 1 – Crearea Comenzii de Achiziție (Purchase Order)

**Acțiune:**
Se creează o comandă de achiziție (PO) către furnizorul extern pentru articolele importate.

**Modul:**
`Purchasing → Purchase Orders`

**Impact:**
- Rezervă marfa în sistem.
- Nu generează nicio notă contabilă.

## 4.2. Pasul 2 – Recepția în Locația de Tranzit (Inventory Receipt)

**Acțiune:**
Deoarece marfa este livrată în regim **FOB**, proprietatea se transferă la plecarea din țara de origine. Se efectuează recepția într-o locație virtuală/intermediară denumită **„Transit/In-Coming”**.

**Modul:**
`Inventory → Receipts`

**Monografie contabilă (automată):**
- **327** (Mărfuri în curs de aprovizionare) = **408** (Furnizori – facturi nesosite)
**Suma:** Valoarea totală în valută convertită la cursul BNR din **data recepției**.

## 4.3. Pasul 3 – Înregistrarea Facturii de Marfă (Vendor Bill)

**Acțiune:**
Se înregistrează factura comercială primită de la furnizor și se asociază cu PO-ul creat la Pasul 1.

**Modul:**
`Accounting → Vendors → Bills`

**Monografie contabilă:**
- **408** (Furnizori – facturi nesosite) = **401.ext** (Furnizori externi)

Se închide contul 408 și se stabilește datoria fermă pe contul 401.ext la **cursul BNR din data emiterii facturii**.

## 4.4. Pasul 4 – Plata Facturii și Diferențele de Curs Valutar

**Acțiune:**
Se efectuează plata facturii către furnizor (de obicei înainte de sosirea mărfii în vamă).

**Modul:**
`Accounting → Bank → Register Payment`

**Monografie contabilă:**
- **401.ext** (Furnizori externi) = **5124** (Banca în valută)
- **665** (Diferențe nefavorabile de curs) / **765** (Diferențe favorabile de curs)

**Observație:** Acesta este singurul moment în care se înregistrează automat diferențele de curs valutar.

## 4.5. Pasul 5 – Înregistrarea DVI – Taxe și TVA (Journal Entry)

**Acțiune:**
După sosirea mărfii în vamă se înregistrează manual datele din DVI.

**Modul:**
`Accounting → Journal Entries`
**Referință:** MRN (Movement Reference Number) din DVI

**Monografie contabilă:**
- **4426** (TVA Deductibil) = **446 / 401.Vama** — suma TVA B00
- **371.tranzit** (Taxe Vamale) = **446 / 401.Vama** — suma taxă vamală A00

## 4.6. Pasul 6 – Plata Datoriei către Vamă

**Acțiune:**
Se efectuează plata efectivă a taxelor vamale și a TVA-ului la import către organele vamale (stingerea datoriei create la Pasul 5).

**Modul:**
`Accounting → Payments → Register Payment`
(sau `Accounting → Journal Entries` dacă se face manual)

**Monografie contabilă:**
- **401.Vama** = **5121** (Banca în RON) — suma totală (taxă vamală A00 + TVA B00)

**Observații:**
- Plata se face **exclusiv în RON**.
- Nu generează diferențe de curs valutar.
- După această plată, contul 401.Vama (sau 446) rămâne cu sold zero pentru respectivul DVI.

## 4.7. Pasul 7 – Repartizarea Costurilor Adiționale (Landed Costs)

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

## 4.8. Pasul 8 – Transferul Final în Depozit (Internal Transfer)

**Acțiune:**
După finalizarea vămuirii, se transferă marfa din locația de tranzit în depozitul fizic.

**Modul:**
`Inventory → Internal Transfers` (din „Transit” în „WH/Stock”)

**Monografie contabilă:**
- **371** (Mărfuri în depozit) = **327** (Mărfuri în curs de aprovizionare)

**Valoarea transferată include:**
Preț marfă (valută la cursul BNR recepție) + Taxe vamale A00.




# Capitolul 5: Incoterms – Reguli internaționale de livrare în comerțul exterior

Prezentul capitol explică regulile **Incoterms® 2020** (International Commercial Terms) emise de Camera Internațională de Comerț (ICC), care stabilesc clar **repartizarea costurilor, riscurilor și responsabilităților** între vânzător și cumpărător în contractele internaționale.

Cunoașterea Incoterm-ului este esențială pentru:
- Momentul transferului proprietății și riscului asupra mărfii;
- Stabilirea momentului recepției contabile în Odoo;
- Calculul corect al landed costs;
- Determinarea responsabilităților vamale și de transport.

## 5.1. Principalele Incoterms utilizate la import (2020)

| Incoterm | Denumire completă                          | Momentul transferului riscului | Transport principal (pe mare/aer) | Vămuire export | Vămuire import | Asigurare | Recomandat pentru importuri în România |
|----------|--------------------------------------------|--------------------------------|-----------------------------------|----------------|----------------|-----------|----------------------------------------|
| **EXW**  | Ex Works (La fabrica / depozitul vânzătorului) | La preluarea mărfii de la sediul vânzătorului | Cumpărător | Vânzător | Cumpărător | Cumpărător | Doar când ai logistică proprie în China |
| **FCA**  | Free Carrier (Liber la transportator)      | Predare la transportator (de obicei depozit) | Cumpărător | Vânzător | Cumpărător | Cumpărător | Foarte folosit (mai avantajos decât EXW) |
| **FOB**  | Free On Board (Liber la bordul navei)      | După încărcarea pe navă (port de încărcare) | Cumpărător | Vânzător | Cumpărător | Cumpărător | **Cel mai folosit la importuri maritime din China** |
| **CFR**  | Cost and Freight (Cost + Freight)          | După încărcarea pe navă       | Vânzător  | Vânzător | Cumpărător | Cumpărător | Bun când vrei ca vânzătorul să se ocupe de freight |
| **CIF**  | Cost, Insurance and Freight (Cost + Asigurare + Freight) | După încărcarea pe navă | Vânzător | Vânzător | Cumpărător | Vânzător (minim) | Folosit când vrei asigurare inclusă de vânzător |
| **DAP**  | Delivered at Place (Livrat la loc)         | La sosirea în locul convenit (ex: depozitul tău) | Vânzător | Vânzător | Cumpărător | Vânzător | Bun pentru transport rutier / aerian |
| **DDP**  | Delivered Duty Paid (Livrat cu taxe vamale plătite) | La sosirea în depozitul cumpărătorului | Vânzător | Vânzător | **Vânzător** | Vânzător | Vânzătorul plătește taxa vamală + TVA |

### 5.2. Impactul Incoterm-ului asupra procedurii Odoo

| Incoterm | Momentul recepției contabile (Pasul 2) | Cine plătește taxele vamale + TVA | Landed Costs (Pasul 7) | Observații |
|----------|----------------------------------------|------------------------------------|------------------------|----------|
| **EXW**  | La preluarea de la furnizor            | Cumpărător                         | Include transport China–RO + taxe | Cel mai mare efort logistic |
| **FCA**  | La predarea către transportator        | Cumpărător                         | Include transport + taxe | Recomandat în locul EXW |
| **FOB**  | La încărcarea pe navă (Bill of Lading) | Cumpărător                         | Include freight + taxe | **Cel mai frecvent la importuri maritime** |
| **CFR / CIF** | La încărcarea pe navă              | Cumpărător                         | Include doar taxe (freight deja plătit de vânzător) | Freight inclus în preț |
| **DAP**  | La sosirea în România (depozit)        | Cumpărător                         | Doar taxe vamale | Riscul rămâne la vânzător până la graniță |
| **DDP**  | La sosirea în depozitul tău            | **Vânzătorul**                     | Nu se fac landed costs pentru taxe | Cel mai simplu pentru cumpărător |

### 5.3. Recomandarea pentru importuri din China (2026)

- **Cel mai folosit:** **FOB** (echilibru bun între preț și control).
- **Cel mai avantajos logistic:** **FCA** (mai modern și mai sigur decât FOB).
- **Cel mai simplu (dar mai scump):** **DDP** (vânzătorul se ocupă de tot, inclusiv vamă).
- **De evitat dacă nu ai experiență:** **EXW** (prea multe responsabilități pe tine încă din China).

**Notă importantă:**
Incoterm-ul trebuie menționat explicit în comanda de achiziție (PO) și în factura furnizor. El determină direct modul în care se face recepția în Odoo și care costuri intră în landed costs.

