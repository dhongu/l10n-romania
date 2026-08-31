Acest modul extinde raportul de factură standard din Odoo pentru a se conforma cerințelor specifice din România și pentru a oferi opțiuni suplimentare de personalizare.

### Funcționalități principale:

- **Detalii linii factură**:
    - Afișarea prețului unitar fără TVA.
    - Afișarea valorii TVA pe fiecare linie.
    - Afișarea totalului cu taxe pe fiecare linie (configurabil).
    - Numerotarea automată a liniilor de factură (Ord).
    - Opțiune de a elimina numele produsului de pe linie dacă există o descriere specifică.
    - Afișarea prețului fără discount.

- **Informații suplimentare pe document**:
    - Câmpuri dedicate pentru **Delegat** și **Mijloc de transport**.
    - Afișarea textului legal privind scutirea de semnătură și ștampilă (conform Codului Fiscal).
    - Posibilitatea de a adăuga un text adițional de la partener pe factură (`info_for_invoice`).
    - Vizibilitatea configurabilă pentru email, telefon și marcaje în adresa facturii.
    - Afișarea informațiilor despre livrări (Pickings) și AWB-uri direct pe factură.
    - Inserarea logoului **Coface** la finalul facturii (activabil din setări).

- **Gestiune documente corelate**:
    - **Chitanță, dispoziție de plată și dispoziție de încasare** tipărite din plată (raportul „Voucher / Payment" pe `account.payment`), cu titlul potrivit tipului de plată și cu suma în cifre și în litere.
    - Pentru plățile pe jurnal de casă, documentul iese ca formular de casierie complet: **codul formularului** (14-4-4 la plată, 14-4-1 la încasare), **casieria**, rândul pentru **actul de identitate** al beneficiarului la plăți, și **cele trei semnături** — conducătorul unității, casierul și beneficiarul. Pentru plățile bancare, aceste elemente nu se tipăresc, nefiind vorba de un document de casă.
    - Gestionarea corectă a semnelor pentru stornări (Credit Notes).

- **Rapoarte dedicate**:
    - Raport de factură în limba companiei, indiferent de limba partenerului.

- **Configurare flexibilă**:
    - Numeroase opțiuni în setările de facturare pentru a activa sau dezactiva elementele menționate mai sus (Sarcini delegat, comentarii plată, index linii, etc.).

### Cerințe tehnice:
- Necesită instalarea bibliotecii `num2words`.
- Recomandat: `pip3 install num2words==0.5.12`
