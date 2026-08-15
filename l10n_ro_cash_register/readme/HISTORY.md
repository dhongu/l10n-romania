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
