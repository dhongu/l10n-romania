Modul pentru gestionarea codurilor poștale din România.

Funcționalități principale:

- Adaugă modelul `res.zip` cu ~73.000 de înregistrări de coduri poștale românești,
  fiecare conținând: cod poștal, localitate, județ, tip stradă, nume stradă, sector (București), oficiu poștal.
- Nomenclatorul este actualizat după posta-romana.ro (noiembrie 2026) pentru toate cele 42 de județe:
  străzile celor 54 de orașe cu coduri pe stradă și oficiul poștal al fiecărei localități. Pentru 269 de orașe
  mici, la care Poșta are un singur cod, străzile vin din OpenStreetMap (ODbL).
- Datele sunt importate automat la instalare dintr-un fișier SQL. Fiecare cod e legat de județ după
  primele două cifre și, când modulul `l10n_ro_city` e instalat, de localitatea din nomenclatorul lui.
- Extinde formularul partenerului (`res.partner`) cu câmpul `Cod Poștal (zip_id)`,
  filtrat după localitate, care completează automat câmpul standard `zip` la selecție.
- Căutarea codurilor poștale funcționează atât după codul numeric, cât și după numele străzii.
- Suportă sectoarele municipiului București (1–6) cu legătură directă la localitățile corespunzătoare.
