# Fișa consultant: Costuri adiționale la achiziție (l10n_ro_stock_account)

## 1. Scop business

Cheltuielile de transport, manipulare sau vamă, facturate separat de marfă, se adaugă la costul de
achiziție al stocului: Dr 371 Mărfuri. Cu `l10n_ro_stock_account`, contul de stoc vine de pe
locația și categoria produsului, iar creditul este contul de cheltuieli (clasa 6) al liniei de
cost, completat din factura transportatorului.

Modulul adaugă, la documentul standard Odoo **Costuri adiționale**:

- **completarea automată** a costului creat din factura de furnizor: recepțiile comenzii de
  achiziție și contul fiecărei linii se iau din factură;
- **contul din locație** pentru nota de evaluare (locația de destinație la intrări, cea sursă la
  ieșiri) și poziția fiscală a jurnalului;
- opțional, **rutarea creditului clasei 6 printr-un cont intermediar tehnic**, pe companie: o notă
  cu două perechi echilibrate (stoc / intermediar și intermediar / 6xx).

Fișa tratează trei situații, de la cea simplă la cele cu stoc mișcat între recepție și
costul adițional:

1. fluxul complet: comandă, recepție, factura mărfii, factura transportatorului, cost adițional;
2. stoc **rezervat** pentru o vânzare când se validează costul;
3. stoc **deja vândut** când se validează costul.

## 2. Bază legală și context

- **OMFP 1802/2014**, costul de achiziție: cheltuielile de transport, manipulare și alte cheltuieli
  direct atribuibile achiziției intră în costul stocului.
- Odoo capitalizează costul adițional **doar pe cantitatea rămasă în stoc** la data validării
  (`remaining_qty` a recepției). Cantitatea rezervată este încă în stoc, deci se capitalizează.
  Cantitatea deja livrată nu se mai capitalizează: partea ei rămâne pe contul de cheltuieli.
- Dacă partea nescăpitalizată se reclasifică în costul vânzărilor (Dr 607 / Cr 6xx) este o decizie
  a politicii contabile a firmei; modulul nu face această notă.
- Contul intermediar este o soluție tehnică (exporturi care cer note echilibrate pe perechi de
  conturi); nu poate fi din clasa 6, iar firma îl definește prin politica contabilă.
- *De verificat cu Pacioli înainte de aprobarea fișei: tratamentul părții vândute (rămâne pe 6xx
  sau se mută pe 607).*

## 3. Utilizatori și roluri

| Rol | Ce face |
|---|---|
| Administrator contabil | Alege metoda și contul intermediar în Setări |
| Contabil | Validează costurile adiționale, verifică notele și tratează partea vândută |
| Operator de stoc | Creează costul adițional din factură sau din recepție |

## 4. Conturi și date implicate

| Cont | Rol |
|---|---|
| 371 Mărfuri | Cont de evaluare (Dr), din locație sau din categoria produsului |
| 607 / 624 | Contul de cheltuieli al liniei de cost (Cr), din factura transportatorului |
| 473 / 482 (analitic tehnic) | Cont intermediar opțional, cu sold zero; nu poate fi clasa 6 |
| 609 | Nu se rutează niciodată prin contul intermediar |

Date: produs stocabil cu evaluare în timp real (FIFO sau cost mediu), produs de serviciu cu **Este cost
adițional** bifat, jurnal de stoc.

## 5. Configurare inițială

1. *Contabilitate → Configurare → Setări → România*: **Metoda pentru creditul clasei 6 la costuri
   adiționale**: *Standard* (implicit) sau *Prin cont intermediar*; pentru a doua, completați
   **Contul intermediar**.
2. Produsul de transport: serviciu, **Este cost adițional**, cu contul de cheltuieli.
3. Marfa: stocabilă, categorie cu evaluare în timp real și cont de evaluare, jurnal de stoc.

![Setări, blocul România: Metodă cost adițional clasa 6 = Standard](../static/description/01_settings_landed_cost.png)

## 6. Flux de utilizare

### Scenariul 1 — Fluxul complet

Marfa: 10 buc. × 100 lei = 1.000 lei. Transport: 100 lei.

1. **Comanda de achiziție** către furnizor, 10 buc. × 100 lei, **Confirmă comanda**.

![Comanda de achiziție confirmată](../static/description/02_purchase_order.png)
2. **Recepția**: **Validează**. Fără bifa **Aviz** nu se postează notă de stoc la recepție; intrarea
   se postează la factură. Cu **Aviz**, recepția postează Dr 371 / Cr 408.

![Recepția validată](../static/description/03_receipt.png)
3. **Factura mărfii** (**Creează factură** din comandă, apoi **Confirmă**): Dr 371 = 1.000 lei
   (cu TVA, după caz) / Cr 401.

![Factura furnizorului de marfă, 10 buc. × 100 lei](../static/description/04_goods_bill.png)
4. **Factura transportatorului**: linie cu produsul de transport (**Este cost adițional**), 100 lei,
   cont de cheltuieli; **Confirmă**.

![Factura transportatorului cu butonul Creați costuri adiționale](../static/description/05_transport_bill_button.png)
5. **Creați costuri adiționale** din factura transportatorului. Dacă factura nu are comandă de
   achiziție, recepția se adaugă manual în **Transferuri**. Alegeți **Jurnalul**.
6. **Calculează**, apoi **Validează**.

![Costul adițional validat, cu recepția în Transferuri](../static/description/06_landed_cost_form.png)

Nota costului adițional (metoda *Standard*): **Dr 371 100 / Cr 6xx 100**. Valoarea recepției crește la
1.100 lei.

![Nota standard: Dr 371 100 / Cr 624 100](../static/description/07_note_standard.png)

Cu metoda *Prin cont intermediar*, aceeași operațiune dă patru linii: Dr 371 100 / Cr intermediar 100 și
Dr intermediar 100 / Cr 6xx 100; soldul intermediarului este 0.

![Nota prin cont intermediar: două perechi de câte 100 lei](../static/description/08_note_intermediary.png)

### Scenariul 2 — Stoc rezervat pentru o vânzare

Din cele 10 buc. recepționate, 4 sunt rezervate pe o livrare încă nevalidată (stare *Pregătit*).

![Livrarea de 4 buc., rezervată și nevalidată (Pregătit)](../static/description/09_delivery_reserved.png)

1. Validați costul adițional de 100 lei ca în Scenariul 1.
2. **Verificați:** nota este tot **Dr 371 100 / Cr 6xx 100**: stocul rezervat este încă în stoc, deci
   se capitalizează integral. Rezervarea nu se modifică.

![Nota pentru stocul rezervat: Dr 371 100 / Cr 624 100](../static/description/10_note_reserved.png)
3. Validați apoi livrarea. Cele 4 buc. ies la **110 lei** bucata (100 + 10 cost adițional), adică 440
   lei în costul vânzărilor: costul adițional urmărește marfa.

### Scenariul 3 — Stoc deja vândut

Din cele 10 buc., 4 au fost livrate și validate înainte de costul adițional (livrarea a ieșit la
100 lei/buc., 400 lei).

![Livrarea de 4 buc., validată (Efectuat)](../static/description/11_delivery_sold.png)

1. Validați costul adițional de 100 lei.
2. **Verificați:** nota este **Dr 371 60 / Cr 6xx 60**, adică doar cele 6 buc. rămase în stoc (6/10 din
   100). Cu metoda *Prin cont intermediar*: Dr 371 60 / Cr intermediar 60 și Dr intermediar 60 / Cr 6xx 60.

![Costul adițional validat după livrare](../static/description/12_landed_cost_sold.png)

![Nota pentru stocul vândut: Dr 371 60 / Cr 624 60](../static/description/13_note_sold.png)
3. **Atenție:** cele 40 lei aferente celor 4 buc. vândute **rămân pe contul de cheltuieli** al liniei
   (6xx) și livrarea nu se reevaluează (rămâne 400 lei). Contabilul decide dacă îi reclasifică în costul
   vânzărilor (Dr 607 / Cr 6xx) conform politicii firmei.
4. Dacă **toată** cantitatea a fost vândută, costul adițional se validează, dar nu se postează nicio
   linie: tot costul rămâne pe 6xx.

### Note de monografie (10 buc., transport 100 lei)

| Situație | Debit | Credit | Sumă |
|---|---|---|---|
| Cost adițional, tot stocul în gestiune | 371 | 6xx | 100,00 |
| Cost adițional, 4 rezervate | 371 | 6xx | 100,00 |
| Cost adițional, 4 vândute | 371 | 6xx | 60,00 |
| Cost adițional, toate vândute | | | 0 (rămâne pe 6xx) |
| Metoda intermediar (oricare din cele de mai sus) | 371 / intermediar | intermediar / 6xx | suma capitalizată |

## 7. Legături cu alte module / declarații

- `l10n_ro_stock_account`: evaluarea stocului, conturile din locație, tipul mișcării.
- `stock_landed_costs` (standard Odoo): documentul, metodele de împărțire.
- Pentru companiile cu `deltatech_obyc`, modulul echivalent este `deltatech_obyc_landed_cost`.
- Nu generează declarații; nota intră în balanță și în fișa contului 371.

## 8. Verificări pentru consultant

- Suma capitalizată = cost × (cantitatea rămasă în stoc / cantitatea recepției).
- Cantitatea rezervată nu scade capitalizarea; cantitatea livrată da.
- Valoarea recepției crește cu **tot** costul (1.000 → 1.100), chiar dacă o parte nu a fost capitalizată:
  soldul contului 371 urmează notele postate (în Scenariul 3: 1.000 + 60 − 400 = 660 lei pentru 6 buc.).
- La metoda intermediar, soldul contului intermediar este 0.
- Costul creat din factură: contul liniei este cel din factura transportatorului.

## 9. Mesaje de eroare frecvente

| Situație | Cauză | Remediere |
|---|---|---|
| `Please define Transfers on which those additional costs should apply.` | Factura transportatorului nu are comandă de achiziție | Adăugați recepțiile manual în **Transferuri** |
| Costul nu postează nicio linie | Toată cantitatea recepției a fost deja vândută | Tratați costul pe 6xx sau reclasificați conform politicii firmei |
| Nu apare rutarea prin intermediar | Metoda e *Standard* sau contul lipsește | Setări → România |

## 10. Capturi de ecran

| Fișier | Ce arată |
|---|---|
| `01_settings_landed_cost.png` | Setări: metoda pentru creditul clasei 6 |
| `02_purchase_order.png` | Comanda de achiziție |
| `03_receipt.png` | Recepția validată |
| `04_goods_bill.png` | Factura mărfii |
| `05_transport_bill_button.png` | Factura transportatorului, butonul Creați costuri adiționale |
| `06_landed_cost_form.png` | Costul adițional validat |
| `07_note_standard.png` | Nota Dr 371 / Cr 624 (100 lei) |
| `08_note_intermediary.png` | Nota prin cont intermediar |
| `09_delivery_reserved.png` | Livrare rezervată, nevalidată |
| `10_note_reserved.png` | Nota pentru stocul rezervat (100 lei) |
| `11_delivery_sold.png` | Livrare validată (stoc vândut) |
| `12_landed_cost_sold.png` | Costul adițional după vânzare |
| `13_note_sold.png` | Nota pentru stocul vândut (60 lei) |

## 11. Observații pentru manual

- Costul adițional se validează cât mai aproape de recepție: după vânzare, partea vândută nu se mai
  capitalizează.
- Stocul rezervat nu influențează costul adițional.
- Partea vândută rămâne pe 6xx: manualul trebuie să spună că reclasificarea în 607 este manuală.
