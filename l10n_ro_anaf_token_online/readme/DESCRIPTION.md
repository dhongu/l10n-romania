Tokenul SPV ANAF pentru e-Factura, și pe **Odoo Online**: modulul nu conține cod Python și se importă
ca arhivă zip (Aplicații > Importați modulul). Autorizarea cu certificatul digital se face o singură
dată, pe serverul Terrabit, care ține tokenul valabil și îl trimite în baza dumneavoastră. Nu
înregistrați o aplicație proprie la ANAF și nu reînnoiți tokenul manual.

- **Generează token (Terrabit)**, în *Setări > Facturare > E-Factura România*: deschide
  autorizarea ANAF pe serverul Terrabit. Primul clic activează serviciul Terrabit al bazei; apăsați
  din nou după câteva secunde.
- **Tokenul se completează singur**: Client ID, Client Secret, tokenul de acces, tokenul de
  reînnoire și datele lor de expirare se scriu pe firmă, în câmpurile standard e-Factura, imediat
  după autorizare și din nou după fiecare reînnoire. Firma se găsește după CUI.
- **Reînnoire într-un singur loc**: când sosește tokenul, acțiunea programată standard de reînnoire
  e-Factura se oprește, pentru că ANAF invalidează tokenul anterior la fiecare reînnoire. Tokenul îl
  reînnoiește serverul Terrabit.
- **Costul**: o autorizare costă 1 credit (1 credit = 1 EUR); reînnoirile sunt gratuite. Autorizarea
  apare în *Setări > Credite Terrabit > Consum credite*.
- **Butonul standard Generează token este ascuns**: ar porni o autorizare locală, cu aplicația ANAF
  proprie, și ar invalida tokenul reînnoit de Terrabit.

Modulul are nevoie de `deltatech_iap_online` (serviciile Terrabit), importat înainte. Serviciul
Terrabit apare în *Setări > Credite Terrabit*.

**Ce iese din baza dumneavoastră**: la activare, adresa și UUID-ul bazei, denumirea și CUI-ul
firmei; la autorizare, adresa webhook-ului care primește tokenul. Tokenul vine de la serverul
Terrabit, prin HTTPS, pe un URL de webhook secret.

### Odoo Online

Modulul nu conține Python: se poate importa pe Odoo Online (planul Custom) din Aplicații > Importați
modulul. Nu se poate instala împreună cu `terrabit_iap_anaf` (manifestul îl exclude, iar importul zip
este refuzat cât timp acel modul e instalat): amândouă primesc același token.

Dacă dezinstalați modulul, reporniți acțiunea programată de reînnoire a tokenului e-Factura
(*Setări > Tehnic > Automatizare > Acțiuni planificate*) sau generați un token cu butonul standard.
