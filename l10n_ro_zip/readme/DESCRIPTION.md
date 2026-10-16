Modul pentru gestionarea codurilor poștale din România.

Funcționalități principale:

- Adaugă modelul `res.zip` cu ~52.000 de înregistrări de coduri poștale românești,
  fiecare conținând: cod poștal, localitate, județ, tip stradă, nume stradă, sector (București), oficiu poștal.
- Datele sunt importate automat la instalare dintr-un fișier SQL și sunt corelate cu județele
  și localitățile din modulul `l10n_ro_city`.
- Extinde formularul partenerului (`res.partner`) cu câmpul `Cod Poștal (zip_id)`,
  filtrat după localitate, care completează automat câmpul standard `zip` la selecție.
- Căutarea codurilor poștale funcționează atât după codul numeric, cât și după numele străzii.
- Suportă sectoarele municipiului București (1–6) cu legătură directă la localitățile corespunzătoare.
