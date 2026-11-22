# Brief: l10n_ro_stock_fifo_recompute

## Cererea

„acum fă wizardul de recalculare FIFO” (22.11.2026), după analiza problemelor din
`l10n_ro_stock_account` și întrebarea „cum se pot corecta evaluările FIFO făcute greșit”.

Precizare ulterioară (22.11.2026): „la recepție și la livrare data trebuie să fie în
concordanță cu factura, dacă acestea nu au fost făcute pe bază de aviz”.

## Scop

Cu FIFO pe locație (`l10n_ro_stock_account`), ieșirile evaluate greșit în trecut (stoc negativ
necompensat, operații cu dată în urmă, buguri reparate între timp) rămân în `stock.move.value` și
în notele contabile, iar soldul conturilor de stoc nu mai corespunde cu valoarea stocului.
Contabilul nu are cum să afle ce valori sunt greșite și cu cât. Modulul recalculează FIFO
cronologic, arată diferențele pe fiecare mișcare și, la cerere, corectează valorile și postează
nota de corecție.

## Cine operează

Contabilul șef: grupul `account.group_account_manager` (Administrator contabilitate).

## Încadrare

- Suita și numele tehnic: `l10n-romania-oca`, `l10n_ro_stock_fifo_recompute`.
- Modul nou. Un instrument folosit ocazional, la corecții, deci nu în modulul de bază încărcat la
  toți clienții.
- `depends`: `l10n_ro_stock_account`, care are FIFO pe locație, tipul de mișcare RO
  (`l10n_ro_move_type`) și conturile pe tip de mișcare.
- Modele noi:
  - `l10n.ro.fifo.recompute`: rularea (companie, produse, date, stare, nota de corecție);
  - `l10n.ro.fifo.recompute.line`: diferența pe o mișcare;
  - `l10n.ro.fifo.recompute.check`: controlul pe un cont de stoc.
- Modele standard extinse: niciunul.

## Flux

1. *Contabilitate > Contabilitate > Închidere > Recalculare FIFO*, **Nou**.
2. Alege produsele sau categoriile (gol = toate produsele FIFO ale companiei), data notei de
   corecție, data de închidere a ultimului exercițiu și contul pentru exercițiile închise (1174).
3. **Calculează**: apar liniile cu diferențe și controlul pe conturile de stoc. Nu se scrie
   nimic în mișcări sau în contabilitate.
4. Contabilul verifică liniile, le poate filtra sau exporta și poate recalcula de câte ori vrea.
5. **Aplică**: se corectează valorile mișcărilor și se postează nota de corecție, legată de
   rulare.

## Criterii de acceptare

- **CA1:** O livrare făcută pe stoc negativ, evaluată la prețul standard (80), urmată de o
  recepție la 100 fără compensare: după **Calculează**, rularea are o linie pe livrare cu
  valoarea actuală 240, valoarea corectă 300 și diferența 60. Valoarea livrării nu se schimbă.
- **CA2:** O livrare evaluată greșit și un transfer intern între gestiuni cu conturi diferite:
  liniile arată Dr 607 / Cr 371 la livrare și Dr 371 destinație / Cr 371 sursă la transfer.
  Valoarea corectată a transferului se regăsește în ieșirile ulterioare din gestiunea destinație.
- **CA3:** Un retur de la client al unei livrări corectate primește valoarea livrării corectate,
  proporțional cu cantitatea.
- **CA4:** După **Aplică**, valorile mișcărilor sunt cele corecte, rularea trece în starea
  *Aplicat* și are o notă contabilă postată, în jurnalul de stoc, la data aleasă. Pe fiecare cont
  și produs, nota conține suma diferențelor. Diferențele negative se postează în roșu (storno).
- **CA5:** O diferență pe o ieșire datată până la data de închidere a exercițiului se postează pe
  contul ales pentru exerciții închise (1174), nu pe 607; un transfer intern din aceeași perioadă
  rămâne pe 371 destinație / 371 sursă.
- **CA6:** Controlul arată, pe fiecare cont de stoc, valoarea stocului recalculată, soldul
  contului pentru produsele rulării, soldul după corecție și diferența rămasă.
- **CA7:** O a doua rulare, după aplicarea primei, nu mai găsește diferențe.
- **CA8:** O recepție fără aviz are ca dată efectivă data facturii de achiziție, iar o livrare
  fără aviz data facturii de vânzare. Ordinea FIFO și încadrarea pe exercițiu folosesc data
  efectivă: o recepție validată după o livrare, dar facturată înaintea ei, acoperă livrarea.

## Cazuri-limită

- **Multi-companie:** se recalculează doar compania rulării; produsele se citesc cu acea companie.
- **Stoc negativ fără nicio intrare ulterioară:** valoarea actuală rămâne, linia e marcată „stoc
  negativ neacoperit”.
- **Producție (`production`):** valoarea intrării se păstrează; propagarea în costul produselor
  finite nu se face.
- **Produse evaluate pe loturi, linii cu proprietar terț, alte metode de cost decât FIFO:** se
  ignoră, ca în motorul FIFO.
- **Data notei într-o perioadă blocată:** aplicarea e refuzată de modul, cu un mesaj; nimic nu se
  scrie.
- **Aplicare repetată:** butonul **Aplică** apare doar în starea *Calculat*; o rulare aplicată nu
  se mai recalculează.
- **Sfârșitul exercițiului completat fără cont pentru exerciții închise:** calculul e refuzat.
- **Ștergerea unei rulări aplicate:** refuzată; rularea e urma notei de corecție.
- **Blocare lunară:** sfârșitul exercițiului închis propus implicit e sfârșitul ultimului exercițiu
  încheiat la data de blocare a companiei (blocare la 31.10.2026 → 31.12.2025), nu data de
  blocare; diferențele din anul curent rămân pe conturile notei originale.
- **Drepturi insuficiente:** meniul și modelele sunt doar pentru Administrator contabilitate.

## Decizii luate

| Decizie | Varianta aleasă | Motiv |
|---|---|---|
| Unde stă instrumentul | modul separat în `l10n-romania-oca` | ales de utilizator; folosit ocazional |
| Data notei de corecție | data aleasă în rulare, perioada curentă | Pacioli: corecția la data constatării (OMFP 1802, pct. 65) |
| Conturi în exercițiul curent | conturile notei originale ale ieșirii, pe net (fără 482) | Pacioli: pct. 67 alin. 1; în aceeași contabilitate 371.dest / 371.sursă direct |
| Exerciții închise | contul ales (1174) în locul contului de cheltuieli | Pacioli: pct. 67 alin. 2 |
| Valoarea intrărilor externe | `move.value` actual (factură, cost de achiziție) | e sursa de adevăr; se corectează doar ieșirile, transferurile și retururile |
| Stoc negativ | la prețul intrărilor care îl acoperă în aceeași locație | aceeași regulă ca la compensarea din motor |
| Data efectivă la recepție/livrare fără aviz | data primei facturi înregistrate de pe linia comenzii, altfel data transferului | cerința utilizatorului |
| Nota de corecție | o singură notă pe rulare, cumulată pe cont, produs și semn | trasabilitate; o notă pe mișcare ar fi prea multe |
| Scrierea valorii | direct `stock.move.value` | prin `value_manual` s-ar reapela evaluarea |

## Decizii deschise

Niciuna.

## În afara scopului

- Propagarea în costul produselor fabricate (MRP).
- Anularea unei rulări aplicate (nota se poate storna manual; valorile mișcărilor nu revin).
- Rulare în fundal pentru volume mari.
- Schimbarea datei notelor de stoc la recepție și livrare în modulul de bază.
- Redeschiderea lunilor închise.
