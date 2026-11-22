Recalculează evaluarea FIFO pe locație a mișcărilor de stoc, în ordine cronologică, și corectează
valorile greșite din trecut, cu nota contabilă aferentă.

Cu FIFO pe locație (`l10n_ro_stock_account`), o ieșire evaluată greșit (pe stoc negativ
necompensat, printr-o operație cu dată în urmă sau printr-un bug reparat între timp) își păstrează
valoarea, iar soldul conturilor de stoc nu mai corespunde cu valoarea stocului. Modulul refă
calculul și arată, pe fiecare mișcare, valoarea actuală, valoarea corectă și diferența.

**Cum se recalculează**

- Mișcările efectuate ale fiecărui produs FIFO se parcurg în ordine cronologică, cu o coadă FIFO
  pentru fiecare locație.
- Recepțiile și livrările care nu sunt pe bază de aviz se ordonează după data facturii.
- Exercițiul unei diferențe e cel al notei de stoc originale a mișcării, nu cel al facturii.
- Valoarea intrărilor din facturi și costuri de achiziție rămâne cea înregistrată; se recalculează
  ieșirile, transferurile interne (valoarea trece din gestiunea sursă în cea destinație) și
  retururile de la clienți (după valoarea livrării corectate).
- O ieșire făcută pe stoc negativ se evaluează la prețul intrărilor care o acoperă în aceeași
  locație. Dacă nicio intrare ulterioară nu o acoperă, valoarea ei rămâne, iar aplicarea nu înregistrează
  o cantitate negativă nouă pe mișcare, ca să nu fie compensată la o recepție viitoare.

Diferențele de până la un prag ales în rulare (implicit 0,05 lei pe mișcare) sunt rotunjiri ale
prețului unitar și nu se listează și nu se corectează.

**Rularea de probă** nu modifică nimic: arată diferențele pe mișcări și un control pe fiecare cont
de stoc (valoarea stocului recalculată, soldul contului, soldul după corecție și diferența rămasă).

**La aplicare** se corectează valorile mișcărilor și se postează o singură notă de corecție, la
data aleasă, în jurnalul de stoc:

| Diferența | Înregistrare |
|---|---|
| Ieșire din exercițiul curent | pe conturile notei originale a ieșirii (de exemplu 607 = 371), în roșu dacă ieșirea a fost supraevaluată |
| Ieșire dintr-un exercițiu închis | 1174 în locul contului de cheltuieli (OMFP 1802/2014, pct. 67 alin. 2), în negru, cu conturile inversate dacă ieșirea a fost supraevaluată (371 = 1174) |
| Transfer între gestiuni | 371 gestiunea destinație = 371 gestiunea sursă, indiferent de exercițiu |

O corecție pe 1174 cere de regulă declarația de impozit pe profit rectificativă pentru anul la care
se referă eroarea (art. 19 alin. 3 lit. a din Codul fiscal).

**Legătura cu verificarea stoc–contabilitate**

Modulul `l10n_ro_stock_account_check` compară valoarea mișcărilor cu soldurile din contabilitate și
aliniază contabilitatea la valoarea mișcărilor, considerând-o corectă. Recalcularea FIFO verifică
tocmai dacă valoarea mișcărilor e corectă. Ordinea recomandată: întâi recalcularea FIFO, apoi
verificarea stoc–contabilitate pentru diferențele rămase.

**Limitări**

- Costul produselor fabricate nu se recalculează după componentele corectate.
- Produsele evaluate pe loturi și liniile cu proprietar terț nu se recalculează.
- O rulare aplicată nu se poate anula: nota de corecție se stornează manual, iar valorile
  mișcărilor rămân cele corectate.
