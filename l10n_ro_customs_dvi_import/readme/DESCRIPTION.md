Preia declarația vamală de import (DVI) direct din PDF-ul tipărit de **Sistemul Național de Import
(SNI)** și completează cu ea wizardul DVI de pe factura furnizorului, din modulul
`l10n_ro_customs_dvi`.

Din PDF se citesc:

- **MRN**-ul și data acceptării declarației, care devin numărul și data DVI-ului;
- **regimul vamal** (4000 sau 4200);
- **taxa vamală** A00, care intră în costul mărfii prin landed cost;
- **baza și TVA-ul** B00, transcrise din declarație, nu recalculate. La regimul 4200, B00 devine
  TVA-ul reținut ca garanție, iar importul rămâne scutit;
- cota de TVA, după care se propune taxa de achiziție;
- LRN-ul, data liberului de vamă, moneda și cursul vamal, facturile din documentele justificative
  (N380) și metoda de plată, afișate pentru control.

Înainte de completare, modulul verifică:

- documentul e o declarație de import tipărită de SNI;
- importatorul e compania curentă;
- declarația nu e deja înregistrată pe alt DVI;
- numărul de articole citite e cel din antet;
- sumele A00 și B00 de pe articole dau totalurile declarației.

Dacă o verificare pică, importul se oprește cu un mesaj și nu se completează nimic. Dacă factura
furnizorului nu apare printre facturile declarației, wizardul afișează un avertisment.

PDF-ul declarației se atașează pe DVI, cu un rezumat al valorilor citite în istoric.

Modulul are nevoie de biblioteca Python `pdfminer.six`.
